def build_report(data, group_by, columns):
    return data.groupby(group_by)[columns].sum()


def save_report(category_summary, path="Report.txt"):
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n--- Σύνοψη ανά Κατηγορία Προϊόντων ---\n")
        f.write(str(category_summary))