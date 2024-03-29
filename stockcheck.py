#!/usr/bin/env python
# coding: utf-8

# # Stock Control
# - Import exported crytal report from starlims
# - Create list of different reagents based on location/activity (e.g. level 3 cold room, ddPCR, NGS)
# - Export different stock lists for each locaiton/activity
# - Highlight items that have gone past their expiry date
# - Highlight items realeased but not yet acceptance tested
# - Check that number of unique items on all groups equal the total number in the starlims export list (so nothing gets missed)
#     - Need to export list that includes missing items from both lists
# - Quick inventory check list (just value_counts)
#
# ## Further goals
# - Add in minimum stock levels and create list of items that fall below min stock
# - Graphs:
#     - Items expired
#     - Items released and not accpetance tested
#     - For each group (join some groups together (e.g. MLPA, PCR, ddPCR))
#
# ## Refactoring bits
# - Create a function to do the writing to excel files and folder checks


import os
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

#Functions
#---> Need to move functions into a class
#----------------------------------------------------------------------------#
#Add value counts as a new column in the main def
def add_value_counts(count_series, cell):
    #if material name equals index in count_series return counts
    for item in count_series.iteritems():
        if cell.lower() == item[0].lower():
            return item[1]


def create_pie(data, title, outdir):

    if len(data.index) <= 1:
        f=open(os.path.join(outdir, title + ' - graph error.txt'), "w+")
        f.write('No data to create graph')
        f.close()
        return None

    def absval(pct, allvals):
        return int(pct/100.*np.sum(allvals))

    labels = data.index
    sizes = data
    explode = (0, 0.1)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct=lambda pct: absval(pct, data),
            shadow=True, startangle=90)
    ax1.axis('equal')
    plt.title(title + " - " + str(datetime.now().date()), fontsize=15)
    plt.savefig(outdir + '//' + title + '.png')
    plt.close()

#----------------------------------------------------------------------------#

#crystal report from starlims
stocklist = pd.read_excel("starlims_stock_check.xls", encoding = "ISO-8859-1")
#User defined inventory groups. Each column is an individual group
groups = pd.read_csv("inventory_groups.csv", encoding = "ISO-8859-1")
#User defined minimum stock and reorder values
min_stock = pd.read_csv("minimum_stock.csv", encoding = "ISO-8859-1")

#Remove empty columns
stocklist.dropna(axis=0, how='all', thresh=None, inplace=True)

#Rename used column headers
stocklist.rename(columns={'MATCODE':'Material Code', 'MATNAME':'Material name', \
'INVENTORYID':'Inv ID', 'LOCATION_CODE':'Location', 'LOTNO':'Lot Number', \
'CATNO':'Catelogue Number', 'RECEIVE_DATE':'Received Date', 'EXPIRE_DATE':'Expiry Date', \
'SUPPCODE':'Supplier Code','STATUS':'Status','BREAKCASE':'Acceptance Tested'}, inplace=True)

#Change all 'Material names' to lowercase remove cases typos
stocklist['Material name'] = stocklist['Material name'].apply(lambda x: x.lower())
min_stock['Material name'] = min_stock['Material name'].apply(lambda x: x.lower())
groups = groups.replace(np.nan,'',regex=True)
for column in groups.columns:
    groups[column] = groups[column].apply(lambda x: x.lower())

#Convert 'Received Date' and 'Expiry Date' columns to datetime
stocklist['Received Date'] = pd.to_datetime(stocklist['Received Date'])
stocklist['Expiry Date'] = pd.to_datetime(stocklist['Expiry Date'])
#Add new column 'Expired' = 'Yes/No'
stocklist['Expired'] = stocklist['Expiry Date'].apply(lambda x: "Yes" if x < pd.to_datetime(datetime.now().date()) else "No")
stocklist['Acceptance Tested'] = stocklist['Acceptance Tested'].replace('Y', 'Yes').replace('N', 'No')

#Add count columns
vc_stocklist = stocklist['Material name'].value_counts()
stocklist['CurrentQuantity'] = stocklist['Material name'].apply(lambda x: add_value_counts(vc_stocklist, x))

#Create array for each group header, contents = inventory items
group_dict = {}
for column in groups:
    arr = np.array(groups[column])
    arr = arr[pd.notnull(arr)]
    group_dict.update({column : arr})

#Loop through keys of group_dict to create new df's filtered based on their lists
group_dfs = {}
group_names = list(groups)

for grp in group_names:
    #Create df's based on inventory lists from group_dict
    #Create copy of the df otherwise it causes errors later when trying to sort etc
    group_dfs[grp] = stocklist[stocklist['Material name'].isin(group_dict[grp])].copy()


