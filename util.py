import datetime
import connection
import os


def convert_timestamp_to_date(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp)
    return date.strftime("%Y-%m-%d %H:%M:%S")


def generated_id(cursor, table):
    query = "SELECT MAX(id) FROM {}.{}};".format("public", table)
    cursor.execute(query)
    result = cursor.fetchone()
    max_id = result[0] if result[0] is not None else 0
    return max_id + 1


def get_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def delete_image_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
