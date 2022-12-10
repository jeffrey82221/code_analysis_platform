"""
Step 3: Build Dependency Edge List CSV file

Input: deps/*.json
Output: deps.csv
"""
import json
import os
from tqdm import tqdm
import io
import pandas as pd


def table_generator():
    """Read Json and Convert it to Pandas DataFrame"""
    for json_file in filter(lambda x: x.endswith(
            '.json'), tqdm(os.listdir('./deps'))):
        pkg = json_file.split('.json')[0]
        try:
            deps = json.load(open(f'./deps/{json_file}'))
        except UnicodeDecodeError as e:
            print('UnicodeDecodeError on', json_file)
            raise e
        if isinstance(deps, list) and len(deps) > 0:
            # , :END_ID(User), reaction_count:INT
            table = pd.DataFrame(
                deps,
                columns=[
                    ':END_ID(PKG)',
                    'test_purpose:BOOL'])
            table['test_purpose:BOOL'] = table['test_purpose:BOOL'] == 'test-dep'
            table[':START_ID(PKG)'] = pkg
            table = table[[':START_ID(PKG)',
                           ':END_ID(PKG)',
                           'test_purpose:BOOL']]
            yield table


def buff_generator(table_gen, table_cnt_per_buff=2):
    """Store pandas DataFrame as CSV into Buffer"""
    buff = io.StringIO()
    for i, table in enumerate(table_gen):
        table.to_csv(buff, index=False, header=(i == 0))
        if i % table_cnt_per_buff == (table_cnt_per_buff - 1):
            yield buff
            buff = io.StringIO()
    yield buff


def save_buff_as_csv(buff_gen):
    """Append CSV in Buffer into CSV FILE"""
    if os.path.exists('deps.csv'):
        os.remove('deps.csv')
    for buff in buff_gen:
        buff.seek(0)
        with open('deps.csv', 'a') as f:
            print(buff.getvalue(), file=f, end='')
            f.close()


if __name__ == '__main__':
    table_gen = table_generator()
    buff_gen = buff_generator(table_gen, table_cnt_per_buff=2)
    save_buff_as_csv(buff_gen)
