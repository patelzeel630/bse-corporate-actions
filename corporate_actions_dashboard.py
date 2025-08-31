import requests
import pandas as pd
import streamlit as st
from datetime import datetime

# ✅ Mapping: Company name -> BSE Scrip Code
COMPANIES = {
    "Cera Sanitaryware": "532443",    # CERA
    "Hindware Home Innovation": "543518", # Hindware
    "Kajaria Ceramics": "500233"     # Kajaria
}

def fetch_announcements(scrip_code, company_name):
    url = f"https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=-1&strPrevDate=&strScrip={scrip_code}&strSearch=&strToDate=&strType=C"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    data = r.json()

    announcements = []
    for item in data.get("Table", []):
        announcements.append({
            "Company": company_name,
            "Scrip Code": scrip_code,
            "Date": item.get("News_dt"),
            "Corporate Action": item.get("Newssub"),
            "Details": item.get("news_detl"),
            "PDF Link": "https://www.bseindia.com" + item.get("ATTACHMENTNAME", "")
        })
    return announcements

def main():
    st.set_page_config(page_title="BSE Corporate Actions", layout="wide")
    st.title("📊 Corporate Action Dashboard (BSE)")

    all_announcements = []
    for company, code in COMPANIES.items():
        try:
            all_announcements.extend(fetch_announcements(code, company))
        except Exception as e:
            st.error(f"Error fetching {company}: {e}")

    if not all_announcements:
        st.warning("No announcements found.")
        return

    df = pd.DataFrame(all_announcements)

    # Filters
    company_filter = st.multiselect("Select Companies", df["Company"].unique(), df["Company"].unique())
    filtered_df = df[df["Company"].isin(company_filter)]

    st.dataframe(filtered_df, use_container_width=True)

    # Download as Excel
    if st.button("Export to Excel"):
        filename = f"Corporate_Actions_{datetime.today().strftime('%Y%m%d')}.xlsx"
        filtered_df.to_excel(filename, index=False)
        st.success(f"✅ Exported to {filename}")

if __name__ == "__main__":
    main()
