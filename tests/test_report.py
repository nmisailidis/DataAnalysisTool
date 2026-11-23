import pandas as pd
import pytest

from core import report


def test_build_reports_sums_per_group():
    data = pd.DataFrame({
        "Category": ["Drinks", "Drinks", "Food"],
        "Quantity": [10, 5, 8],
    })

    summary = report.build_report(data, "Category", ["Quantity"])

    assert summary.loc["Drinks", "Quantity"] == 15
    assert summary.loc["Food", "Quantity"] == 8


def test_build_report_with_a_text_column():
    data = pd.DataFrame({
        "Category": ["Drinks", "Drinks", "Food"],
        "Quantity": [10, 5, 8],
        "Region": ["West", "East", "West"],
    })

    with pytest.raises(ValueError, match="Region"):
        report.build_report(data, "Category", ["Quantity", "Region"])


def test_build_report_with_unknown_column():
    data = pd.DataFrame({
        "Category": ["Drinks", "Drinks", "Food"],
        "Quantity": [10, 5, 8],
    })

    with pytest.raises(KeyError):
        report.build_report(data,"Category", ["Price"])


def test_build_report_with_unknown_groupby_column():
    data = pd.DataFrame({
        "Category": ["Drinks", "Drinks", "Food"],
        "Quantity": [10, 5, 8],
    })

    with pytest.raises(KeyError):
        report.build_report(data,"Region", ["Quantity"])


def test_build_report_with_two_columns():
    data = pd.DataFrame({
        "Category": ["Drinks", "Drinks", "Food"],
        "Quantity": [10, 5, 8],
        "Revenue": [20, 10, 40],
    })

    summary = report.build_report(data, "Category", ["Quantity", "Revenue"])

    assert summary.loc["Drinks", "Quantity"] == 15
    assert summary.loc["Drinks", "Revenue"] == 30