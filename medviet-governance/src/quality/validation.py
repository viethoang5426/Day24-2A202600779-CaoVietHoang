# src/quality/validation.py
import pandas as pd
import re

def build_patient_expectation_suite():
    """
    Tạo expectation suite cho anonymized patient data.
    Dùng validation thủ công thay cho Great Expectations (tương thích Python 3.9).
    """
    df = pd.read_csv("data/raw/patients_raw.csv")
    
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    # 1. patient_id không được null
    if df["patient_id"].isnull().any():
        results["success"] = False
        results["failed_checks"].append("patient_id contains null values")

    # 2. cccd phải có đúng 12 ký tự
    if not (df["cccd"].astype(str).str.len() == 12).all():
        results["success"] = False
        results["failed_checks"].append("cccd must be exactly 12 characters")

    # 3. ket_qua_xet_nghiem phải trong khoảng [0, 50]
    if not df["ket_qua_xet_nghiem"].between(0, 50).all():
        results["success"] = False
        results["failed_checks"].append("ket_qua_xet_nghiem out of range [0, 50]")

    # 4. benh phải thuộc danh sách hợp lệ
    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
    if not df["benh"].isin(valid_conditions).all():
        results["success"] = False
        results["failed_checks"].append("benh contains invalid values")

    # 5. email phải match regex pattern
    email_regex = r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
    if not df["email"].apply(lambda x: bool(re.match(email_regex, str(x)))).all():
        results["success"] = False
        results["failed_checks"].append("email format invalid")

    # 6. Không được có duplicate patient_id
    if df["patient_id"].duplicated().any():
        results["success"] = False
        results["failed_checks"].append("duplicate patient_id found")

    return results


def validate_anonymized_data(filepath: str) -> dict:
    """
    Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath)
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    # Check 1: Không còn CCCD gốc dạng số thuần túy 12 chữ số
    # (kiểm tra format — sau anonymization cccd vẫn là 12 số nhưng khác giá trị gốc)
    if "cccd" in df.columns:
        invalid_cccd = df["cccd"].astype(str).apply(
            lambda x: not bool(re.match(r"^\d{12}$", x))
        )
        if invalid_cccd.any():
            results["success"] = False
            results["failed_checks"].append(
                f"CCCD format invalid in {invalid_cccd.sum()} rows"
            )

    # Check 2: Không có null values trong các cột quan trọng
    important_cols = ["patient_id", "benh", "ket_qua_xet_nghiem"]
    for col in important_cols:
        if col in df.columns and df[col].isnull().any():
            results["success"] = False
            results["failed_checks"].append(f"Null values found in {col}")

    # Check 3: Số rows phải bằng original
    original_df = pd.read_csv("data/raw/patients_raw.csv")
    if len(df) != len(original_df):
        results["success"] = False
        results["failed_checks"].append(
            f"Row count mismatch: {len(df)} vs {len(original_df)}"
        )

    return results
