import pandas as pd


def load_excel(source):

    source_type = "local"

    if source.strip().startswith("https"):
        source_type = "url"
        source_list = source.split("/")
        source_list[-1] = "export?format=xlsx"
        delimiter = "/"
        source = delimiter.join(source_list)

    return pd.read_excel(source), source_type
