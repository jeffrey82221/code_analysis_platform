"""
Step 4: Enrich Package CSV with download count and import name

Input: pkg.csv
Output: pkg_full.csv
"""
import pandas as pd
import concurrent.futures
import tqdm
from api.import_name import main as call_import_name
from api.download import main as call_download_cnt


def get_import_names(pkg_names):
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        result = list(executor.map(call_import_name, tqdm.tqdm(pkg_names)))
    return result


def get_download_cnts(pkg_names):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        result = list(tqdm.tqdm(executor.map(call_download_cnt, pkg_names, chunksize=100), total=len(pkg_names)))
    return result


if __name__ == '__main__':
    table = pd.read_csv('pkg.csv')
    def clean_up_name(name):
        if '~=' in name:
            name = name.split('~=')[0]
        if '!=' in name:
            name = name.split('!=')[0]
        if '>=' in name:
            name = name.split('>=')[0]
        if '<' in name:
            name = name.split('<')[0]
        if ';' in name:
            name = name.split(';')[0]
        if '==' in name:
            name = name.split('==')[0]
        if '>' in name:
            name = name.split('>')[0]
        return name.strip()
    table['name_alias'] = table.name.map(clean_up_name)
    table['download_count'] = get_download_cnts(table.name_alias.tolist())
    table.to_csv('pkg_full.csv', index=False)
    print(table[table.download_count == -1].name.tolist())
