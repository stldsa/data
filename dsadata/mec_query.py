import os
import json
import pandas as pd
import geopandas as gpd
import geobuf

from sqlalchemy import and_
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from database import db
from dotenv import load_dotenv

load_dotenv()
# app = Flask(__name__)
# class PandasModel(db.Model):
#     @hybrid_property
#     def df(self):
#         return pd.read_sql("contribution", db.engine)

candidate_pac_dict = {
    "C201175": {
        "candidate_mec_id": "C201500",
        "candidate_name": "Lewis Reed",
        "pac_name": "One St. Louis",
    },
    "C201534": {
        "candidate_mec_id": "C201500",
        "candidate_name": "Lewis Reed",
        "pac_name": "Leadership Counts",
    },
    "C201113": {
        "candidate_mec_id": "C201499",
        "candidate_name": "Tishaura Jones",
        "pac_name": "314 Forward",
    },
    "C211552": {
        "candidate_mec_id": "C201099",
        "candidate_name": "Cara Spencer",
        "pac_name": "Gateway to Progress",
    },
}


class Candidate(db.Model):
    mec_id = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String)
    committee_name = db.Column(db.String)
    office_sought = db.Column(db.String)
    # status = db.Column(db.String)
    # contributions = db.relationship(
    #     "Contribution",
    #     back_populates="candidate",
    #     cascade="all, delete",
    #     passive_deletes=True,
    # )

    @classmethod
    def df(self):
        df = pd.read_sql("candidate", db.engine)
        return df

    # return pd.DataFrame()

    @hybrid_property
    def stats(self):
        # print(self.contributions)
        # for contribution in self.contributions:
        #     print(contribution, contribution.amount)
        return {
            "$ Raised": sum(contribution.amount for contribution in self.contributions)
        }


class Contributor(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String)
    zip5 = db.Column(db.String)
    is_committee = db.Column(db.Boolean)


class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    # mec_id = db.Column(db.String, db.ForeignKey("candidate.mec_id"))
    mec_id = db.Column(db.String)
    # candidate = db.relationship("Candidate", back_populates="contributions")
    # contributor_id =:E db.Column(
    #     db.Integer,
    #     db.ForeignKey("contributor.id", ondelete="CASCADE"),
    # )
    # contributor = db.relationship(
    #     "Contributor", backref=db.backref("contributions", lazy=True)
    # )
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    employer = db.Column(db.String)
    occupation = db.Column(db.String)
    amount = db.Column(db.Float)
    contribution_type = db.Column(db.String)
    # report = db.Column(db.String)

    # @hybrid_property
    # def df(self):
    #     with app.app_context():
    #         df = pd.read_sql("contribution", db.engine.connect())
    #     return

    @hybrid_property
    def sum(self):
        self.df["amount"].sum()


def build_mec_df(mec_ids):
    li = []
    for filename in os.listdir("data/mec_geocoded"):
        df_geocoded = pd.read_csv(
            "data/mec_geocoded/" + filename, header=0, parse_dates=["Date"]
        )
        # this is hacky but I'm doing this to make sure we don't miss non-geocoded rows:
        #  we should adjust geocode to not lose those rows
        df_nogeocode = pd.read_csv(
            "data/mec/" + filename, header=0, parse_dates=["Date"]
        )
        if len(df_geocoded.index) < len(df_nogeocode.index):
            df = pd.concat([df_geocoded, df_nogeocode])
            df = df.drop_duplicates(subset=["CD1_A ID"]).reset_index(drop=True)
        else:
            df = df_geocoded
        df.loc[:, "ZIP5"] = df.loc[:, "Zip"].astype(str).str[:5]
        df.loc[:, "MECID"] = df.loc[:, " MECID"]
        df = df[df["MECID"].isin(mec_ids)]
        li.append(df)
    frame = pd.concat(li, verify_integrity=True)
    return frame


def clear_tables():
    Contribution.query.delete()
    Candidate.query.delete()
    Contributor.query.delete()
    db.session.commit()


def create_tables():
    db.create_all()
    db.session.commit()


