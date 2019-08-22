# # Stock Control
# - Import exported crytal report from starlims
# - Create list of different reagents based on location/activity (e.g. level 3 cold room, ddPCR, NGS)
# - Export different stock lists for each locaiton/activity
# - Highlight items that have gone past their expiry date
# - Highlight items realeased but not yet acceptance tested
#
# ## Further goals
# - Add in minimum stock levels and create list of items that fall below min stock

import os
import pandas as pd
import numpy as np
from datetime import datetime
stocklist = pd.read_csv("20190426_starlims_testing_kit_list.csv")
groups = pd.read_csv("groups.csv")

#Convert 'Received Date' and 'Expiry Date' columns to datetime
stocklist['Received Date'] = pd.to_datetime(stocklist['Received Date'])
stocklist['Expiry Date'] = pd.to_datetime(stocklist['Expiry Date'])
#Add new column 'Expired' = 'Yes/No'
stocklist['Expired'] = stocklist['Expiry Date'].apply(lambda x: "Yes" if x < pd.to_datetime(timenow.date()) else "No")

#Create dict including each group {header : list of inventory items}
group_dict = {}
for column in groups:
    arr = np.array(groups[column])
    arr = arr[pd.notnull(arr)]
    group_dict.update({column : arr})

#Loop through keys of group_dict to create new df's filtered based on their inventory items
group_dfs = {}
group_names = list(groups)

for grp in group_names:
    #do some calcs to get a dataframe called 'df'
    group_dfs[grp] = stocklist[stocklist['Material Code'].isin(group_dict[grp])]

#export list of inventory items based on each groups
for df in group_dfs:
    outname = df + " " + str(datetime.now().date()) + '.xlsx'
    outdir = './Stock check lists'
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    fullname = os.path.join(outdir, outname)
    group_dfs[df].to_excel(fullname, sheet_name=df, index=False)
