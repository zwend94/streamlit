import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Streamlit Setup
st.title("Healthcare Claims Data Simulator")
st.sidebar.header("Options")

# Function to Generate 762,542 Healthcare Claims Records
def generate_fixed_claims_data(total_records=762542):
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
        "ICD-10": [f"D{np.random.randint(100, 999)}" for _ in range(total_records)],  # Renamed header
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

# Generate Fixed Dataset
st.write("Generating dataset with 762,542 records...")
df = generate_fixed_claims_data()

# Display Dataset and Filters
st.success(f"Data generated with {len(df)} records.")

# Date Range Slider
st.sidebar.header("Filters")
st.sidebar.write("**Date Range Filter**")
min_date = datetime(2014, 1, 1)
max_date = datetime.now()
selected_dates = st.sidebar.slider(
    "Select Claim Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# Apply Date Range Filter
filtered_df = df[
    (pd.to_datetime(df["Claim Date"]) >= pd.to_datetime(selected_dates[0])) &
    (pd.to_datetime(df["Claim Date"]) <= pd.to_datetime(selected_dates[1]))
]

# Display Filtered Results
st.write(f"Filtered Records: {len(filtered_df)}")
st.dataframe(filtered_df.head(100))  # Display first 100 records for performance reasons

# Download Option
st.download_button(
    label="Download Filtered Dataset",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_healthcare_claims_data.csv",
    mime="text/csv"
)
