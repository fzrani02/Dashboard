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

            # ===============
            # Filter Customer
            # ===============
            
            customers = st.multiselect(
                "Choose Customer",
                df_monthly["Customer"].unique()
            )
            
            if customers:

                # Filter data hanya YIELD
                df_filtered = df_monthly[
                    df_monthly["Customer"].isin(customers)
                ]

               
                
                month = st.selectbox(
                    "Choose Month",
                   df_monthly["Customer"].isin(customers)
                )

                # ===========
                # Pilih bulan
                # ===========

                month = st.selectbox(
                    "Choose Month",
                    df_monthly["Month"].unique()
                )

                df_filtered = df_filtered[df_filtered["Month] == month]

                
                # =========================
                # Select Metric
                # =========================
                metric = st.selectbox(
                    "Choose Metric",
                    ["Total_QTY_IN",
                     "Total_QTY_PASS",
                     "Total_QTY_FAIL",
                     "Yield"]
                )

                if not df_filtered.empty:
        
                    fig, ax = plt.subplots()
        
                    stations = df_filtered["Station"]
                    values = df_filtered[metric]
        
                    bars = ax.bar(stations, values)
        
                    # Label
                    for i in range(len(stations)):
                        ax.text(
                            i,
                            values.iloc[i],
                            round(values.iloc[i], 2),
                            ha='center',
                            va='bottom',
                            weight='bold'
                        )
        
                    ax.set_ylabel(metric)
        
                    if metric == "Yield":
                        ax.set_ylim(0, 100)
        
                    ax.set_title(f"{metric} - {month}")
                    ax.set_xticklabels(stations, rotation=45)
        
                    st.pyplot(fig)
        
                else:
                    st.warning("No data available for selected filter.")
        
            else:
                st.info("Please select at least one customer.")
                


                    
                            
                    






        