def create_contributions(mec_df):
    mec_col_name = " MECID"  # this column has a space in front for some reason
    name_dict = {  # FIXME: This is a shortcut for now
        "Tishaura O. Jones for Mayor": "Tishaura Jones",
        "Cara Spencer For Mayor": "Cara Spencer",
        "Reed For St Louis": "Lewis Reed",
        "Friends of Andrew Jones": "Andrew Jones",
    }
    candidate_dict = {}
    contributor_dict = {}
    all_contributions = []
    for index, row in mec_df.iterrows():

        if row[mec_col_name] not in candidate_dict:
            this_candidate = Candidate(
                name=name_dict[row["Committee Name"]],
                committee_name=row["Committee Name"],
                mec_id=row[mec_col_name],
            )
            candidate_dict[row[mec_col_name]] = this_candidate
            db.session.add(this_candidate)
            db.session.commit()
        else:
            this_candidate = candidate_dict[row[mec_col_name]]

        contributor_name = "no name"
        is_committee = False
        if isinstance(row["Committee"], str):
            contributor_name = row["Committee"].strip()
            is_committee = True
        elif isinstance(row["Company"], str):
            contributor_name = row["Company"].strip()
        elif isinstance(row["Last Name"], str):
            contributor_name = (
                row["First Name"].strip() + str(" ") + row["Last Name"].strip()
            )

        namezip = contributor_name + " " + row["ZIP5"]
        if namezip not in contributor_dict:
            this_contributor = Contributor(
                name=contributor_name, zip5=row["ZIP5"], is_committee=is_committee
            )
            contributor_dict[namezip] = this_contributor
            db.session.add(this_contributor)
            db.session.commit()
        else:
            this_contributor = contributor_dict[namezip]

        if row["Latitude"] and row["Longitude"]:
            lat = row["Latitude"]
            lon = row["Longitude"]
        else:
            lat = None
            lon = None

        this_contribution = Contribution(
            candidate=this_candidate,
            mec_id=this_candidate.mec_id,
            contributor=this_contributor,
            contributor_id=this_contributor.id,
            lat=lat,
            lon=lon,
            employer=row["Employer"],
            occupation=row["Occupation"],
            date=row["Date"],
            amount=row["Amount"],
            contribution_type=row["Contribution Type"],
            report=row["Report"],
        )
        all_contributions.append(this_contribution)
    return all_contributions


# This is like the function below, but we don't need to geocode zips
def build_zip_donation_pbf_from_geojson(
    contribution_df,
    contest_name,
    candidate_mec_ids,
    contest_pac_ids,
    polygons_geojson_data,
    output_geobuf_path,
):
    polygons = gpd.read_file(polygons_geojson_data)
    zip_df = contribution_df.groupby(by=["ZIP5", "MECID"]).agg({"Amount": "sum"})
    zip_total_df = contribution_df.groupby(by=["ZIP5"]).agg({"Amount": "sum"})
    for index, polygon in polygons.iterrows():
        this_zip = polygon.ZCTA5CE10
        no_pac_total = 0
        if this_zip in zip_df.index:
            mec_donations = zip_df.loc[this_zip].to_dict()
            candidate_geography_totals = {}
            for mec_id in candidate_mec_ids:
                if mec_id in mec_donations["Amount"]:
                    this_candidate_donations = mec_donations["Amount"][mec_id]
                else:
                    this_candidate_donations = 0
                polygons.loc[
                    index, "mec_donations_" + mec_id
                ] = this_candidate_donations
                candidate_geography_totals[mec_id] = this_candidate_donations
                no_pac_total = no_pac_total + this_candidate_donations
            for pac_id in contest_pac_ids:
                if pac_id in candidate_pac_dict and pac_id in mec_donations["Amount"]:
                    this_pac = candidate_pac_dict[pac_id]
                    candidate_geography_totals[this_pac["candidate_mec_id"]] = (
                        mec_donations["Amount"][pac_id]
                        + candidate_geography_totals[this_pac["candidate_mec_id"]]
                    )

            # Add pac to totals
            for cand_mec_id in candidate_mec_ids:
                if cand_mec_id in candidate_geography_totals:
                    polygons.loc[
                        index, "mec_donations_" + cand_mec_id + "_with_pacs"
                    ] = candidate_geography_totals[cand_mec_id]
                else:
                    polygons.loc[index, "mec_dotations_" + mec_id + "_with_pacs"] = 0
                total_monetary_donations = zip_total_df.loc[this_zip].Amount
        else:
            total_monetary_donations = 0
        polygons.loc[index, "total_monetary_donations_" + contest_name] = no_pac_total
        polygons.loc[
            index, "total_monetary_donations_" + contest_name + "_with_pacs"
        ] = total_monetary_donations

    polygons_json = polygons.to_json()
    polygon_geojson_data = json.loads(polygons_json)
    pbf = geobuf.encode(polygon_geojson_data)
    with open(output_geobuf_path, "wb") as write_file:
        write_file.write(pbf)


