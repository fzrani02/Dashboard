import streamlit as st
from rty_processor import process_rty_7z

@st.cache_data(show_spinner=False)
def run_processing(uploaded_file):
    return process_rty_7z(uploaded_file)


st.set_page_config(layout="wide")

st.sidebar.header("Input Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload .7z file",
    type=["7z"]
)

st.sidebar.caption("Require < 200MB and compressed .7z")

if uploaded_file:

    with st.spinner("Processing file..."):
        df_qty, df_fail, excel_buffer = run_processing(uploaded_file)

    if df_qty is not None:

        st.success("Processing Completed")

        tab1, tab2 = st.tabs(["Data Overview", "Visualization"])

        with tab1:
            st.subheader("Sheet 1 - QTY")
            st.dataframe(df_qty)

            st.subheader("Sheet 2 - Top5FailMode")
            st.dataframe(df_fail)

            st.download_button(
                "Download Integrated File",
                excel_buffer,
                file_name="Laporan_RTY_Final.xlsx"
            )

        with tab2: 
            st.subheader("Choose Month")
            month = st.selectbox("Choose Month", 
                     ["Jan","Feb","Mar","Apr","May","Jun",
                      "Jul","Aug","Sep","Oct","Nov","Dec"])
            fig, ax = plt.subplots()

            stations = pivot.index
            pass_vals = pivot["PASS"]
            fail_vals = pivot["FAIL"]

            # warna PASS tergantung customer
            colors_pass = []
            for cust in pivot["Customer"]:
                if cust == "ABB":
                    colors_pass.append("red")
                elif cust == "Life Fitness":
                    colors_pass.append("blue")
                else:
                    colors_pass.append("gray")

            ax.bar(stations, pass_vals, color=colors_pass, label="PASS")
            ax.bar(stations, fail_vals, bottom=pass_vals, color="black", label="FAIL")

            for i in range(len(stations)):
                total = pass_vals[i] + fail_vals[i]
                ax.text(i, total + 3, int(total), ha='center', weight='bold')

            for bar in ax.patches:
                height = bar.get_height()
                if height > 0:
                    ax.text(
                        bar.get_x() + bar.get_width()/2,
                        bar.get_y() + height/2,
                        int(height),
                        ha='center',
                        color='white',
                        weight='bold',
                        size=8
                    )
            customers = st.multiselect(
                "Choose Customer",
                df_qty["Customer"].unique()
            )
            df_filtered = df_qty[
                (df_qty["Customer"].isin(customers)) &
                (df_qty["QTY"] == "YIELD")
            ]
            fig, ax = plt.subplots()

            for cust in customers:
                df_cust = df_filtered[df_filtered["Customer"] == cust]
                ax.bar(
                    df_cust["Station"],
                    df_cust[month],
                    label=cust
                )

            ax.set_ylim(0,100)
            ax.set_ylabel("Yield (%)")
            ax.legend()

            st.set_page_config(
                page_title="RTY Dashboard",
                layout="wide"
            )

            st.session_state["df_qty"] = df_qty
            st.session_state["df_fail"] = df_fail

            st.markdown("## 📈 RTY Performance Dashboard")

