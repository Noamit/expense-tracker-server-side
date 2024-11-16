import csv
from flask import current_app
import hashlib


def get_default_lang_id():
    return 1


def csv_export(user_id, headers, data):
    hash_object = hashlib.sha256((str(user_id)).encode())
    hash_user = hash_object.hexdigest()
    file_name = current_app.config['CSV_EXPORT_FOLDER'] + \
        '/' + hash_user + '.csv'
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for d in data:
            values = [d.get(header) for header in headers]
            writer.writerow(values)
    return hash_user + '.csv'
