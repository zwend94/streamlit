import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Streamlit Setup
st.title("Healthcare Claims Data Simulator")
st.sidebar.header("Options")

# Payor Lists
gov_payors = ["Medicare", "Medicaid"]
private_payors = [
    "United Healthcare",
    "Aetna",
    "Cigna",
    "Humana",
    "Blue Cross Blue Shield",
    "Kaiser Permanente",
    "Centene",
    "Anthem",
    "Molina Healthcare",
    "WellCare"
]

def generate_fixed_claims_data(total_records=377000):
    start_date = datetime(2019, 1, 1)  # Updated start date
    end_date = datetime.now()

    # Generate claim dates uniformly distributed across the range
    claim_dates = np.random.choice(pd.date_range(start_date, end_date).to_numpy(), total_records)

    # Generate realistic patient ages
    ages = np.random.randint(1, 100, total_records)

    # Generate related dates
    service_start_dates = claim_dates - np.random.randint(0, 30, total_records).astype("timedelta64[D]")
    service_end_dates = service_start_dates + np.random.randint(1, 10, total_records).astype("timedelta64[D]")
    payment_dates = claim_dates + np.random.randint(1, 60, total_records).astype("timedelta64[D]")

    # Split data into two groups: 30% gov payors (Medicare/Medicaid), 70% private payors
    gov_count = int(total_records * 0.3)
    private_count = total_records - gov_count

    # Assign government payors
    gov_payor_names = np.random.choice(gov_payors, gov_count, p=[0.5, 0.5])  # 50% Medicare, 50% Medicaid
    # Assign fixed payor IDs for government payors
    gov_payor_ids = np.where(gov_payor_names == "Medicare", "0000000001", "0000000002")

    # Assign private payors
    private_payor_names = np.random.choice(private_payors, private_count)
    # Assign random 10-digit payor IDs for private payors
    private_payor_ids = [f"{pid:010d}" for pid in np.random.randint(0, 10**10, private_count)]

    # Concatenate government and private payors
    payor_names = np.concatenate([gov_payor_names, private_payor_names])
    payor_ids = np.concatenate([gov_payor_ids, private_payor_ids])

    # Shuffle the arrays to ensure a uniform distribution throughout the dataset
    idx = np.arange(total_records)
    np.random.shuffle(idx)

    payor_names = payor_names[idx]
    payor_ids = payor_ids[idx]
    claim_dates = claim_dates[idx]
    service_start_dates = service_start_dates[idx]
    service_end_dates = service_end_dates[idx]
    payment_dates = payment_dates[idx]
    ages = ages[idx]

    data = {
        "Claim ID": [f"C{np.random.randint(1000000, 9999999)}" for _ in range(total_records)],
        "Claim Date": claim_dates.astype(str),
        "Provider ID": [f"{pid:010d}" for pid in np.random.randint(0, 10**10, total_records)],
        "Facility ID": [f"{fid:010d}" for fid in np.random.randint(0, 10**10, total_records)],
        "Payor ID": payor_ids,
        "Payor Name": payor_names,
        "Patient ID": [f"{patid:010d}" for patid in np.random.randint(0, 10**10, total_records)],
        "Gender": np.random.choice(["Male", "Female"], total_records),
        "Age": ages,
        "ICD-10": [f"D{np.random.randint(100, 999)}" for _ in range(total_records)],
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
st.write("Generating dataset with ~377,000 records...")
df = generate_fixed_claims_data()

# Display Dataset and Filters
st.success(f"Data generated with {len(df)} records.")

# Date Range Slider
st.sidebar.header("Filters")
st.sidebar.write("**Date Range Filter**")
min_date = datetime(2019, 1, 1)
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
