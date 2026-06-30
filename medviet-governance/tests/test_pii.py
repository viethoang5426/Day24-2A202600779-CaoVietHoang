# tests/test_pii.py
import pytest
import pandas as pd
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pii.anonymizer import MedVietAnonymizer

@pytest.fixture
def anonymizer():
    return MedVietAnonymizer()

@pytest.fixture
def sample_df():
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "raw", "patients_raw.csv"
    )
    return pd.read_csv(data_path).head(50)

class TestPIIDetection:

    def test_cccd_detected(self, anonymizer):
        text = "Bệnh nhân Nguyen Van A, CCCD: 012345678901"
        results = anonymizer.analyzer.analyze(text=text, language="vi",
                                               entities=["VN_CCCD"])
        # Assert rằng có ít nhất 1 result
        assert len(results) >= 1

    def test_phone_detected(self, anonymizer):
        text = "Liên hệ: 0912345678"
        results = anonymizer.analyzer.analyze(text=text, language="vi",
                                               entities=["VN_PHONE"])
        assert len(results) >= 1

    def test_email_detected(self, anonymizer):
        text = "Email: nguyenvana@gmail.com"
        results = anonymizer.analyzer.analyze(text=text, language="vi",
                                               entities=["EMAIL_ADDRESS"])
        assert len(results) >= 1

    # --- TASK QUAN TRỌNG ---
    def test_detection_rate_above_95_percent(self, anonymizer, sample_df):
        """Pipeline phải đạt >95% detection rate."""
        pii_columns = ["ho_ten", "cccd", "so_dien_thoai", "email"]
        rate = anonymizer.calculate_detection_rate(sample_df, pii_columns)
        print(f"\nDetection rate: {rate:.2%}")
        assert rate >= 0.95, f"Detection rate {rate:.2%} < 95%"

class TestAnonymization:

    def test_pii_not_in_output(self, anonymizer, sample_df):
        """Sau anonymization, không còn CCCD gốc trong output."""
        df_anon = anonymizer.anonymize_dataframe(sample_df)
        for original_cccd in sample_df["cccd"]:
            # Assert CCCD gốc không xuất hiện trong df_anon
            assert str(original_cccd) not in df_anon["cccd"].to_string()

    def test_non_pii_columns_unchanged(self, anonymizer, sample_df):
        """Cột benh và ket_qua_xet_nghiem phải giữ nguyên."""
        df_anon = anonymizer.anonymize_dataframe(sample_df)
        # Assert hai cột này không thay đổi
        pd.testing.assert_series_equal(
            sample_df["benh"].reset_index(drop=True),
            df_anon["benh"].reset_index(drop=True)
        )
        pd.testing.assert_series_equal(
            sample_df["ket_qua_xet_nghiem"].reset_index(drop=True),
            df_anon["ket_qua_xet_nghiem"].reset_index(drop=True)
        )
