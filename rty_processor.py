import os
import shutil
import pandas as pd
import uuid
import tempfile
from io import BytesIO
import py7zr


def process_rty_7z(uploaded_file):

    # ==============================
    # Temp folder
    # ==============================
    temp_dir = os.path.join(
        tempfile.gettempdir(),
        f"rty_extract_{uuid.uuid4().hex}"
    )
    os.makedirs(temp_dir, exist_ok=True)

    # ==============================
    # Simpan upload ke temp
    # ==============================
    archive_path = os.path.join(temp_dir, uploaded_file.name)
    with open(archive_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    all_data = []
    all_top5_data = []
    monthly_detail_data = []


    try:
        # ==============================
        # Extract pakai py7zr (NO subprocess)
        # ==============================
        with py7zr.SevenZipFile(archive_path, mode='r') as z:
            z.extractall(path=temp_dir)

        # ==============================
        # Loop file excel
        # ==============================
        for root_dir, dirs, files in os.walk(temp_dir):
            for file in files:

                if file.endswith(".xlsx") and not file.endswith("Retest.xlsx"):

                    full_path = os.path.join(root_dir, file)

                    parts = full_path.split(os.sep)
                    filename = parts[-1]
                    station = parts[-2] if len(parts) >= 2 else ""
                    customer = parts[-3] if len(parts) >= 3 else ""

                    # ==============================
                    # QTY
                    # ==============================
                    df = pd.read_excel(
                        full_path,
                        sheet_name=3,
                        usecols="A:N",
                        skiprows=1,
                        nrows=5,
                        engine="openpyxl"
                    )

                    df.rename(columns={"Unnamed: 0": "QTY"}, inplace=True)
                    numeric_cols = df.columns[1:]

                    df[numeric_cols] = df[numeric_cols].apply(
                        lambda x: pd.to_numeric(x, errors="coerce")
                    )

                    result = (
                        df.loc[1, numeric_cols] /
                        df.loc[0, numeric_cols].replace(0, pd.NA)
                    ) * 100

                    df.loc[3, numeric_cols] = result.fillna(0).round(2)

                    df["Customer"] = customer
                    df["Station"] = station
                    df["Project"] = filename

                    all_data.append(df)

                    # ==============================
                    # FAIL MODE
                    # ==============================
                    df_fail = pd.read_excel(
                        full_path,
                        sheet_name=3,
                        usecols="A:N",
                        skiprows=7,
                        nrows=793,
                        engine="openpyxl"
                    )

                    df_fail.rename(columns={"FAIL MODE / LOC": "FailMode"}, inplace=True)
                    df_fail = df_fail[df_fail["FailMode"].notna()]

                    months = ["Jan","Feb","Mar","Apr","May","Jun",
                              "Jul","Aug","Sep","Oct","Nov","Dec"]

                    df_fail[months] = df_fail[months].apply(
                        lambda x: pd.to_numeric(x, errors="coerce")
                    ).fillna(0)

                    for month in months:

                        month_data = df_fail.sort_values(by=month, ascending=False)
                        valid_fail = month_data[month_data[month] > 0]

                        rows_added = 0

                        if len(valid_fail) > 0:
                            top5 = valid_fail.head(5)

                            for _, row_fail in top5.iterrows():
                                all_top5_data.append({
                                    "Month": month,
                                    "Top 5 Fail Mode": row_fail["FailMode"],
                                    "Count": int(row_fail[month]),
                                    "Customer": customer,
                                    "Station": station,
                                    "Project": filename
                                })
                                rows_added += 1

                            while rows_added < 5:
                                all_top5_data.append({
                                    "Month": month,
                                    "Top 5 Fail Mode": "Not Available",
                                    "Count": 0,
                                    "Customer": customer,
                                    "Station": station,
                                    "Project": filename
                                })
                                rows_added += 1
                        else:
                            for _ in range(5):
                                all_top5_data.append({
                                    "Month": month,
                                    "Top 5 Fail Mode": "No Fail Data",
                                    "Count": 0,
                                    "Customer": customer,
                                    "Station": station,
                                    "Project": filename
                                })

                    # ==============================
                    # MONTHLY DETAIL
                    # ==============================
                    monthly_detail_data = []
                    for month in months:
                        if month in df.columns:

                            qty_in = pd.to_numeric(df.loc[0, month], errors="coerce")
                            qty_pass = pd.to_numeric(df.loc[1, month], errors="coerce")
                            qty_fail = pd.to_numeric(df.loc[2, month], errors="coerce")

                            yield_value = 0
                            if pd.notna(qty_in) and qty_in != 0:
                                yield_value = round((qty_pass / qty_in) * 100, 2)
                            
                            monthly_detail_data.append({
                                "Customer": customer,
                                "Station": station,
                                "Month": month,
                                "Total_QTY_IN": qty_in if pd.notna(qty_in) else 0,
                                "Total_QTY_PASS": qty_pass if pd.notna(qty_pass) else 0,
                                "Total_QTY_FAIL": qty_fail if pd.notna(qty_fail) else 0,
                                "Yield": yield_value
                            })




        if not all_data:
            return None, None, None

        final_df = pd.concat(all_data, ignore_index=True)
        top5_df = pd.DataFrame(all_top5_data)
        monthly_df = pd.DataFrame(monthly_detail_data)

        monthly_df = (
            monthly_df
            .groupby(["Customer", "Station", "Month"], as_index=False)
            .agg({
                "Total_QTY_IN": "sum",
                "Total_QTY_PASS": "sum",
                "Total_QTY_FAIL": "sum"
            })
        )

        monthly_df["Yield"] = (
            monthly_df["Total_QTY_PASS"] / 
            monthly_df["Total_QTY_IN"].replace(0, pd.NA) 
        ) * 100

        monthly_df["Yield"] = monthly_df["Yield"].fillna(0).round(2)

        output_buffer = BytesIO()

        with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
            final_df.to_excel(writer, sheet_name="QTY", index=False)
            top5_df.to_excel(writer, sheet_name="Top5FailMode", index=False)
            monthly_df.to_excel(writer, sheet_name="MonthlyDetail", index=False)


        output_buffer.seek(0)

        return final_df, top5_df, output_buffer

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
