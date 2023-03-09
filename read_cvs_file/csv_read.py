import csv
import os

# 获取告警名称配置文件
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(BASE_DIR, 'warning.csv')


def csv_to_dict(csv_name):
    data = {}
    with open(csv_name, encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:

            data[row['warning_code']] = row
    return data


row_dict = csv_to_dict(filename)
print(row_dict)
