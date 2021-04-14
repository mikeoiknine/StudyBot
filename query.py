from rdflib import Graph, Namespace, URIRef
from rdflib.plugins.sparql import prepareQuery

FOCU = Namespace("http://focu.io/schema#")
FOCUDATA = Namespace("http://focu.io/data#")
DBO = Namespace("http://dbpedia.org/ontology/")
DBP = Namespace("http://dbpedia.org/property/")
DCE = Namespace("http://purl.org/dc/elements/1.1/")
VIVO = Namespace("http://vivoweb.org/ontology/core#")

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