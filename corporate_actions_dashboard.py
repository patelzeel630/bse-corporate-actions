import streamlit as st
import pandas as pd
import requests

# -------------------- Company List --------------------
# You can extend this dictionary with more companies
COMPANIES = {
    "Reliance Industries": "500325",
    "State Bank of India": "500112",
    "Tata Consultancy Services": "532540",
    "Infosys": "500209",
    "HDFC Bank": "500180",
}

# -------------------- Fetch corporate actions from BSE --------------------
def fetch_corporate_actions(company_code):
    """
    Fetches corporate actions for a given company from BSE.
    """
    url = f"https://api.bseindia.com/BseIndiaAPI/api/CorporateAction/w?Debtflag=&strSearch={company_code}&strType=C"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            data = response.json()
            if "Table" in data and len(data["Table"]) > 0:
                df = pd.DataFrame(data["Table"])
                return df
            else:
                return pd.DataFrame()
        else:
            st.error(f"❌ Failed to fetch data from BSE (Status {response.status_code})")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Error fetching data: {e}")
        return pd.DataFrame()

# -------------------- Streamlit App --------------------
st.set_page_config(page_title="Corporate Actions Dashboard", layout="wide")
st.title("📊 Corporate Actions Viewer (BSE Live Data)")

# Select company from dropdown
company_name = st.selectbox("🏢 Select a company:", list(COMPANIES.keys()))
company_code = COMPANIES[company_name]

# Fetch data
df = fetch_corporate_actions(company_code)

if df.empty:
    st.warning("⚠️ No corporate actions found for this company.")
else:
    st.success(f"✅ Found {len(df)} corporate actions for {company_name}.")
    st.dataframe(df)

    # If EX DATE exists, allow date filtering
    if "Ex Date" in df.columns:
        df["Ex Date"] = pd.to_datetime(df["Ex Date"], errors="coerce")
        min_date = df["Ex Date"].min()
        max_date = df["Ex Date"].max()

        start_date, end_date = st.date_input(
            "📅 Select date range:",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date,
        )

        mask = (df["Ex Date"] >= pd.to_datetime(start_date)) & (df["Ex Date"] <= pd.to_datetime(end_date))
        filtered_df = df.loc[mask]

        st.write("### 🔎 Filtered Corporate Actions")
        st.dataframe(filtered_df)
    else:
        st.warning("⚠️ 'Ex Date' column not found in BSE data.")
