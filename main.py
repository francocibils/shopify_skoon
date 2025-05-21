import pandas as pd
import streamlit as st

from io import BytesIO
from xlsxwriter import Workbook
from helper_functions import *

st.title('Shopify - Skoon')
st.header('File upload')
st.markdown('Upload file to obtain gifts, free-reships and coupons.')

raw = st.file_uploader('Upload Shopify file', type = ['xlsx', 'xls', 'csv'])

if raw is not None:
    file_type = get_file_type(raw)
    
    if file_type == 'csv':
        raw_df = pd.read_csv(raw)
    elif file_type == 'xlsx' or file_type == 'xls':
        raw_df = pd.read_excel(raw)
    
    st.success('Shopify file uploaded successfully.')

if st.button('Process file'):

    keep_cols = ['Total', 'Discount Code', 'Created at', 'Tags']
    df = raw_df[keep_cols]

    df['Tags_mapped'] = df['Tags'].apply(map_value)
    df['Date'] = pd.to_datetime(df['Created at']).dt.strftime('%Y-%m-%d')
    df['has_discount'] = df['Discount Code'].notna().astype(int)
    df = df.drop(['Created at'], axis = 1)

    # Gifts and free-reships
    df_1 = df.copy(deep = True)

    df_1 = df_1[(df_1['Total'] == 0) & (df_1['has_discount'] == 1)]
    df_1['discount_type'] = df_1['Discount Code'].fillna('').str.lower().apply(
        lambda x: 'Free-reships' if 'free' in x or 'reship' in x else 'Gifts'
    )
    pivot_df_1 = df_1.groupby(['Date', 'discount_type']).size().unstack(fill_value = 0)
    # pivot_df_1 = pivot_df_1[['Gifts', 'Free-reships']]

    # Coupons (sign-ups and one-offs)
    df_2 = df.copy(deep = True)

    df_2 = df_2[((df_2['Tags_mapped'] == 'PARENT') | (df_2['Tags_mapped'] == 'ONE OFFS')) & (df_2['has_discount'] == 1)]
    pivot_df_2 = df_2.groupby(['Date', 'Tags_mapped']).size().unstack(fill_value = 0)

    st.success('Shopify file has been processed successfully.')
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine = 'xlsxwriter') as writer:
        pivot_df_1.to_excel(writer, index = True, sheet_name = 'Gifts & Reships')
        pivot_df_2.to_excel(writer, index = True, sheet_name = 'Coupons')
        writer.close()

        # Rewind the buffer
        output.seek(0)

        # Create a download button
        st.download_button(
            label = "Download Excel file",
            data = output,
            file_name = "Shopify - Skoon.xlsx",
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
