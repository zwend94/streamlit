import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# Streamlit Setup
st.title("Healthcare Claims Data Simulator")
st.sidebar.header("Options")

# Function to Generate Synthetic Healthcare Claims Data
def generate_large_claims_data(total_records):
    start_date = datetime(2014, 1, 1)
    end_date = datetime.now()
    data = []

    for _ in range(total_records):
        claim_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        service_start_date = claim_date - timedelta(days=random.randint(0, 30))
        service_end_date = service_start_date + timedelta(days=random.randint(1, 10))
        payment_date = claim_date + timedelta(days=random.randint(1, 60))
        
        record = {
            "Claim ID": f"C{random.randint(1000000, 9999999)}",
            "Claim Date": claim_date.strftime("%Y-%m-%d"),
            "Provider ID": random.randint(1000, 9999),
            "Facility ID": random.randint(2000, 9999),
            "Payor ID": random.randint(3000, 9999),
            "Patient ID": random.randint(4000, 9999),
            "Gender": random.choice(["Male", "Female"]),
            "Age": random.randint(1, 99),
            "Diagnosis Code": f"D{random.randint(100, 999)}",
            "Procedure Code": f"P{random.randint(1000, 9999)}",
            "Amount Billed": round(random.uniform(100, 5000), 2),
            "Amount Paid": round(random.uniform(0, 5000), 2),
            "Claim Status": random.choice(["Paid", "Denied", "Pending"]),
            "Service Date Start": service_start_date.strftime("%Y-%m-%d"),
            "Service Date End": service_end_date.strftime("%Y-%m-%d"),
            "Payment Date": payment_date.strftime("%Y-%m-%d"),
            "Adjustments": round(random.uniform(0, 500), 2),
            "Deductibles": round(random.uniform(0, 500), 2),
            "Co-pays": round(random.uniform(0, 500), 2),
        }
        data.append(record)
    
    return pd.DataFrame(data)

# Options in the Sidebar
st.sidebar.write("**Dataset Options**")
generate_data = st.sidebar.checkbox("Generate Dataset", value=False)
records_to_generate = st.sidebar.slider("Number of Records to Generate", 1000, 1252249, 10000, step=1000)

# Generate or Load Data
if generate_data:
    with st.spinner(f"Generating {records_to_generate} records..."):
        df = generate_large_claims_data(records_to_generate)
    st.success("Data generation complete!")
    st.write(f"Generated {records_to_generate} records:")
    st.dataframe(df.head(100))  # Display first 100 records for performance reasons
    st.download_button(
        label="Download Full Dataset",
        data=df.to_csv(index=False),
        file_name="healthcare_claims_data.csv",
        mime="text/csv"
    )
else:
    st.write("Select 'Generate Dataset' from the sidebar to create the data.")

# Show Records Based on Filters
st.sidebar.header("Filters")
if 'df' in locals():
    claim_status_filter = st.sidebar.selectbox("Claim Status", ["All", "Paid", "Denied", "Pending"])
    provider_id_filter = st.sidebar.text_input("Provider ID (Exact Match)")
    date_range_filter = st.sidebar.date_input("Claim Date Range", [])

    filtered_df = df
    if claim_status_filter != "All":
        filtered_df = filtered_df[filtered_df["Claim Status"] == claim_status_filter]
    if provider_id_filter:
        filtered_df = filtered_df[filtered_df["Provider ID"] == int(provider_id_filter)]
    if len(date_range_filter) == 2:
        start_date, end_date = date_range_filter
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df["Claim Date"]) >= pd.to_datetime(start_date)) &
            (pd.to_datetime(filtered_df["Claim Date"]) <= pd.to_datetime(end_date))
        ]
    st.write(f"Filtered Records: {len(filtered_df)}")
    st.dataframe(filtered_df.head(100))  # Display first 100 filtered records

