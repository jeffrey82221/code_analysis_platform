"""
Step 4: Building revised dependency edges list and node list CSV files

Input: 
    deps.csv
Output: 
    dep_edge.csv
    pkg.csv
"""
import pandas as pd
dep_table = pd.read_csv('deps.csv')
pkg_table = pd.concat([dep_table[':START_ID(PKG)'], dep_table[':END_ID(PKG)']], axis=0).unique()
pkg_table = pd.DataFrame(pkg_table, columns = [':ID(PKG)'])
pkg_table = pkg_table.reset_index()
pkg_table.columns = [':ID(PKG)', 'name']
pkg_name_table = pkg_table.set_index('name')
dep_table[':START_ID(PKG)'] = pkg_name_table.loc[dep_table[':START_ID(PKG)']][':ID(PKG)'].tolist()
dep_table[':END_ID(PKG)'] = pkg_name_table.loc[dep_table[':END_ID(PKG)']][':ID(PKG)'].tolist()
dep_table.to_csv('dep_edge.csv', index=False)
pkg_table.to_csv('pkg.csv', index=False)