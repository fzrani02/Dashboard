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
        df_qty, df_fail, excel_buffer = run_processing(uploaded_file)

    if df_qty is not None:

        st.success("Processing Completed")

        tab1, tab2 = st.tabs(["Data Overview", "Visualization"])

        with tab1:
            st.subheader("Quantity and Yield")
            AgGrid(df_qty)

            st.subheader("Top 5 Fail Mode")
            AgGrid(df_fail)

            st.download_button(
                "Download Integrated File",
                excel_buffer,
                file_name="Laporan_RTY_Final.xlsx"
            )

        with tab2:
            st.subheader("RTY Visualization")

            # Filter Customer
            customers = st.multiselect(
                "Choose Customer",
                df_qty["Customer"].unique()
            )
            
            if customers:

                # Filter data hanya YIELD
                df_filtered = df_qty[
                    (df_qty["Customer"].isin(customers)) &
                    (df_qty["QTY"] == "YIELD")
                ]
        
                # Pilih bulan
                month = st.selectbox(
                    "Choose Month",
                    ["Jan","Feb","Mar","Apr","May","Jun",
                     "Jul","Aug","Sep","Oct","Nov","Dec"]
                )
                # Buat pivot untuk stacked PASS/FAIL
                pivot = df_filtered.pivot_table(
                    index=["Station","Customer"],
                    values=month,
                    aggfunc="mean"
                ).reset_index()
        
                if not pivot.empty:
                    fig, ax = plt.subplots()

                    stations = pivot["Station"]
                    values = pivot[month]
        
                    # Warna berdasarkan customer
                    colors = []
                    for cust in pivot["Customer"]:
                        if cust == "ABB":
                            colors.append("red")
                        elif cust == "Life Fitness":
                            colors.append("blue")
                        else:
                            colors.append("gray")
                    bars = ax.bar(stations, values, color=colors)
                    

                    # Label angka di atas bar
                    for i in range(len(stations)):
                        ax.text(
                            i,
                            values.iloc[i] + 1,
                            round(values.iloc[i], 1),
                            ha='center',
                            weight='bold'
                        )
                        
                    ax.set_ylim(0, 100)
                    ax.set_ylabel("Yield (%)")
                    ax.set_title(f"RTY Performance - {month}")
                    ax.set_xticklabels(stations, rotation=45)
        
                    st.pyplot(fig)

                else:
                    st.warning("No data available for selected filter.")
            else:
                st.info("Please select at least one customer.")
                    


                    
                            
                    






        






