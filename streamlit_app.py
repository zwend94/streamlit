import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Streamlit Setup
st.title("Healthcare Claims Data Simulator")
st.sidebar.header("Options")

# Function to Generate Synthetic Healthcare Claims Data
def generate_large_claims_data(total_records):
    start_date = datetime(2014, 1, 1)
    end_date = datetime.now()

    # Generate claim dates uniformly distributed across the range
    claim_dates = np.random.choice(
        pd.date_range(start_date, end_date).to_numpy(), 
        total_records
    )

    # Generate realistic patient ages
    ages = np.random.randint(1, 100, total_records)

    # Generate related dates
    service_start_dates = claim_dates - np.random.randint(0, 30, total_records).astype("timedelta64[D]")
    service_end_dates = service_start_dates + np.random.randint(1, 10, total_records).astype("timedelta64[D]")
    payment_dates = claim_dates + np.random.randint(1, 60, total_records).astype("timedelta64[D]")

    # Generate other fields
    data = {
        "Claim ID": [f"C{np.random.randint(1000000, 9999999)}" for _ in range(total_records)],
        "Claim Date": claim_dates.astype(str),
        "Provider ID": np.random.randint(1000, 9999, total_records),
        "Facility ID": np.random.randint(2000, 9999, total_records),
        "Payor ID": np.random.randint(3000, 9999, total_records),
        "Patient ID": np.random.randint(4000, 9999, total_records),
        "Gender": np.random.choice(["Male", "Female"], total_records),
        "Age": ages,
        "Diagnosis Code": [f"D{np.random.randint(100, 999)}" for _ in range(total_records)],
        "Procedure Code": [f"P{np.random.randint(1000, 9999)}" for _ in range(total_records)],
        "Amount Billed": np.round(np.random.uniform(100, 5000, total_records), 2),
        "Amount Paid": np.round(np.random.uniform(0, 5000, total_records), 2),
        "Claim Status": np.random.choice(["Paid", "Denied", "Pending"], total_records, p=[0.7, 0.2, 0.1]),
        "Service Date Start": service_start_dates.astype(str),
        "Service Date End": service_end_dates.astype(str),
        "Payment Date": payment_dates.astype(str),
        "Adjustments": np.round(np.random.uniform(0, 500, total_records), 2),
        "Deductibles": np.round(np.random.uniform(0, 500, total_records), 2),
        "Co-pays": np.round(np.random.uniform(0, 500, total_records), 2),
    }

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

