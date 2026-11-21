import pandas as pd


def load_excel(source):
    if source.strip().startswith("https"):
        source_list = source.split("/")
        source_list[-1] = "export?format=xlsx"
        delimiter = "/"
        source = delimiter.join(source_list)

    return pd.read_excel(source)
