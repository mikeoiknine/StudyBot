import requests
import json

from constants import FUSEKI_BASE_URL

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.plugins.sparql import prepareQuery

namespaces = (
    "PREFIX focu: <http://focu.io/schema#>"
    "PREFIX focudata: <http://focu.io/data#>"
    "PREFIX dbo: <http://dbpedia.org/ontology/>"
    "PREFIX dbp: <http://dbpedia.org/property/>"
    "PREFIX dce: <http://purl.org/dc/elements/1.1/>"
    "PREFIX vivo: <http://vivoweb.org/ontology/core#>"
    "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"
    "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns>"
)

FOCUDATA = Namespace("http://focu.io/data#")


def make_query(query):
    try:
        rows = requests.get(FUSEKI_BASE_URL, params={'query': query})
        rows.raise_for_status()

        return rows
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def extract_bindings(query_result):
    results = query_result.get("results", None)
    if results is None:
        return None

    bindings = results.get("bindings", None)
    if bindings is None or not bindings:
        return None

    return bindings


def get_course_description(course):
    """
    Query the graph for the name and description the course
    """

    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    q = f"SELECT ?name ?description WHERE {{ <{course}> a vivo:Course; dbp:name ?name; dce:description ?description. }}"

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    bindings = bindings[0]
    course_name = bindings.get("name", None)
    course_descr = bindings.get("description", None)

    if course_name is None or course_descr is None:
        return None

    return course_name.get("value", None), course_descr.get("value", None)


def get_lecture_count(course):
    """
    Return the amount of lectures associated with the given course in the graph
    """

    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    q = f"SELECT (COUNT(?lecture) as ?lecture_cnt) WHERE {{ <{course}> focu:lectures ?lecture. }}"

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    bindings = bindings[0]
    lecture_count = bindings.get("lecture_cnt", None)
    if lecture_count is None:
        return None

    return lecture_count.get("value", None)


def get_lab_count(course):
    """
    Return the amount of labs associated with the given course in the graph
    """

    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    q = f"SELECT (COUNT(?labs) as ?lab_cnt) WHERE {{ <{course}> focu:lectures ?lectures. OPTIONAL {{ ?lectures focu:labs ?labs }}. }}"

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    bindings = bindings[0]
    lab_count = bindings.get("lab_cnt", None)
    if lab_count is None:
        return None

    return lab_count.get("value", None)


def get_tutorial_count(course):
    """
    Return the amount of tutorials associated with the given course in the graph
    """

    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    q = f"SELECT (COUNT(?tutorials) as ?tutorial_cnt) WHERE {{ <{course}> focu:lectures ?lectures. OPTIONAL {{ ?lectures focu:tutorials ?tutorials }}. }}"

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    bindings = bindings[0]
    tutorial_count = bindings.get("tutorial_cnt", None)
    if tutorial_count is None:
        return None

    return tutorial_count.get("value", None)


def get_course_topics(course):
    """
    Query the graph for all of the topics associated to a given course
    """

    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    q = """ SELECT DISTINCT ?topics ?urls
            WHERE {{
                <{course}> a vivo:Course; focu:lectures ?lectures.
                {{
                    {{
                        ?lectures focu:worksheets ?docs.
                        ?doc focu:topics ?topics.
                    }} UNION {{
                        ?lectures focu:slides ?docs.
                        ?doc focu:topics ?topics.
                    }} UNION {{
                        ?lectures focu:readings ?docs.
                        ?doc focu:topics ?topics.
                    }}
                }} UNION {{
                    ?lectures focu:labs ?labs.
                    {{
                        ?labs focu:worksheets ?docs.
                        ?doc focu:topics ?topics.
                    }} UNION {{
                        ?labs focu:slides ?docs.
                        ?doc focu:topics ?topics.
                    }} UNION {{
                        ?labs focu:readings ?docs.
                        ?doc focu:topics ?topics.
                    }}
                }} UNION {{
                    ?lectures focu:tutorials ?tutorials.
                    {{
                        ?tutorials focu:worksheets ?docs.
                        ?doc focu:topics ?topics.
                    }} UNION {{
                        ?tutorials focu:slides ?docs.
                        ?doc focu:topics ?topics.
                    }} UNION {{
                        ?tutorials focu:readings ?docs.
                        ?doc focu:topics ?topics.
                    }}
                }}
                ?topics rdfs:seeAlso ?urls.
            }}
        """.format(course=course)

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    topics = []
    for row in bindings:
        topic = row.get("topics", None)
        links = row.get("urls", None)
        if topic is None or links is None:
            continue

        topic = topic.get("value", None)
        links = links.get("value", None)
        if topic is None or links is None:
            continue

        topics.append((topic, links))
    return topics


