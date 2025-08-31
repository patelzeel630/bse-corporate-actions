import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# -------------------- Company List --------------------
COMPANIES = {
    "Reliance Industries": "500325",
    "State Bank of India": "500112",
    "Tata Consultancy Services": "532540",
    "Infosys": "500209",
    "HDFC Bank": "500180",
}

# -------------------- Scraper from BSE Announcements --------------------
def fetch_corporate_actions(company_code):
    url = f"https://www.bseindia.com/corporates/ann.aspx?ann_flag=C&SecurityCode={company_code}&curpg=1&ann=True"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            st.error(f"❌ Failed to fetch data (Status {response.status_code})")
            return pd.DataFrame()

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "ctl00_ContentPlaceHolder1_gvData"})

        if table is None:
            return pd.DataFrame()

        # Extract headers
        headers = [th.text.strip() for th in table.find_all("th")]

        # Extract rows
        rows = []
        for tr in table.find_all("tr")[1:]:
            cells = [td.text.strip() for td in tr.find_all("td")]
            if cells:
                rows.append(cells)

        df = pd.DataFrame(rows, columns=headers)
        return df

    except Exception as e:
        st.error(f"⚠️ Error fetching data: {e}")
        return pd.DataFrame()

# -------------------- Streamlit App --------------------
st.set_page_config(page_title="Corporate Actions Dashboard", layout="wide")
st.title("📊 Corporate Actions Viewer (BSE Live Data)")

# Select company
company_name = st.selectbox("🏢 Select a company:", list(COMPANIES.keys()))
company_code = COMPANIES[company_name]

# Fetch and display
df = fetch_corporate_actions(company_code)

if df.empty:
    st.warning("⚠️ No corporate actions found for this company.")
else:
    st.success(f"✅ Found {len(df)} corporate actions for {company_name}.")
    st.dataframe(df)

    # Filter by date if column present
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        min_date = df["Date"].min()
        max_date = df["Date"].max()

        start_date, end_date = st.date_input(
            "📅 Select date range:",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date,
        )

        mask = (df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))
        filtered_df = df.loc[mask]

        st.write("### 🔎 Filtered Corporate Actions")
        st.dataframe(filtered_df)

        # Download button
        st.download_button(
            "⬇️ Download Filtered Data (CSV)",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{company_name}_corporate_actions.csv",
            mime="text/csv"
        )
