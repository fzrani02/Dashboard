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
            st.write("Visualization section (lanjut ke plot kamu)")
