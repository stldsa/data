import pandas as pd
import plotly.express as px
from flask import url_for


class Candidate:
    def __init__(self, mec_id):
        self.mec_id = mec_id
        self.df = self.df.loc[mec_id]

    df = pd.read_csv(
        url_for("static", filename="candidates_2021-03-02.csv"), index_col="MECID"
    )

    @classmethod
    @property
    def amounts_raised(self):
        return Contribution.df.groupby(" MECID")["Amount"].sum()

    @classmethod
    @property
    def plot(self):
        amount = self.amounts_raised.rename("$ Raised")
        fig = px.bar(
            amount,
            # x="$ Raised",
            # y=amount.index,
            template="simple_white",
        )
        return fig


class Contribution:
    df = pd.read_csv("data/mec_geocoded/all_years.csv", index_col="CD1_A ID")