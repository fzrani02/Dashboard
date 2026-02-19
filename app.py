import matplotlib.pyplot as plt
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

st.sidebar.caption("Require < 200MB and compressed .7z")

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
                file_name="Laporan_RTY_Final.xlsx"
            )

        with tab2:
            st.subheader("RTY Visualization")

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
                    ["Total_QTY_IN",
                     "Total_QTY_PASS",
                     "Total_QTY_FAIL",
                     "Yield"]
                )
        
                df_filtered = df_monthly[
                    (df_monthly["Customer"].isin(customers)) &
                    (df_monthly["Month"] == month)
                ]
               
                if not df_filtered.empty:
        
                    # ===========
                    # Warna Per Customer
                    # ===========
                    unique_customers = df_filtered["Customer"].unique()
                    colors = plt.cm.tab10(range(len(unique_customers)))
                    color_map = {
                        cust: colors[i]
                        for i, cust in enumerate(unique_customers)
                    }

                    fig, ax = plt.subplots(figsize=(10,6))

                    # ========
                    # Horizontal Bar Chart
                    # ========

                    for cust in unique_customers:
                        cust_data = df_filtered[df_filtered["Customer"] == cust]

                        ax.barh(
                            cust_data["Station"], 
                            cust_data[metric],
                            label=cust,
                            color=color_map[cust]
                        )

                        # Label nilai
                        for i, value in enumerate(cust_data[metric]):
                            ax.text(
                                value,
                                cust_data["Station"].iloc[i],
                                round(value, 2),
                                va='center', 
                                ha='left', 
                                fontweight='bold'
                            )

                        ax.set_xlabel(metric)
                        ax.set_ylabel("Station")
                        ax.set_title(f"{metric} - {month}")
            
                        if metric == "Yield":
                            ax.set_xlim(0, 200)
            
                        ax.legend(title="Customer")
            
                        st.pyplot(fig)
        
                else:
                    st.warning("No data available for selected filter.")
        
            else:
                st.info("Please select at least one customer.")
                


                    
                            
                    






        















