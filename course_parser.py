import pandas as pd
import os
from annotate_files import get_spotlight_annotated_file_as_dictionary

from constants import COURSE_DATA_CSV, COURSE_DESCRIPTIONS_CSV, CSV_KEYS, DESCRIPTION_PLACEHOLDERS, COURSE_DATA, LECTURE_KEYS, PREPROCESSED_COURSE_DATA


def parse_courses():
    """
    Parses the Course data and description csv files found in the
    ./data/CSV/ folder.

    Returns a list of dictionaries representing courses.
    """

    # Read course data file as list of dictionaries
    courses = pd.read_csv(
        COURSE_DATA_CSV, encoding="ISO-8859-1").filter(CSV_KEYS).to_dict(orient="records")

    # Read course description into dataframe
    descriptions = pd.read_csv(COURSE_DESCRIPTIONS_CSV, encoding="ISO-8859-1")

    # Annotate course with description from course description csv. `Course ID` is used
    # as a foreign key and then removed from the course dict.
    for course in courses:
        key = course.get("Course ID", None)
        if key is None:
            continue

        key = int(key)
        res = descriptions[descriptions["Course ID"] == int(key)]
        if res.empty:
            continue

        course_descr = res["Descr"].values[0]
        if not pd.isna(course_descr) and course_descr not in DESCRIPTION_PLACEHOLDERS:
            course["Description"] = course_descr.strip()

        # No longer need foreign key
        course.pop("Course ID", None)

    return courses


def get_paths_and_preprocessed_paths(base_path, base_preprocessed_path, key):
    """
    Explores the path formed by appending `key` to `base_path` and `base_preprocessed_path` and returning a list of 
    dictionaries for each of the files found. The dictionary includes the "filepath" and the "preprocessed_file_path" for each file.

    If no such path exists, None is returned.
    """
    path = os.path.join(base_path, key)
    preprocessed_path = os.path.join(base_preprocessed_path, key)
    if not os.path.exists(path) or not os.path.exists(preprocessed_path):
        return []
    return [{
        'filepath': os.path.join(path, f), 
        'preprocessed_file_path': os.path.join(preprocessed_path, f)[:-4]+".txt" #remove .pdf, add .txt
    } for f in os.listdir(path)]

def get_paths(base_path, key):
    """
    Explores the path formed by appending `key` to `base_path` and returning a list of 
    all the files found.

    If no such path exists, None is returned.
    """
    path = os.path.join(base_path, key)
    if not os.path.exists(path):
        return None
    return [os.path.join(path, f) for f in os.listdir(path)]


def parse_local_courses():
    """
    Parse the course data in the structured directories in the COURSE_DATA path.

    Returns a list of dictionaries containing the courses found in the path.
    """
    courses = []
    abs_course_data_path = os.path.abspath(COURSE_DATA)
    abs_preprocessed_course_data_path = os.path.abspath(PREPROCESSED_COURSE_DATA)
    for course_path in os.listdir(abs_course_data_path):
        course = {}

        name, number = course_path.split()[0],  course_path.split()[1]
        course["Subject"], course["Number"] = name, number

        # Use absolute paths for individual resources
        preprocessed_course_path = os.path.join(abs_preprocessed_course_data_path, course_path)
        course_path = os.path.join(abs_course_data_path, course_path)

        # Check for course outline
        outlines = []
        outline_path_dicts = get_paths_and_preprocessed_paths(course_path, preprocessed_course_path, "Outlines")
        for filepath_dict in outline_path_dicts:
                annotations = get_spotlight_annotated_file_as_dictionary(filepath_dict['preprocessed_file_path'])
                docDict = {
                    "annotations": annotations,
                    "file_path": filepath_dict['filepath']
                }
                outlines.append(docDict)
        course["Outlines"] = outlines

        # Explore lectures
        lectures = parse_course_lectures(course_path, preprocessed_course_path)
        course["Lectures"] = lectures
        courses.append(course)

    return courses


def parse_course_lectures(course_path, preprocessed_course_path):
    """
    Parse the lecture data of a given course
    """
    lectures = []

    base_lecture_path = os.path.join(course_path, "Lectures")
    base_preprocessed_lecture_path = os.path.join(preprocessed_course_path, "Lectures")
    for lecture_dir in os.listdir(base_lecture_path):
        lecture = {}

        # Extract Lecture metadata
        s = lecture_dir.split()
        name, number = '_'.join(s[3:]), s[1]
        lecture["Name"], lecture["Number"] = name, number

        # Add all of the file paths found in the lecture_path subdirectory
        lecture_path = os.path.join(base_lecture_path, lecture_dir)
        preprocessed_lecture_path = os.path.join(base_preprocessed_lecture_path, lecture_dir)
        for key in LECTURE_KEYS:
            lecture[key] = []
            filepath_dicts = get_paths_and_preprocessed_paths(lecture_path, preprocessed_lecture_path, key)
            for filepath_dict in filepath_dicts:
                annotations = get_spotlight_annotated_file_as_dictionary(filepath_dict['preprocessed_file_path'])
                docDict = {
                    "annotations": annotations,
                    "file_path": filepath_dict['filepath']
                }
                lecture[key].append(docDict)
        lectures.append(lecture)
    return lectures
