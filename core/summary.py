import re

import pandas as pd


def compute_stats(data: pd.DataFrame) -> dict:
    numeric = data.select_dtypes("number")
    return {
        "rows": len(data),
        "columns": list(data.columns),
        "totals": {str(column): round(float(numeric[column].sum()), 2) for column in numeric.columns},
        "averages": {str(column): round(float(numeric[column].mean()), 2) for column in numeric.columns},
        "missing_values": {str(column): int(data[column].isna().sum()) for column in data.columns},
    }


def stats_to_lines(stats: dict) -> str:
    lines = [f"Number of rows: {stats['rows']}"]
    for column in stats["totals"]:
        lines.append(f"{column} total: {stats['totals'][column]}")
        lines.append(f"{column} average: {stats['averages'][column]}")

    missing = {column: count for column, count in stats["missing_values"].items() if count > 0}
    if missing:
        lines.append(f"Missing values: {missing}")
    else:
        lines.append("Missing values: None")
    return "\n" .join(lines)


def allowed_numbers(stats: dict) -> set:
    values = [stats["rows"]]
    values += list(stats["totals"].values())
    values += list(stats["averages"].values())
    values += list(stats["missing_values"].values())

    allowed = set()
    for value in values:
        allowed.add(round(float(value), 2))
        allowed.add(round(float(value) * 100, 2))
    return allowed


def numbers_are_valid(text: str, stats: dict) -> bool:
    allowed = allowed_numbers(stats)
    for found in re.findall(r"\d[\d,]*(?:\.\d+)?", text):
        number = round(float(found.replace(",", "")), 2)
        if number not in allowed:
            return False
        return True


def template_summary(stats: dict) -> str:
    parts = [f"The dataset has {stats['rows']} rows."]

    for column in stats["totals"]:
        parts.append(f"{column}: total {stats['totals'][column]}, average {stats['averages'][column]}.")

    missing = {column: count for column, count in stats["missing_values"].items() if count > 0}
    parts.append(f"Missing values: {missing}." if missing else "No missing values.")
    return " ".join(parts)

