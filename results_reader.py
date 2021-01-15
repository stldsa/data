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
normal_column_names = ["Reg. Voters", "Cards Cast", "% Turnout", "Times Counted", "Total Votes"]
special_column_names = ["Write-In Votes"]
special_contest_names = ["TURN OUT", "TREASURER"] # Treasurer vote is an issue in 2020 nov election

#TODO:
election_date = "2020-06-23"

import re
new_contest_match = re.compile(r'(CITYWIDE\n\s*)?W (\d\d) P (\d\d)')


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

def parse_page_headers(pdf_obj, page_num):
    pdf_header_area = pdf_obj.pages[page_num].crop(crop_header_boundaries)
    headers = pdf_header_area.extract_words(y_tolerance=12, keep_blank_chars=True, use_text_flow=True)
    return_headers = ["Type"] # first column is always the ward or the vote type
    page_contests = [] # thus far this is only used when TURN OUT is on the same page as another contest
    for i in range(len(headers)):
        col_name = headers[i]["text"]
        if col_name in special_contest_names:
            page_contests.append(col_name)
        elif col_name.isupper() or col_name in normal_column_names or col_name in special_column_names: 
            return_headers.append(col_name)
            # candidate vote columns are in all caps and have a vote count and a percent data column, but only have one header column, so we'll add the percent one here 
            if i+1 == len(headers): 
                # the last phrase on the page is a special case: the contest name
                # TODO: What happens on pages with multiple contests? We see this with TURN OUT but we handle that specal case
                page_contests.append(return_headers.pop())
                break
            if col_name.isupper() or col_name in special_column_names:
                return_headers.append(col_name+" PERCENT")
    return {"columns":return_headers, "contests":page_contests}

def parse_page_data(pdf_obj, page_num):
    pdf_data_area = pdf_obj.pages[page_num].crop(crop_data_boundaries)
    table = pdf_data_area.extract_table(table_settings=table_settings)
    return table        

def parse_pdf(pdf_path):
    page_num = 1
    pdf = pdfplumber.open(pdf_path)    
    headers = [page.crop(crop_header_boundaries) for page in pdf.pages]
    
    data = [page.crop(crop_data_boundaries) for page in pdf.pages]
    table = data[page_num].extract_table(table_settings=table_settings)
    df = pd.DataFrame(table)
    return df

def create_dataframe(data, headers):
    page_df = pd.DataFrame(data)
    # we have only seen cases where there are two contests when looking at turnout also
    print(headers["contests"])
    if len(headers["contests"]) == 2:
        page_contest = headers["contests"][1]
    elif len(headers["contests"]) == 1:
        page_contest = headers["contests"][0]
    else:
        print("PAGE CONTESTS ISSUE")
        return []
    if len(headers['columns']) == len(page_df.columns):
        page_df.columns = headers['columns']
    elif len(headers['columns']) == len(page_df.columns)+1: 
        # this can happen if all of the final vote column have zero votes, and thus 
        # the "-" for the percents get read as a part of the table's ending line
        headers['columns'].pop()
        page_df.columns = headers['columns']
    else:
        print("PROBLEM WITH PAGE")
        
    # drop unnecessary percentage columns
    columns_to_drop = []
    for col_name in headers["columns"]:
        if col_name.endswith(" PERCENT") or col_name == "% Turnout":
            columns_to_drop.append(col_name)
    page_df = page_df.drop(columns=columns_to_drop)
    page_df["Contest"] = page_contest
    return page_df

def prep_pdf_pages(pdf_path):
    pdf = pdfplumber.open(pdf_path)
    pdf_pages = []
    for i in range(len(pdf.pages)):
        print("Reading page "+str(i))
        headers = parse_page_headers(pdf, i)
        data = parse_page_data(pdf, i)
        page_df = create_dataframe(data, headers)
        pdf_pages.append(page_df)
    return pdf_pages

def read_pages(pdf_page_dfs):
    tidy_data = []
    last_column_was_total = False
    ignoring = False
    for i in range(len(pdf_page_dfs)):
        for index, row in pdf_page_dfs[i].iterrows():
            # this is kind of a wacky hack but we want to ignore rows that are the accumulated totals: we can tell those begin when we get two totals in a row,
            if row["Type"] == "Total":
                if ignoring:
                    ignoring = False
                else:
                    if last_column_was_total:
                        ignoring = True
                    else:
                        last_column_was_total = True
                continue
            else:
                last_column_was_total = False
            if ignoring:
                continue
            if new_contest_match.match(row.Type):
                ward_num = int(new_contest_match.match(row.Type).group(2))
                precinct_num = int(new_contest_match.match(row.Type).group(3))
                print("New precint: W"+str(ward_num)+" P"+str(precinct_num))
            else:
                row_type = row["Type"]
                for col_name, content in row.iteritems():
                    if col_name.isupper() or col_name in special_column_names:
                        if not content.isnumeric():
                            content = 0
                        tidy_data.append({
                            "election_date":election_date,
                            "ward":ward_num,
                            "precinct":precinct_num,
                            "contest_name":row["Contest"],
                            "candidate_selection":col_name,
                            "vote_type":row_type,
                            "vote_count":int(content),
                        })
    return tidy_data
            
