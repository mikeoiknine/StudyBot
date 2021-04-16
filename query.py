from rdflib import Graph, Namespace, URIRef
from rdflib.plugins.sparql import prepareQuery

FOCU = Namespace("http://focu.io/schema#")
FOCUDATA = Namespace("http://focu.io/data#")
DBO = Namespace("http://dbpedia.org/ontology/")
DBP = Namespace("http://dbpedia.org/property/")
DCE = Namespace("http://purl.org/dc/elements/1.1/")
VIVO = Namespace("http://vivoweb.org/ontology/core#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

def get_course_description(graph, course):
    """
    Query the graph for the name and description the course
    """
    
    q = prepareQuery(
        "SELECT ?name ?description WHERE { ?course a vivo:Course; dbp:name ?name; dce:description ?description. }",
        initNs = {
            "focudata": FOCUDATA,
            "vivo": VIVO,
            "dbp": DBP,
            "dce": DCE
        }
    )

    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    rows = list(graph.query(q, initBindings={"course": course}))
    if rows is None or not rows:
        return None 

    course_descr = rows[0].get("description", None)
    course_name = rows[0].get("name", None)
    if course_descr is None or course_name is None:
        return None 

    return str(course_name), str(course_descr)

def get_lecture_count(graph, course):
    """
    Return the amount of lectures associated with the given course in the graph
    """

    q = prepareQuery(
        "SELECT (COUNT(?lecture) as ?lecture_cnt) WHERE { ?course focu:lectures ?lecture. }",
        initNs = {
            "focudata": FOCUDATA,
            "focu": FOCU
        }
    )

    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    rows = list(graph.query(q, initBindings={"course": course}))
    if rows is None or not rows:
        return None 

    lecture_count = rows[0].get("lecture_cnt", None)
    return lecture_count
    

def get_course_topics(graph, course):
    """
    Query the graph for all of the topics associated to a given course
    """

    q = prepareQuery(
        "SELECT ?topics ?urls WHERE { ?course a vivo:Course; focu:topics ?topics. ?topics rdfs:seeAlso ?urls.}",
        initNs = {
            "focudata": FOCUDATA,
            "vivo": VIVO,
            "focu": FOCU,
            "rdfs": RDFS
        }
    )

    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    rows = list(graph.query(q, initBindings={"course": course}))
    if rows is None or not rows:
        return None 

    topics = []
    for row in rows:
        topic = row.get("topics", None)
        link = row.get("urls", None)
        if topic is not None and link is not None:
            topics.append((str(topic), link))
    return topics