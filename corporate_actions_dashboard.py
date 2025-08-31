import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="BSE Corporate Actions Dashboard", layout="wide")

# ✅ Load company list from CSV (root folder)
@st.cache_data
def load_company_list():
    return pd.read_csv("company_list.csv")   # file in root

# Try loading company list
try:
    company_df = load_company_list()
    st.sidebar.success("Company list loaded successfully!")
except Exception as e:
    st.sidebar.error(f"Error loading company list: {e}")
    st.stop()

# Sidebar: company selection
st.sidebar.header("Select Company")
company_names = company_df["NAME OF COMPANY"].unique()
selected_company = st.sidebar.selectbox("Choose a company", company_names)

# Find company code
company_code = company_df.loc[
    company_df["NAME OF COMPANY"] == selected_company, "SCRIP CODE"
].values[0]

st.write(f"### Selected Company: {selected_company} (Code: {company_code})")

# ✅ Fetch corporate actions from BSE (if available)
@st.cache_data
def get_corporate_actions(scrip_code):
    url = f"https://api.bseindia.com/BseIndiaAPI/api/CorporateAction/w?scripcode={scrip_code}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return pd.DataFrame(data.get("Table", []))
        else:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# Load actions
actions_df = get_corporate_actions(company_code)

# Show results
if not actions_df.empty:
    st.write("### Corporate Actions")
    st.dataframe(actions_df)
else:
    st.warning("No corporate actions found for this company.")
