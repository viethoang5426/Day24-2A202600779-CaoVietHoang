# src/api/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os
from src.access.rbac import get_current_user, require_permission
from src.pii.anonymizer import MedVietAnonymizer

app = FastAPI(title="MedViet Data API", version="1.0.0")
anonymizer = MedVietAnonymizer()

# Resolve data path
_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_raw_data_path = os.path.join(_base_dir, "data", "raw", "patients_raw.csv")

# --- ENDPOINT 1 ---
@app.get("/api/patients/raw")
@require_permission(resource="patient_data", action="read")
async def get_raw_patients(
    current_user: dict = Depends(get_current_user)
):
    """
    Trả về raw patient data (chỉ admin được phép).
    Load từ data/raw/patients_raw.csv
    Trả về 10 records đầu tiên dưới dạng JSON.
    """
    df = pd.read_csv(_raw_data_path)
    records = df.head(10).to_dict(orient="records")
    return {"data": records, "total": len(df), "showing": 10}

# --- ENDPOINT 2 ---
@app.get("/api/patients/anonymized")
@require_permission(resource="training_data", action="read")
async def get_anonymized_patients(
    current_user: dict = Depends(get_current_user)
):
    """
    Trả về anonymized data (ml_engineer và admin được phép).
    Load raw data → anonymize → trả về JSON.
    """
    df = pd.read_csv(_raw_data_path)
    df_anon = anonymizer.anonymize_dataframe(df.head(10))
    records = df_anon.to_dict(orient="records")
    return {"data": records, "total": len(df), "showing": 10}

# --- ENDPOINT 3 ---
@app.get("/api/metrics/aggregated")
@require_permission(resource="aggregated_metrics", action="read")
async def get_aggregated_metrics(
    current_user: dict = Depends(get_current_user)
):
    """
    Trả về aggregated metrics (data_analyst, ml_engineer, admin).
    Ví dụ: số bệnh nhân theo từng loại bệnh (không có PII).
    """
    df = pd.read_csv(_raw_data_path)
    metrics = df.groupby("benh").agg(
        so_benh_nhan=("patient_id", "count"),
        ket_qua_tb=("ket_qua_xet_nghiem", "mean")
    ).reset_index()
    metrics["ket_qua_tb"] = metrics["ket_qua_tb"].round(2)
    return {
        "metrics": metrics.to_dict(orient="records"),
        "total_patients": len(df)
    }

# --- ENDPOINT 4 ---
@app.delete("/api/patients/{patient_id}")
@require_permission(resource="patient_data", action="delete")
async def delete_patient(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Chỉ admin được xóa. Các role khác nhận 403.
    """
    return {
        "message": f"Patient {patient_id} has been deleted",
        "deleted_by": current_user["username"]
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "MedViet Data API"}
