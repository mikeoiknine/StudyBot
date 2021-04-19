import requests
import os
import xmltodict
import json

def get_spotlight_annotated_file_as_dictionary(file_path):
    headers = {'Accept':'text/xml'}
    file_content = open(file_path, 'r', encoding='utf-8').read()
    data = {'confidence':'0.35', 'support':'0', "text":file_content}
    r = requests.post("http://localhost:2222/rest/annotate", headers=headers, data=data)
    return(xmltodict.parse(r.content))

def create_directory_if_path_doesnt_exist(file_path):
    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except OSError as exc: # Guard against race condition
            raise

def save_text_to_file(text, file_path):
    create_directory_if_path_doesnt_exist(file_path)
    f = open(file_path, "w+", encoding='utf-8')
    f.write(text)
    f.close()

annotated_files_path_prefix = "./data/annotated_data/"

dict_filepath_annotations = {}

if __name__ == "__main__":

    for subdir, dirs, files in os.walk('./data/preprocessed_data/Courses'):
        for file in files:
            #print os.path.join(subdir, file)
            filepath = subdir + os.sep + file

            if filepath.endswith(".txt"):
                annotations_dict = get_spotlight_annotated_file_as_dictionary(filepath)
                dict_filepath_annotations[filepath] = annotations_dict
                save_text_to_file(json.dumps(annotations_dict), annotated_files_path_prefix+filepath[21:-4]+'.txt') #remove ./data/preprocessed_data, append new file extension
