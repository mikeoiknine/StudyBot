# Paths
COURSE_DATA_CSV = "./data/CSV/course_catalog.csv"
COURSE_DESCRIPTIONS_CSV = "./data/CSV/course_descriptions.csv"
COURSE_DATA = "./data/Courses"
PREPROCESSED_COURSE_DATA = "./data/preprocessed_data/Courses"

# Constants
CSV_KEYS = ["Course ID", "Subject", "Catalog", "Long Title"]
DESCRIPTION_PLACEHOLDERS = [
    "Please see Graduate Calendar", "Please see GRAD Calendar", "Please see UGRD Calendar", "Please see Undergraduate Calendar"
]
LECTURE_KEYS = ["Slides", "Worksheets",
                "Readings", "Labs", "Tutorials"]

# Hardcoded University dbpedia reference
CONCORDIA_UNIVERSITY_DBPEDIA_URL = "https://dbpedia.org/resource/Concordia_University"

# Hardcoded course urls
COURSE_URLS = {
    "COMP_474": "http://concordia.catalog.acalog.com/preview_course_nopop.php?catoid=1&coid=2718",
    "COMP_445": "http://concordia.catalog.acalog.com/preview_course_nopop.php?catoid=1&coid=2713"
}
