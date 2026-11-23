import pandas as pd


def build_report(data, group_by, columns):

    for i in columns:
        if not pd.api.types.is_numeric_dtype(data[i]):
            raise ValueError(f"'{i}' is not a number column")

    return data.groupby(group_by)[columns].sum()


def save_report(category_summary, path="Report.txt"):
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n--- Σύνοψη ανά Κατηγορία Προϊόντων ---\n")
        f.write(str(category_summary))