def get_courses_covering_topic(topicname):
    """
    Query the graph for all courses that cover a given topic, by checking if their documents contain the topic
    """

    q = """ SELECT ?coursesubject ?coursenumber ?coursename (COUNT(?doc) as ?doccount)
            WHERE {{
                ?course a vivo:Course;
                        dce:subject ?coursesubject;
                        dbp:number ?coursenumber;
                        dbp:name ?coursename;
                        focu:lectures ?lectures.
                {{
                    {{
                        ?lectures focu:worksheets ?doc.
                        ?doc focu:topics ?topic.
                    }} UNION {{
                        ?lectures focu:slides ?doc.
                        ?doc focu:topics ?topic.
                    }} UNION {{
                        ?lectures focu:readings ?doc.
                        ?doc focu:topics ?topic.
                    }}
                }} UNION {{
                    ?lectures focu:labs ?labs.
                    {{
                        ?labs focu:worksheets ?doc.
                        ?doc focu:topics ?topic.
                    }} UNION {{
                        ?labs focu:slides ?doc.
                        ?doc focu:topics ?topic.
                    }} UNION {{
                        ?labs focu:readings ?doc.
                        ?doc focu:topics ?topic.
                    }}
                }} UNION {{
                    ?lectures focu:tutorials ?tutorials.
                    {{
                        ?tutorials focu:worksheets ?doc.
                        ?doc focu:topics ?topic.
                    }} UNION {{
                        ?tutorials focu:slides ?doc.
                        ?doc focu:topics ?topic.
                    }} UNION {{
                        ?tutorials focu:readings ?doc.
                        ?doc focu:topics ?topic.
                    }}
                }}
                ?topic dbp:name "{topicname}".
            }} GROUP BY ?course ?coursesubject ?coursename ?coursenumber
            ORDER BY DESC(?doccount)
        """.format(topicname=topicname.lower())

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    courses = []
    for row in bindings:
        course_subject = row.get("coursesubject", None)
        course_number = row.get("coursenumber", None)
        course_name = row.get("coursename", None)
        doc_count = row.get("doccount", None)

        if not all([course_subject, course_number, course_name, doc_count]):
            continue

        course_subject = course_subject.get("value", None)
        course_number = course_number.get("value", None)
        course_name = course_name.get("value", None)
        doc_count = doc_count.get("value", None)

        if not all([course_subject, course_number, course_name, doc_count]):
            continue
        courses.append((course_subject, course_number, course_name, doc_count))

    return courses


def get_slides_covering_topic(topicname):
    """
    Query the graph for slides of lectures covering a given topic
    """

    q = """ SELECT ?slides
            WHERE {{
                ?lecture a focu:Lecture;
                         focu:slides ?slides.
                ?slides focu:topics ?topic.
                ?topic dbp:name "{topicname}".
            }}
        """.format(topicname=topicname.lower())

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    slidesets = []
    for row in bindings:
        slides = row.get("slides", None)
        if slides is None:
            continue

        slides = slides.get("value", None)
        if slides is None:
            continue

        slidesets.append(slides)

    return slidesets