#Create seperate folders for each group
outdir = './' + str(datetime.now().date()) + ' Stock check output'
if not os.path.exists(outdir):
    os.mkdir(outdir)
    for df in group_dfs:
        os.mkdir(os.path.join(outdir, df))

#Save df to their corresponding folders
for df in group_dfs:
    outname = df + " 1_detailed " + str(datetime.now().date()) + '.xlsx'
    outdir = './' + str(datetime.now().date()) + ' Stock check output//' + df
    fullname = os.path.join(outdir, outname)
    group_dfs[df].sort_values(['Location', 'Material name', 'Status', 'Acceptance Tested'], ascending=[True, True, False, False],inplace=True)
    group_dfs[df].to_excel(fullname, sheet_name=df, index=False)

#Save individual group dfs for value_counts, expired, acceptance testing
for df in group_dfs:
    sum_df = group_dfs[df]['Material name'].value_counts()
    exp_df = group_dfs[df][group_dfs[df]['Expired'] == "Yes"]
    accept_df = group_dfs[df][group_dfs[df]['Acceptance Tested'] == 'No']
    #Reset summary df index, rename columns, merge min_stock data and create new 'OrderNow' column
    sum_df_reset = sum_df.reset_index().rename(columns={'index':'Material name', 'Material name':'Counts'})
    min_stock_df = pd.merge(sum_df_reset, min_stock, on="Material name")
    min_stock_df['OrderNow'] = min_stock_df['Counts'] <= min_stock_df['MinStock']

    sum_outname = df + " 2_summary " + str(datetime.now().date()) + '.xlsx'
    exp_outname = df + " 3_expired " + str(datetime.now().date()) + '.xlsx'
    accept_outname = df + " 4_acceptance tested " + str(datetime.now().date()) + '.xlsx'
    min_stock_outname = df + " 5_min stock " + str(datetime.now().date()) + '.xlsx'

    outdir = './' + str(datetime.now().date()) + ' Stock check output//' + df
    sum_df.to_excel(os.path.join(outdir, sum_outname), sheet_name=df)
    exp_df.to_excel(os.path.join(outdir, exp_outname), sheet_name=df)
    accept_df.to_excel(os.path.join(outdir, accept_outname), sheet_name=df)
    min_stock_df[min_stock_df['OrderNow'] == True].to_excel(os.path.join(outdir, min_stock_outname), sheet_name=df)

    #Generate graphs
    create_pie(group_dfs[df]['Expired'].value_counts(), df + ' Expired', outdir)
    create_pie(group_dfs[df]['Acceptance Tested'].value_counts(), df + ' Acceptance test', outdir)
    create_pie(group_dfs[df]['Status'].value_counts(), df + ' Release Status', outdir)
    create_pie(group_dfs[df][group_dfs[df]['Status'] == "Released"]['Acceptance Tested'].value_counts(), df + ' Acceptance test (Released)', outdir)

#Check to see if all inventory items are accounted for
stocklist_check = set(stocklist['Material name'])
groups_check = []
for grp in groups:
    groups_check.append(groups[grp].values)
groups_check = np.asarray(groups_check).flatten()
groups_check = set(groups_check[pd.notnull(groups_check)])

if len(groups_check.difference(stocklist_check)) == 0 and len(stocklist_check) == len(groups_check):
       print("All Starlims inventory items accounted for.")
else:
    stocklist_missing = pd.DataFrame(list(stocklist_check.difference(groups_check)), columns=["Not in Input File"])
    groups_missing = pd.DataFrame(list(groups_check.difference(stocklist_check)), columns=["Not in Starlims"])
    missing_items = pd.concat([stocklist_missing, groups_missing], axis=1)
    missing_items.to_excel('./' + str(datetime.now().date()) + ' Stock check output/Missing Inventory.xlsx', index=False)

#merge value_counts for each item and minimum stock/reorder data
stock_count = stocklist['Material name'].value_counts().to_frame('counts').reset_index().rename(columns={'index':'Material name'})
stock_count = pd.merge(stock_count, min_stock, on='Material name')
stock_count['OrderNow'] = stock_count['counts'] <= stock_count['MinStock']
#export complete list
stock_count.to_excel('./' + str(datetime.now().date()) + ' Stock check output/Complete stock count.xlsx', index=False)
#export list of items that have less items than minimum stock
stock_count[stock_count['OrderNow'] == True].to_excel('./' + str(datetime.now().date()) + ' Stock check output/Low stock.xlsx', index=False)
