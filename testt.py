from Test123 import check# Importing necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import base64
import openpyxl
st.title("Linkedin ScraPy")

# Allow the user to upload an Excel file
uploaded_file = st.file_uploader("Upload your Data Sheet here", type="xlsx")

if uploaded_file is not None:
    workbook = openpyxl.load_workbook(uploaded_file)
    sheet = workbook.active
    data = []
    header = []
    for row in sheet.iter_rows(values_only=True):
        if not header:
            header = row
        else:
            data.append(row)
    df = pd.DataFrame(data, columns=header)
    check(df)

    # Display the DataFrame
    #st.write(df)
    
