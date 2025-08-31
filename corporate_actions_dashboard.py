import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="BSE Corporate Actions", layout="wide")

st.title("📊 BSE Corporate Action Dashboard")

@st.cache_data
def load_company_list():
    url = "https://www.bseindia.com/download/BhavCopy/Equity/EQ_ISINCODE.csv"
    df = pd.read_csv(url)
    df = df[["SC_CODE", "SC_NAME"]]
    df["SC_NAME"] = df["SC_NAME"].str.strip()
    return df

def fetch_announcements(scrip_code):
    url = f"https://www.bseindia.com/corporates/ann.aspx?scrip={scrip_code}&dur=A&expandable=0"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "ctl00_ContentPlaceHolder1_gvData"})
    
    announcements = []
    if table:
        rows = table.find_all("tr")[1:]  # skip header
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                date = cols[0].text.strip()
                description = cols[1].text.strip()
                attachment = cols[2].text.strip()
                announcements.append({
                    "Date": date,
                    "Description": description,
                    "Attachment": attachment
                })
    return announcements

# Load company list
company_df = load_company_list()

# Search box
search_term = st.text_input("🔎 Search company name").upper().strip()
if search_term:
    filtered_df = company_df[company_df["SC_NAME"].str.contains(search_term, case=False)]
else:
    filtered_df = company_df.head(20)  # show only first 20 if nothing typed

company_name = st.selectbox(
    "Select Company",
    filtered_df["SC_NAME"].tolist()
)

# Date range filter
time_filter = st.selectbox(
    "Select Time Period",
    ["All", "Last 1 Month", "Last 3 Months", "Last 6 Months", "Last 1 Year"]
)

if company_name:
    scrip_code = company_df.loc[company_df["SC_NAME"] == company_name, "SC_CODE"].values[0]
    
    announcements = fetch_announcements(scrip_code)
    
    if announcements:
        df = pd.DataFrame(announcements)
        
        # Convert Date column
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
        
        # Apply filter
        today = datetime.today()
        if time_filter == "Last 1 Month":
            cutoff = today - timedelta(days=30)
            df = df[df["Date"] >= cutoff]
        elif time_filter == "Last 3 Months":
            cutoff = today - timedelta(days=90)
            df = df[df["Date"] >= cutoff]
        elif time_filter == "Last 6 Months":
            cutoff = today - timedelta(days=180)
            df = df[df["Date"] >= cutoff]
        elif time_filter == "Last 1 Year":
            cutoff = today - timedelta(days=365)
            df = df[df["Date"] >= cutoff]
        
        # Show table
        st.dataframe(df, use_container_width=True)
        
        if not df.empty:
            # Download option
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Announcements as CSV",
                csv,
                f"{company_name}_corporate_actions.csv",
                "text/csv",
                key="download-csv"
            )
        else:
            st.warning("No announcements found in this period.")
    else:
        st.warning(f"No announcements found for {company_name}.")
