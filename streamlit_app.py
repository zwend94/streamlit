import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from payor_dimension import generate_payor_dimension
from icd_dimension import generate_icd_dimension
from facility_dimension import generate_facility_dimension

st.title("Healthcare Claims Data Simulator with Dimension Tables")
st.sidebar.header("Options")

def generate_fixed_claims_data(total_records=377000):
    start_date = datetime(2019, 1, 1)
    end_date = datetime.now()

    claim_dates = np.random.choice(pd.date_range(start_date, end_date).to_numpy(), total_records)
    ages = np.random.randint(1, 100, total_records)

    service_start_dates = claim_dates - np.random.randint(0, 30, total_records).astype("timedelta64[D]")
    service_end_dates = service_start_dates + np.random.randint(1, 10, total_records).astype("timedelta64[D]")
    payment_dates = claim_dates + np.random.randint(1, 60, total_records).astype("timedelta64[D]")

    gov_count = int(total_records * 0.3)
    private_count = total_records - gov_count

    gov_payor_names = np.random.choice(["Medicare", "Medicaid"], gov_count, p=[0.5, 0.5])
    gov_payor_ids = np.where(gov_payor_names == "Medicare", "0000000001", "0000000002")

    private_payors_list = [
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
    private_payor_names = np.random.choice(private_payors_list, private_count)
    
    private_payor_ids = [f"{pid:010d}" for pid in np.random.randint(3, 10**10, private_count)]

    payor_names = np.concatenate([gov_payor_names, private_payor_names])
    payor_ids = np.concatenate([gov_payor_ids, private_payor_ids])

    idx = np.arange(total_records)
    np.random.shuffle(idx)

    payor_names = payor_names[idx]
    payor_ids = payor_ids[idx]
    claim_dates = claim_dates[idx]
    service_start_dates = service_start_dates[idx]
    service_end_dates = service_end_dates[idx]
    payment_dates = payment_dates[idx]
    ages = ages[idx]

    icd_code_count = 100  # number of unique ICD codes
    unique_icd_codes = [f"D{np.random.randint(100,999)}" for _ in range(icd_code_count)]
    unique_icd_codes = list(set(unique_icd_codes))  # ensure unique
    if len(unique_icd_codes) < icd_code_count:
        # If we didn't get enough unique codes, just pad with a known pattern
        needed = icd_code_count - len(unique_icd_codes)
        unique_icd_codes += [f"D{1000+i}" for i in range(needed)]

    icd_codes = np.random.choice(unique_icd_codes, total_records)

    facility_count = 500  # number of unique facilities
    unique_facility_ids = [f"{fid:010d}" for fid in np.random.randint(0, 10**10, facility_count)]
    facility_ids = np.random.choice(unique_facility_ids, total_records)

    data = {
        "Claim ID": [f"C{np.random.randint(1000000, 9999999)}" for _ in range(total_records)],
        "Claim Date": claim_dates.astype(str),
        "Provider ID": [f"{pid:010d}" for pid in np.random.randint(0, 10**10, total_records)],
        "Facility ID": facility_ids,
        "Payor ID": payor_ids,
        "Payor Name": payor_names,
        "Patient ID": [f"{patid:010d}" for patid in np.random.randint(0, 10**10, total_records)],
        "Gender": np.random.choice(["Male", "Female"], total_records),
        "Age": ages,
        "ICD-10": icd_codes,
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

    fact_df = pd.DataFrame(data)
    return fact_df, unique_icd_codes, unique_facility_ids, private_payors_list

st.write("Generating dataset with ~377,000 records...")
fact_df, unique_icd_codes, unique_facility_ids, private_payors_list = generate_fixed_claims_data()

payor_dim = generate_payor_dimension()

private_payor_rows = fact_df[~fact_df["Payor ID"].isin(["0000000001", "0000000002"])]
unique_private = private_payor_rows[["Payor ID", "Payor Name"]].drop_duplicates()

unique_private["Is Government"] = False

payor_dim = pd.concat([payor_dim, unique_private], ignore_index=True).drop_duplicates(subset=["Payor ID"])

icd_dim = generate_icd_dimension(unique_icd_codes)

facility_dim = generate_facility_dimension(unique_facility_ids)

st.success(f"Fact data generated with {len(fact_df)} records.")
st.write("Dimensions:")
st.write("Payor Dim:", payor_dim.head())
st.write("ICD-10 Dim:", icd_dim.head())
st.write("Facility Dim:", facility_dim.head())

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

filtered_df = fact_df[
    (pd.to_datetime(fact_df["Claim Date"]) >= pd.to_datetime(selected_dates[0])) &
    (pd.to_datetime(fact_df["Claim Date"]) <= pd.to_datetime(selected_dates[1]))
]

st.write(f"Filtered Records: {len(filtered_df)}")
st.dataframe(filtered_df.head(100))  # Display first 100 records

# Download buttons
st.download_button(
    label="Download Fact Dataset",
    data=fact_df.to_csv(index=False),
    file_name="fact_claims_data.csv",
    mime="text/csv"
)

st.download_button(
    label="Download Payor Dimension",
    data=payor_dim.to_csv(index=False),
    file_name="dim_payor.csv",
    mime="text/csv"
)

st.download_button(
    label="Download ICD-10 Dimension",
    data=icd_dim.to_csv(index=False),
    file_name="dim_icd10.csv",
    mime="text/csv"
)

st.download_button(
    label="Download Facility Dimension",
    data=facility_dim.to_csv(index=False),
    file_name="dim_facility.csv",
    mime="text/csv"
)
