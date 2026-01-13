import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config('Data Cleaning', page_icon='🧙‍♂️',layout='wide')
st.title('🧹 Cleaning Your Data')
st.write('📁 Upload A ***CSV*** or an ***Excel*** File To be clean!')

# for uploading file
uploaded_file= st.file_uploader("Upload A CSV Or An Excel File",type=(['csv','xlsx']))

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)

        
        # converting bool columns as str
        bool_cols = data.select_dtypes(include = ['bool']).columns
        data[bool_cols] = data[bool_cols].astype('str')
    except Exception as e:
        st.error("Could Not Read Excel / CSV File. Please Check File Format ")
        st.exception(e)
        st.stop()

    st.success('✨ File Uploaded Sucessfully !')
    st.write('### Preview Of Data')
    st.dataframe(data.head())

    # To Get Data Info

    buffer = io.StringIO()
    data.info(buf=buffer)
    info_str = buffer.getvalue()

    st.text(' ### 🗒 DataFrame Info:')
    st.text(info_str)

    st.write('### 📊 Data Overview')
    st.write('Number Of Rows ',data.shape[0])
    st.write('Number Of Columns ',data.shape[1])
    st.write('Number Of Missing Values ',data.isnull().sum().sum())
    st.write('Number Of Duplicates Records ',data.duplicated().sum())

# Duplicate value Handling

    st.title("Duplicate Data Checker")

    duplicate_rows = data[data.duplicated()]
    dup_count = duplicate_rows.shape[0]

    st.subheader("Duplicate Check")

    if dup_count == 0:
        st.success("No duplicate rows found 🎉")
    else:
        st.warning(f"Found {dup_count} duplicate rows")

        with st.expander("Preview duplicate rows"):
            st.dataframe(duplicate_rows)

        keep_option = st.radio(
            "When removing duplicates, keep:",
            options=["first", "last"]
        )

        if st.button("Remove Duplicates"):
            df_cleaned = data.drop_duplicates(keep=keep_option)

            st.success("Duplicates removed successfully!")

# Missing value Handling

    missing_cols = data.columns[data.isnull().any()].tolist()

    if not missing_cols:
        st.success("No missing values found 🎉")
    else:
        st.warning("Missing values detected!")
        st.write(data[missing_cols].isnull().sum())

        method = st.selectbox(
            "Choose a method",
            ["Default Value", "Mean", "Median", "Mode", "Custom Value"]
        )

        # ✅ STEP 1: Collect custom values FIRST
        custom_values = {}

        if method == "Custom Value":
            st.subheader("Enter custom values for missing columns")

            for col in missing_cols:
                default_val = "Unknown" if data[col].dtype == "object" else 0
                custom_values[col] = st.text_input(
                    f"Value for '{col}'",
                    value=str(default_val)
                )

        # ✅ STEP 2: Apply only when button is clicked
        if st.button("Apply"):
            for col in missing_cols:
                if method == "Default Value":
                    if data[col].dtype == "object":
                        data[col].fillna("Unknown", inplace=True)
                    else:
                        data[col].fillna(0, inplace=True)

                elif method == "Mean" and data[col].dtype != "object":
                    data[col].fillna(data[col].mean(), inplace=True)

                elif method == "Median" and data[col].dtype != "object":
                    data[col].fillna(data[col].median(), inplace=True)

                elif method == "Mode":
                    data[col].fillna(data[col].mode()[0], inplace=True)

                elif method == "Custom Value":
                    value = custom_values[col]

                    # Convert numeric columns safely
                    if data[col].dtype != "object":
                        value = float(value)

                    data[col].fillna(value, inplace=True)

            st.success("Missing values filled!")
            st.subheader("Updated Dataset")
            st.dataframe(data)


    # Download Cleaned Data File 
    st.subheader("⬇ Download Cleaned Dataset")

    csv = data.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="cleaned_data.csv",
        mime="text/csv"
    )