
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import pandas as pd
import streamlit as st
from rty_processor import process_rty_7z
from st_aggrid import AgGrid

@st.cache_data(show_spinner=False)
def run_processing(uploaded_file):
    return process_rty_7z(uploaded_file)


st.set_page_config(layout="wide")

st.sidebar.header("Input Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload .7z file",
    type=["7z"]
)

st.sidebar.caption("Format: Folder > Customer > Station > Excel files")
st.sidebar.caption("Example: RTY > ABB > FCT > AB_010.xlsx")

if uploaded_file:

    with st.spinner("Processing file..."):
        df_qty, df_fail, df_monthly, excel_buffer = run_processing(uploaded_file)

    if df_qty is not None:

        st.success("Processing Completed")

        tab1, tab2 = st.tabs(["Data Overview", "Visualization"])

        with tab1:
            st.subheader("Quantity and Yield")
            AgGrid(df_qty)

            st.subheader("Top 5 Fail Mode")
            AgGrid(df_fail)

            st.subheader("Monthly Detail")
            AgGrid(df_monthly)


            st.download_button(
                "Download Integrated File",
                excel_buffer,
                file_name="Report_Final.xlsx"
            )

        with tab2:
            st.subheader("Quantity and Yield")

            # ==========================
            # Urutan Bulan Fix
            # ==========================
            month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                           "Jul","Aug","Sep","Oct","Nov","Dec"]
        
            available_months = [m for m in month_order if m in df_monthly["Month"].unique()]

            # ===============
            # Filter Customer
            # ===============
            
            customers = st.multiselect(
                "Choose Customer",
                (df_monthly["Customer"].unique())
            )
            
            if customers:
                
                month = st.selectbox(
                    "Choose Month",
                    available_months
                )
        
                metric = st.selectbox(
                    "Choose Metric",
                    ["TOTAL QTY",
                     "TOTAL YIELD (%)"]
                )
        
                df_filtered = df_monthly[
                    (df_monthly["Customer"].isin(customers)) &
                    (df_monthly["Month"] == month)
                ]
               
                if not df_filtered.empty:

                    fig, ax = plt.subplots(figsize=(14, 6))
                    df_filtered = df_filtered.copy()
                    df_filtered["Station_Label"] = (
                        df_filtered["Customer"] + " | " + df_filtered["Station"]
                    )

                    if metric == "TOTAL QTY":

                        pass_values = df_filtered["TOTAL QTY PASS"]
                        fail_values = df_filtered["TOTAL QTY FAIL"]
                        total_values = pass_values + fail_values

                        unique_customers = df_filtered["Customer"].unique()
                        colors = plt.cm.tab10(range(len(unique_customers)))
                        color_map = {
                            cust: colors[i]
                            for i, cust in enumerate(unique_customers)
                        }

                        pass_colors = df_filtered["Customer"].map(color_map)

                        ax.bar(
                            df_filtered["Station_Label"],
                            pass_values,
                            color=pass_colors,
                            label="PASS"
                        )

                        ax.bar(
                            df_filtered["Station_Label"],
                            fail_values,
                            bottom=pass_values,
                            color="black",
                            label="FAIL"
                        )

                        for i in range(len(df_filtered)):

                            if pass_values.iloc[i] > 0:
                
                                ax.text(
                                    i,
                                    pass_values.iloc[i] / 2,
                                    int(pass_values.iloc[i]),
                                    ha='center',
                                    va='center',
                                    fontsize=8,
                                    color='white'
                                )

                            if fail_values.iloc[i] > 0:

                                ax.text(
                                    i,
                                    pass_values.iloc[i] + fail_values.iloc[i] / 2,
                                    int(fail_values.iloc[i]),
                                    ha='center',
                                    va='center',
                                    fontsize=8,
                                    color='white'
                                )

                            ax.text(
                                i,
                                total_values.iloc[i],
                                int(total_values.iloc[i]),
                                ha='center',
                                va='bottom',
                                fontsize=9,
                                fontweight='bold'
                            )
                            
                        legend_elements = [
                             Patch(facecolor=color_map[cust], label=cust)
                                for cust in unique_customers
                            ]
                             
                        legend_elements.append(
                            Patch(facecolor="black", label="FAIL")
                        )

                        ax.legend(handles=legend_elements, title="Customer / Fail")

                        ax.set_ylabel("Quantity")
                        ax.set_title(f"Total Quantity (QTY Pass + QTY Fail) per Station - {month}")
                        ax.set_ylim(0, total_values.max() * 1.20)

                    else:

                        unique_customers = df_filtered["Customer"].unique()
                        colors = plt.cm.tab10(range(len(unique_customers)))
                        color_map = {
                            cust: colors[i]
                            for i, cust in enumerate(unique_customers)
                        }

                        bar_colors = df_filtered["Customer"].map(color_map)

                        ax.bar(
                            df_filtered["Station_Label"],
                            df_filtered["TOTAL YIELD (%)"],
                            color=bar_colors
                        )

                        for i, value in enumerate(df_filtered["TOTAL YIELD (%)"]):
                            ax.text(
                                i,
                                value,
                                round(value, 2),
                                ha='center',
                                va='bottom',
                                fontsize=8
                            )

                        legend_elements = [
                            Patch(facecolor=color_map[cust], label=cust)
                            for cust in unique_customers
                        ]

                        ax.legend(handles=legend_elements, title="Customer")
                        ax.set_ylabel("Total Yield (%)")
                        ax.set_title(f"Total Yield (%) per Station - {month}")
                        ax.set_ylim(0, 105)

                    ax.set_xlabel("STATION")
                    ax.set_xticklabels(
                        df_filtered["Station_Label"],
                        rotation=90,
                        fontsize=7
                    )

                    plt.tight_layout()
                    st.pyplot(fig)

                else:
                    st.warning("No data available for the selected filters.")
        
            else:
                st.info("Please select at least one customer.")



