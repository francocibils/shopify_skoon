import pandas as pd

def map_value(val):
    if pd.isna(val):
        return 'ONE OFFS'
    val = val.lower()
    if 'recurring' in val:
        return 'REFILL'
    elif 'first' in val:
        return 'PARENT'
    else:
        return 'ONE OFFS' 
    
def get_file_type(file):
    
    if file.name.endswith(".csv"):
        return "csv"
    elif file.name.endswith(".xlsx"):
        return "xlsx"
    elif file.name.endswith(".xls"):
        return 'xls'