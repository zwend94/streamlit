import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from fastapi import FastAPI
from pydantic import BaseModel

# Streamlit Setup
st.title("Healthcare Claims Data Simulator")
st.sidebar.header("Options")

# Generate Synthetic Claims Data
def generate_claims_data(num_records):
    data = []
    for _ in range(num_records):
        claim_date = datetime.now() - timedelta(days=random.randint(0, 365))
        service_start_date = claim_date - timedelta(days=random.randint(0, 30))
        service_end_date = service_start_date + timedelta(days=random.randint(0, 10))
        payment_date = claim_date + timedelta(days=random.randint(1, 60))
        
        record = {
            "Claim ID": f"C{random.randint(100000, 999999)}",
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

# Input Options
mode = st.sidebar.selectbox("Mode", ["Upload Data", "Generate Data"])
if mode == "Upload Data":
    uploaded_file = st.file_uploader("Upload Claims Data File (CSV/JSON)", type=["csv", "json"])
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_json(uploaded_file)
        st.write("Uploaded Data Preview:")
        st.dataframe(df)
else:
    num_records = st.sidebar.slider("Number of Records to Generate", 10, 500, 50)
    df = generate_claims_data(num_records)
    st.write("Generated Data Preview:")
    st.dataframe(df)

# API Simulation
st.sidebar.header("API Simulation")
api_enabled = st.sidebar.checkbox("Enable API")

if api_enabled:
    st.write("Simulated API Endpoint: `/get_claims_data`")

    # Mock API using FastAPI
    app = FastAPI()

    class ClaimRequest(BaseModel):
        filters: dict = None

    @app.get("/get_claims_data")
    async def get_claims_data(filters: dict = None):
        # Apply filters to the claims data
        filtered_df = df
        if filters:
            for column, value in filters.items():
                if column in df.columns:
                    filtered_df = filtered_df[filtered_df[column] == value]
        return filtered_df.to_dict(orient="records")