def get_courses_without_slides():
    """
    Query the graph for course which have no lecture slides
    """

    q = """ SELECT DISTINCT ?course
            WHERE {
                ?course a vivo:Course.
                OPTIONAL {
                    ?course focu:lectures ?lectures .
                    ?lectures focu:slides ?slides .
                }
                FILTER (!BOUND(?slides))
            }
        """

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    courses = []
    for row in bindings:
        course = row.get("course", None)
        if course is None:
            continue

        course = course.get("value", None)
        if course is None:
            continue

        courses.append(course)

    return courses


def get_courses_covering_topic_at_university(topicname, university):
    """
    Query the graph for courses covering the given topic at the given University
    """

    q = """ SELECT ?coursesubject ?coursenumber ?coursename
            WHERE {{
                ?uni a dbo:University;
                    dbp:name "{uniname}";
                    focu:courses ?course.
                ?course a vivo:Course;
                        dce:subject ?coursesubject;
                        dbp:number ?coursenumber;
                        dbp:name ?coursename;
                        focu:lectures ?lectures.
                ?topic a focu:Topic;
                        dbp:name "{topic_name}".
                {{
                    {{
                        ?lectures focu:worksheets ?doc.
                        ?doc focu:topics ?topic.
                    }} UNION {{
                        ?lectures focu:slides ?doc.
                        ?doc focu:topics ?topic.
                    }} UNION {{
                        ?lectures focu:readings ?doc.
                        ?doc focu:topics ?topic.
                    }}
                }} UNION {{
                    ?lectures focu:labs ?labs.
                    {{
                        ?labs focu:worksheets ?doc.
                        ?doc focu:topics ?topic.
                    }} UNION {{
                        ?labs focu:slides ?doc.
                        ?doc focu:topics ?topic.
                    }} UNION {{
                        ?labs focu:readings ?doc.
                        ?doc focu:topics ?topic.
                    }}
                }} UNION {{
                    ?lectures focu:tutorials ?tutorials.
                    {{
                        ?tutorials focu:worksheets ?doc.
                        ?doc focu:topics ?topic.
                    }} UNION {{
                        ?tutorials focu:slides ?doc.
                        ?doc focu:topics ?topic.
                    }} UNION {{
                        ?tutorials focu:readings ?doc.
                        ?doc focu:topics ?topic.
                    }}
                }}
             }}
            GROUP BY ?coursesubject ?coursenumber ?coursename
        """.format(uniname=university.lower(), topic_name=topicname.lower())

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    courses = []
    for row in bindings:
        course_subject = row.get("coursesubject", None)
        course_number = row.get("coursenumber", None)
        course_name = row.get("coursename", None)

        if not all([course_subject, course_number, course_name]):
            continue

        course_subject = course_subject.get("value", None)
        course_number = course_number.get("value", None)
        course_name = course_name.get("value", None)

        if not all([course_subject, course_number, course_name]):
            continue
        courses.append((course_subject, course_number, course_name))
    return courses


def get_courses_offered_at_university(university):
    """
    Query the graph for courses offered by given university
    """

    q = """ SELECT DISTINCT ?course
            WHERE {{
                ?course a vivo:Course.
                ?uni focu:courses ?course;
                     dbp:name "{uniname}".
            }}
        """.format(uniname=university.lower())

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    courses = []
    for row in bindings:
        course = row.get("course", None)
        if course is None:
            continue

        course = course.get("value", None)
        if course is None:
            continue
        courses.append(course)

    return courses


def get_courses_with_labs():
    """
    Query the graph for courses which have a lab component
    """

    q = """ SELECT DISTINCT ?course
            WHERE {
                ?course a vivo:Course;
                        focu:lectures ?lectures .
                ?lectures focu:labs ?labs.
            }
        """

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    courses = []
    for row in bindings:
        course = row.get("course", None)
        if course is None:
            continue

        course = course.get("value", None)
        if course is None:
            continue

        courses.append(course)

    return courses


