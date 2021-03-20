import pandas as pd
from constants import COURSE_DATA_CSV, COURSE_DESCRIPTIONS_CSV, KEYS, DESCRIPTION_PLACEHOLDER


def parse_courses():
    """
    Parses the Course data and description csv files found in the
    ./data/CSV/ folder.

    Returns a list of dictionaries representing courses.
    """

    # Read course data file as list of dictionaries
    courses = pd.read_csv(
        COURSE_DATA_CSV, encoding="ISO-8859-1").filter(KEYS).to_dict(orient="records")

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
        if not pd.isna(course_descr) and course_descr not in DESCRIPTION_PLACEHOLDER:
            course["Description"] = course_descr.strip()

        # No longer need foreign key
        course.pop("Course ID", None)

    return courses