def build_donation_pbf_from_geojson(
    contribution_gdf,
    contest_name,
    candidate_mec_ids,
    contest_pac_ids,
    polygons_geojson_paths,
    output_geobuf_path,
):
    # polygons = gpd.read_file(polygons_geojson_path)
    polygons = gpd.GeoDataFrame(
        pd.concat([gpd.read_file(i) for i in polygons_geojson_paths], ignore_index=True)
    )

    for index, polygon in polygons.iterrows():
        total_monetary_donations = 0
        # total_nonmonetary_donations = 0
        donations_this_geography = {}
        no_pac_total = 0
        candidate_geography_totals = {}
        pip = contribution_gdf.within(polygon.geometry)
        for j, row in contribution_gdf[pip].iterrows():
            # Each iteration here is a contribution inside of this polygon's geometry:
            if row.contribution_type == "M":
                total_monetary_donations = total_monetary_donations + row.amount
                if row.mec_id in candidate_mec_ids:
                    if row.mec_id not in donations_this_geography:
                        donations_this_geography[row.mec_id] = 0
                    donations_this_geography[row.mec_id] = (
                        donations_this_geography[row.mec_id] + row.amount
                    )
                    no_pac_total = no_pac_total + row.amount
                elif row.mec_id in contest_pac_ids:
                    if row.mec_id not in donations_this_geography:
                        donations_this_geography[row.mec_id] = 0
                    donations_this_geography[row.mec_id] = (
                        donations_this_geography[row.mec_id] + row.amount
                    )
        polygons.loc[index, "total_monetary_donations_" + contest_name] = no_pac_total
        polygons.loc[
            index, "total_monetary_donations_" + contest_name + "_with_pacs"
        ] = total_monetary_donations

        for mec_id in candidate_mec_ids:
            if (
                mec_id in donations_this_geography
                and donations_this_geography[mec_id] > 0
            ):
                this_candidate_donations = donations_this_geography[mec_id]
            else:
                this_candidate_donations = 0
            polygons.loc[index, "mec_donations_" + mec_id] = this_candidate_donations
            candidate_geography_totals[mec_id] = this_candidate_donations
        for pac_id in contest_pac_ids:
            this_pac = candidate_pac_dict[pac_id]
            if pac_id in donations_this_geography:
                candidate_geography_totals[this_pac["candidate_mec_id"]] = (
                    candidate_geography_totals[this_pac["candidate_mec_id"]]
                    + donations_this_geography[pac_id]
                )
        for mec_id in candidate_mec_ids:

            polygons.loc[
                index, "mec_donations_" + mec_id + "_with_pacs"
            ] = candidate_geography_totals[mec_id]

    polygons_json = polygons.to_json()
    polygon_geojson_data = json.loads(polygons_json)
    pbf = geobuf.encode(polygon_geojson_data)
    with open(output_geobuf_path, "wb") as write_file:
        write_file.write(pbf)


def insert_contributions(contribution_objects):
    db.session.bulk_save_objects(contribution_objects)
    db.session.commit()


def get_all_contributions():
    return Contribution.query.all()


def get_all_contributors():
    contributors = Contributor.query.all()
    return_contributors = []
    for contributor in contributors:
        total_contributions = 0
        for contribution in contributor.contributions:
            total_contributions = total_contributions + contribution.amount
        return_contributors.append(
            {
                "name": contributor.name,
                "zip5": contributor.zip5,
                "total_contribution": total_contributions,
            }
        )
    return sorted(
        return_contributors, key=lambda contributor: contributor["total_contribution"]
    )


def get_candidate_total_donations(candidate_name):
    return (
        db.session.query(func.sum(Contribution.amount))
        .filter(
            and_(
                Contribution.candidate.has(name=candidate_name),
                Contribution.contribution_type == "M",
            )
        )
        .scalar()
    )


def get_contribution_stats_for_candidate(candidate_name):
    contributions = Contribution.query.filter(
        Contribution.candidate.has(name=candidate_name)
    )
    total_collected_monetary = 0
    num_donations = 0
    for contribution in contributions:
        if contribution.contribution_type == "M":
            total_collected_monetary = contribution.amount + total_collected_monetary
            num_donations = 1 + num_donations
    average_donation = total_collected_monetary / num_donations
    stats = {
        "total_collected": total_collected_monetary,
        "num_donations": num_donations,
        "average_donation": average_donation,
    }
    return stats


def get_standard_contest_name(contest):
    contest_parts = contest.split(" - ")
    if contest_parts[0] == "Alderperson":
        contest_name = contest_parts[1].replace(" ", "")
    else:
        contest_name = contest_parts[0]
    return contest_name