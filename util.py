import datetime
import uuid
import os
from pathlib import Path


ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']


def allowed_file(filename):
    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(image_file):
    if image_file and allowed_file(image_file.filename):
        unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
        image_path = 'static/uploads/' + unique_filename
        image_file.save(image_path)
        return image_path
    else:
        raise ValueError('Invalid file format. Please upload a JPG or PNG file.')


def get_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def delete_image_files(image_paths):
    [Path(image_path).unlink() for image_path in image_paths if image_path and
     Path(image_path).is_file() and Path(image_path).exists()]

