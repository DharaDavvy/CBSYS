"""
Tests for the Firebase model helpers (matric conversion, init logic).
"""

from app.models.firebase import matric_to_email


class TestMatricToEmail:
    def test_standard_conversion(self):
        assert matric_to_email("CSC/2024/001") == "csc-2024-001@faculty.local"

    def test_lowercase_input(self):
        assert matric_to_email("csc/2024/001") == "csc-2024-001@faculty.local"

    def test_strips_whitespace(self):
        assert matric_to_email("  CSC/2024/001  ") == "csc-2024-001@faculty.local"

    def test_different_department(self):
        assert matric_to_email("SWE/2023/042") == "swe-2023-042@faculty.local"

    def test_four_digit_id(self):
        assert matric_to_email("IFT/2025/1234") == "ift-2025-1234@faculty.local"
