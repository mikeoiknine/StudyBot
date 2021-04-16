from tika import parser
from pathlib import Path

import os

def parse_file(file_path):
    print(file_path)
    parsed = parser.from_file(file_path)['content'].splitlines()

    text = ""

    for s in parsed:
        if len(s) <= 2:
            continue
        s = s.strip()
        text = text + ' ' + s

    return text

def create_directory_if_path_doesnt_exist(file_path):
    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def save_text_to_file(text, file_path):
    create_directory_if_path_doesnt_exist(file_path)
    f = open(file_path, "w+", encoding='utf-8')
    f.write(text)
    f.close()

converted_files_path_prefix = "./data/converted_data/"

for subdir, dirs, files in os.walk('./data/Courses'):
    for file in files:
        #print os.path.join(subdir, file)
        filepath = subdir + os.sep + file

        if filepath.endswith(".pdf") or filepath.endswith(".txt"):
            extracted_text = parse_file(filepath)
            save_text_to_file(extracted_text, converted_files_path_prefix+filepath[6:-4]+'.txt') #remove ./data, append new file extension

