import os
import pandas as pd

import contrib
import mec_query

# Right now only doing mayoral race, but update as necessary
mayor_mec_ids = ['C201499', 'C201099', 'C201500', 'C211544']
mec_df = mec_query.build_mec_df(mayor_mec_ids)
mec_query.clear_tables()
mec_query.insert_contributions(mec_df)
all_contributions = mec_query.get_all_contributions()