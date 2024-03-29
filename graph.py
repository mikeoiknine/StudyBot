import urllib.request
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS

from course_parser import parse_courses, parse_local_courses
from constants import CONCORDIA_UNIVERSITY_DBPEDIA_URL, COURSE_URLS

FOCU = Namespace("http://focu.io/schema#")
FOCUDATA = Namespace("http://focu.io/data#")
DBO = Namespace("http://dbpedia.org/ontology/")
DBP = Namespace("http://dbpedia.org/property/")
DCE = Namespace("http://purl.org/dc/elements/1.1/")
VIVO = Namespace("http://vivoweb.org/ontology/core#")
dbr = "http://dbpedia.org/resource/"

def build_graph():
    """
    Builds and returns the graph representing the entire Knowledge Base
    """
    g = Graph()

    # Bind namespaces
    g.bind("focu", FOCU)
    g.bind("dbp", DBP)
    g.bind("dce", DCE)
    g.bind("dbo", DBO)
    g.bind("vivo", VIVO)

    # Add Concordia to the graph
    g.add((FOCUDATA.Concordia_University, RDF.type, DBO.University))
    g.add((FOCUDATA.Concordia_University, DBP.name, Literal("Concordia University")))
    g.add((FOCUDATA.Concordia_University, RDFS.seeAlso,
          URIRef(CONCORDIA_UNIVERSITY_DBPEDIA_URL)))

    # Add general courses to the graph
    general_courses = build_general_course_graph()
    g += general_courses

    # Create link between Concordia and each of the courses
    for s, _, _ in general_courses.triples((None, RDF.type, VIVO.Course)):
        g.add((FOCUDATA.Concordia_University, FOCU.courses, s))

    # Add local courses to the graph
    g += build_local_course_graph()

    return g


def build_general_course_graph():
    """
    Builds and returns the graph representing all of the courses of Concordia
    University which were parsed from the CSV files.
    """
    g = Graph()
    for raw_course in parse_courses():
        course_subject = raw_course.get("Subject", None)
        course_number = raw_course.get("Catalog", None)
        if course_subject is None or course_number is None:
            continue

        # Add course to graph
        course = URIRef(FOCUDATA + f"{course_subject.upper()}_{course_number}")
        g.add((course, RDF.type, VIVO.Course))

        # Course subject
        g.add((course, DCE.subject, Literal(course_subject)))

        # Course number
        g.add((course, DBP.number, Literal(course_number)))

        # Course name
        course_name = raw_course.get("Long Title", None)
        if course_name is not None:
            g.add((course, DBP.name, Literal(course_name)))

        # Course Description
        course_descr = raw_course.get("Description", None)
        if course_descr is not None:
            g.add((course, DCE.description, Literal(course_descr)))

    return g


def build_local_course_graph():
    """
    Builds and returns the graph representing the detailed Courses
    found in the data/Courses directory.
    """
    g = Graph()
    for raw_course in parse_local_courses():
        course_subject = raw_course.get("Subject", None)
        course_number = raw_course.get("Number", None)
        if course_subject is None or course_number is None:
            continue

        # Add course to graph
        short_name = f"{course_subject.upper()}_{course_number}"
        course = URIRef(FOCUDATA + short_name)
        g.add((course, RDF.type, VIVO.Course))
        g.add((course, DBP.number, Literal(course_number)))

        # Add course URL if its in the known urls
        if short_name in COURSE_URLS:
            g.add((course, RDFS.seeAlso, URIRef(COURSE_URLS[short_name])))

        # Add course outline
        add_uris_to_graph(g, course, FOCU.outlines,
                          raw_course.get("Outlines", None))

        # Add lectures to graph
        raw_lectures = raw_course.get("Lectures", None)
        if raw_lectures is not None:
            course_lectures = build_lecture_graph(raw_lectures, short_name)
            g += course_lectures

            # Create link from this course to each of its lectures
            for s, _, _ in course_lectures.triples((None, RDF.type, FOCU.Lecture)):
                g.add((course, FOCU.lectures, s))
    return g


def build_lecture_graph(lectures, course_name):
    """
    Builds and returns the graph representing the detailed Lectures
    found in the data/Courses/*/Lectures sub-directory.
    """
    g = Graph()

    for raw_lecture in lectures:
        lecture_name = raw_lecture.get("Name", None)
        lecture_number = raw_lecture.get("Number", None)

        if lecture_name is None or lecture_number is None:
            continue

        # Add lecture to graph
        lecture = URIRef(
            FOCUDATA + f"{lecture_name}")
        g.add((lecture, RDF.type, FOCU.Lecture))
        g.add((lecture, DBP.name, Literal(lecture_name)))
        g.add((lecture, DBP.number, Literal(lecture_number)))

        # Add lecture slides
        add_uris_to_graph(g, lecture, FOCU.slides,
                          raw_lecture.get("Slides", None))

        # Add lecture worksheets
        add_uris_to_graph(g, lecture, FOCU.worksheets,
                          raw_lecture.get("Worksheets", None))

        # Add lecture readings
        add_uris_to_graph(g, lecture, FOCU.readings,
                          raw_lecture.get("Readings", None))

        # Add Labs associated to this lecture
        lab_ref = add_course_event_to_graph(g, course_name, lecture_number, "Lab",
                                            FOCU.Lab, raw_lecture.get("Labs", None))
        if lab_ref:
            g.add((lecture, FOCU.labs, lab_ref))

        # Add Tutorials associated to this lecture
        tut_ref = add_course_event_to_graph(g, course_name, lecture_number, "Tutorial",
                                            FOCU.Tutorial, raw_lecture.get("Tutorials", None))
        if tut_ref:
            g.add((lecture, FOCU.tutorials, tut_ref))

    return g


def add_course_event_to_graph(g, course_name, lecture_number, name, obj, paths):
    if paths is None:
        return

    event_name = f"{course_name}_{name}_{lecture_number}"
    event_ref = URIRef(FOCUDATA + event_name)
    g.add((event_ref, RDF.type, obj))

    added_uris = add_uris_to_graph(g, event_ref, FOCU.worksheets, paths)
    if not added_uris:
        g.remove((event_ref, RDF.type, obj))
        return None

    return event_ref


def add_uris_to_graph(g, subject, predicate, file_dicts):
    """
    Converts all the given file_dicts to locally resolvable URIs and adds them
    as objects to the graph, g, with the given subject and predicate
    """
    if file_dicts is None or not file_dicts:
        return []

    uris = []
    for dict in file_dicts:
        docURI = URIRef(f"file:{urllib.request.pathname2url(dict['file_path'])}")
        g.add((docURI, RDF.type, DBO.document))

        # add each topic in the db and link to doc
        for annotation in dict.get('annotations', {}).get('Annotation',{}).get('Resources',{}).get('Resource',{}): #conditional chaining
            topicName = annotation['@URI'].replace(dbr, '') # get name from dbpedia resource
            topicURI = URIRef(FOCUDATA + topicName)
            g.add((topicURI, RDF.type, FOCU.Topic))
            g.add((topicURI, DBP.name, Literal(annotation['@surfaceForm'].lower())))
            g.add((topicURI, RDFS.seeAlso, URIRef(annotation['@URI'])))
            g.add((docURI, FOCU.topics, topicURI))

        g.add((subject, predicate, docURI))
        uris.append(docURI)
    return uris
