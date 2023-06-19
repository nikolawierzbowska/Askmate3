import connection
import datetime
import os
import uuid


def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def save_image_dm(image_file):
    unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
    image_path = 'static/uploads/' + unique_filename
    image_file.save(image_path)
    return image_path


# TODO update funkcji pod baza danych
def delete_image_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
