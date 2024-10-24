import csv
from flask import current_app


def get_default_lang_id():
    return 1


def csv_export(user_id, headers, data):
    file_name = current_app.config['CSV_EXPORT_FOLDER'] + \
        '/' + str(user_id) + '.csv'
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for d in data:
            values = [d.get(header) for header in headers]
            writer.writerow(values)
    return str(user_id) + '.csv'