def get_topics_covered_in_lecture(course, lecture_number):
    """
    Query the graph for the topics covered in a given lecture for a given course
    """
    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    q = """ SELECT ?lecture ?topics ?docs
            WHERE {{
                <{course}> a vivo:Course;
                           focu:lectures ?lecture.
                ?lecture a focu:Lecture;
                        dbp:number "{lecture_number}".
                {{
                    ?lecture focu:slides ?docs.
                    ?docs focu:topics ?topics.
                }} UNION {{
                    ?lecture focu:worksheets ?docs.
                    ?docs focu:topics ?topics.
                }} UNION {{
                    ?lecture focu:readings ?docs.
                    ?docs focu:topics ?topics.
                }}
            }}
        """.format(course=course, lecture_number=lecture_number)

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    lecture_topics = []
    for row in bindings:
        lecture = row.get("lecture", None)
        topic = row.get("topics", None)
        resource = row.get("docs", None)

        if not all([lecture, topic, resource]):
            continue

        lecture = lecture.get("value", None)
        topic = topic.get("value", None)
        resource = resource.get("value", None)

        if not all([lecture, topic, resource]):
            continue

        lecture_topics.append((lecture, topic, resource))

    return lecture_topics


def get_topics_covered_in_tutorial(course, tutorial_number):
    """
    Query the graph for the topics covered in a given tutorial for a given course
    """
    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    q = """ SELECT ?tutorial ?topics ?docs
            WHERE {{
                <{course}> a vivo:Course;
                           focu:lectures ?lecture.
                ?lecture a focu:Lecture;
                        dbp:number "{tutorial_number}";
                        focu:tutorials ?tutorial.
                ?tutorial focu:worksheets ?docs.
                ?docs focu:topics ?topics.
            }}
        """.format(course=course, tutorial_number=tutorial_number)

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    tutorial_topics = []
    for row in bindings:
        tutorial = row.get("tutorial", None)
        topic = row.get("topics", None)
        resource = row.get("docs", None)

        if not all([tutorial, topic, resource]):
            continue

        tutorial = tutorial.get("value", None)
        topic = topic.get("value", None)
        resource = resource.get("value", None)

        if not all([tutorial, topic, resource]):
            continue

        tutorial_topics.append((tutorial, topic, resource))

    return tutorial_topics


def get_topics_covered_in_lab(course, lab_number):
    """
    Query the graph for the topics covered in a given lab for a given course
    """

    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    q = """ SELECT ?lab ?topics ?docs
            WHERE {{
                <{course}> a vivo:Course;
                           focu:lectures ?lecture.
                ?lecture a focu:Lecture;
                        dbp:number "{lab_number}";
                        focu:labs ?lab.
                ?lab focu:worksheets ?docs.
                ?docs focu:topics ?topics.
            }}
        """.format(course=course, lab_number=lab_number)

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    lab_topics = []
    for row in bindings:
        lab = row.get("lab", None)
        topic = row.get("topics", None)
        resource = row.get("docs", None)

        if not all([lab, topic, resource]):
            continue

        lab = lab.get("value", None)
        topic = topic.get("value", None)
        resource = resource.get("value", None)

        if not all([lab, topic, resource]):
            continue

        lab_topics.append((lab, topic, resource))

    return lab_topics


def get_courses_by_level_at_university(level, university):
    """
    Query the graph for courses matching a given course level at a given university
    """

    level_number = level[0]

    q = """ SELECT ?course
            WHERE {{
                ?university a dbo:University;
                            dbp:name "{university}";
                            focu:courses ?course.
                ?course dbp:number ?courseNumber .
                FILTER(STRSTARTS(?courseNumber, "{levelnumber}")) .
            }}
        """.format(university=university.lower(), levelnumber=level_number)

    rows = make_query(namespaces + q)
    if rows is None:
        return None

    bindings = extract_bindings(rows.json())
    if bindings is None:
        return None

    courses = []
    for row in bindings:
        course = row.get("course", None)
        if course is None:
            continue

        course = course.get("value", None)
        if course is None:
            continue

        courses.append(course)

    return courses
