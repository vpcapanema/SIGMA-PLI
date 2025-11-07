import sys
import zipfile
import io
import csv

path = sys.argv[1]
with zipfile.ZipFile(path) as zf:
    for name in zf.namelist():
        if not name.lower().endswith('.csv'):
            continue
        print('---', name)
        with zf.open(name) as f:
            try:
                text = io.TextIOWrapper(f, encoding='utf-8')
                reader = csv.reader(text)
                for i,row in enumerate(reader):
                    print(row)
                    if i>=3:
                        break
            except Exception as e:
                print('ERROR reading', e)
