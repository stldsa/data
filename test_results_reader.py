import results_reader
import datatest as dt
import pytest
import pdfplumber


@pytest.fixture
def sample_pdf_path():
    return "data/pdf/2020-06-23_precinct.pdf"


@pytest.fixture
def sample_pdf(sample_pdf_path):
    return pdfplumber.open(sample_pdf_path)


@pytest.fixture
def data_pages(sample_pdf):
    return results_reader.pdf_to_data_pages(sample_pdf)


@pytest.fixture
def results_indexes():
    return {
        "Election Date",
        "Ward",
        "Precinct",
        "Ballot Selection",
        "Vote Type",
    }


def test_parse_pdf(sample_pdf_path, results_indexes):
    page_num = 222

    precinct_data = results_reader.parse_pdf(sample_pdf_path)
    dt.validate(precinct_data.columns, {"votes"})
    dt.validate(precinct_data.index.names, results_indexes)


def test_pdf_to_data_pages(sample_pdf_path):
    pdf = pdfplumber.open(sample_pdf_path)
    data = results_reader.pdf_to_data_pages(pdf)
    assert len(data) == len(pdf.pages)


def test_tidy_data(data_pages, results_indexes):
    tidy_df = results_reader.tidy_data(data_pages)

    dt.validate(tidy_df.columns, {"votes"})
    dt.validate(tidy_df.index.names, results_indexes)