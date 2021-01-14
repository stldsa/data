import pdfplumber
import pandas as pd

crop_boundaries = (35, 133, 575, 755)
crop_header_boundaries = (35, 133, 575, 208)
crop_data_boundaries = (35, 208, 575, 755)
table_settings = {
    "horizontal_strategy": "text",
    "vertical_strategy": "text",
    "join_tolerance": 0,
    "keep_blank_chars": True,
    "text_x_tolerance": 2,
}


def pdf_to_data_pages(pdf):
    data = [page.crop(crop_data_boundaries) for page in pdf.pages]
    tables = [
        data_page.extract_table(table_settings=table_settings) for data_page in data
    ]
    return tables


def tidy_data(data_pages):
    first_page = pd.DataFrame(data_pages[0])
    header_names = [
        "CITYWIDE\n    W 04 P 01",
        "W 04 P 02",
        "W 04 P 03",
        "W 04 P 04",
        "W 04 P 05",
        "W 04 P 06",
        "W 04 P 07",
        "W 04 P 08",
        "W 04 P 09",
        "W 04 P 10",
        "Total",
    ]
    columns = [
        "Vote Type",
        " Reg. Voters",
        "Cards Cast",
        "% Turnout",
        "Reg. Voters",
        "Times Counted",
        "Total Votes",
        "DWINDERLIN EVANS",
        "DWINDERLIN EVANS %",
        "Write-In Votes",
        "Write-In Votes %",
    ]
    groups = first_page[0].isin(header_names)
    df = pd.DataFrame(first_page)
    df = first_page[~groups]
    df.columns = columns

    df = df.set_index("Vote Type")
    df = df[["DWINDERLIN EVANS", "Write-In Votes"]]

    for i in range(11):
        df.loc[(i - 1) * 4 : i * 4, "Precinct"] = i

    df["Precinct"] = df["Precinct"].astype("int")

    df = df.assign(Ward=4)
    df = df.reset_index()
    df = df.set_index(["Ward", "Precinct", "Vote Type"])
    df = df.melt(var_name="Ballot Selection", value_name="votes", ignore_index=False)
    df = df.reset_index()
    df["Election Date"] = "2020-06-23"
    df = df.set_index(
        ["Election Date", "Ward", "Precinct", "Ballot Selection", "Vote Type"]
    )
    return df


def parse_pdf(pdf_path):
    # page_num = 1
    # headers = [page.crop(crop_header_boundaries) for page in pdf.pages]
    # data = [page.crop(crop_data_boundaries) for page in pdf.pages]
    # table = data[page_num].extract_table(table_settings=table_settings)
    df = pd.DataFrame(
        data=[
            {
                "Election Date": "2020-06-23",
                "Ward": 4,
                "Precinct": 1,
                "Ballot Selection": "Dwinderlin Evans",
                "Vote Type": "Polling",
                "votes": 35,
            }
        ]
    ).set_index(["Election Date", "Ward", "Precinct", "Ballot Selection", "Vote Type"])
    return df
