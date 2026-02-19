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

                    # ==========================
                    # Hitung jumlah bar
                    # ==========================
                    total_bars = len(df_filtered)
                    
                    # Tinggi dinamis (0.6 per bar, minimum 6)
                    fig_height = max(6, total_bars * 0.6)
                    
                    fig, ax = plt.subplots(figsize=(12, fig_height))

                    # ==========================
                    # Buat label unik Customer | Station
                    # ==========================
                    df_filtered = df_filtered.copy()
                    df_filtered["Station_Label"] = (
                        df_filtered["Customer"] + " | " + df_filtered["Station"]
                    )
                    
                    # Warna per bar berdasarkan customer
                    bar_colors = df_filtered["Customer"].map(color_map)
                    
                    # Plot horizontal bar (sekali saja, bukan loop)
                    bars = ax.bar(
                        df_filtered["Station_Label"],
                        df_filtered[metric],
                        color=bar_colors
                    )

                    
                    # Label angka
                    for i, value in enumerate(df_filtered[metric]):
                        ax.text(
                            i,
                            value,
                            round(value, 2),
                            ha='center',
                            va='bottom',
                            fontsize=8
                        )

                    
                    # Legend manual
                   

                    ax.set_xlabel(metric)
              
                    ax.set_title(f"{metric} - {month}")

                    ax.set_xticklabels(
                        df_filtered["Station_Label"],
                        rotation=45,
                        ha="right"
                    )

                    
                    # Tambah padding kanan supaya label tidak kepotong
                    x_max = df_filtered[metric].max()
                    
                    if metric == "Yield":
                        ax.set_ylim(0, 105)
                    else:
                        ax.set_ylim(0, x_max * 1.15)

                    
                    ax.legend(title="Customer")
                    legend_elements = [
                        Patch(facecolor=color_map[cust], label=cust)
                        for cust in unique_customers
                        ]
                
                    ax.legend(
                        handles=legend_elements,
                        title="Customer"
                        )

                    plt.tight_layout()
                    st.pyplot(fig)
            else:
                st.info("Please select at least one customer.")
                


                    
                            
                    






        























