from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.plugins.sparql import prepareQuery

FOCU = Namespace("http://focu.io/schema#")
FOCUDATA = Namespace("http://focu.io/data#")
DBO = Namespace("http://dbpedia.org/ontology/")
DBP = Namespace("http://dbpedia.org/property/")
DCE = Namespace("http://purl.org/dc/elements/1.1/")
VIVO = Namespace("http://vivoweb.org/ontology/core#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")


def get_course_description(graph, course):
    """
    Query the graph for the name and description the course
    """

    q = prepareQuery(
        "SELECT ?name ?description WHERE { ?course a vivo:Course; dbp:name ?name; dce:description ?description. }",
        initNs={
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
        initNs={
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


def get_lab_count(graph, course):
    """
    Return the amount of labs associated with the given course in the graph
    """

    q = prepareQuery(
        "SELECT (COUNT(?labs) as ?lab_cnt) WHERE { ?course focu:lectures ?lectures. OPTIONAL { ?lectures focu:labs ?labs }. }",
        initNs={
            "focudata": FOCUDATA,
            "focu": FOCU
        }
    )

    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    rows = list(graph.query(q, initBindings={"course": course}))
    if rows is None or not rows:
        return None

    lab_count = rows[0].get("lab_cnt", None)
    return lab_count


def get_tutorial_count(graph, course):
    """
    Return the amount of tutorials associated with the given course in the graph
    """

    q = prepareQuery(
        "SELECT (COUNT(?tutorials) as ?tutorial_cnt) WHERE { ?course focu:lectures ?lectures. OPTIONAL { ?lectures focu:tutorials ?tutorials }. }",
        initNs={
            "focudata": FOCUDATA,
            "focu": FOCU
        }
    )

    course = URIRef(FOCUDATA + f"{'_'.join(course.split()).upper()}")
    rows = list(graph.query(q, initBindings={"course": course}))
    if rows is None or not rows:
        return None

    tutorial_count = rows[0].get("tutorial_cnt", None)
    return tutorial_count


def get_course_topics(graph, course):
    """
    Query the graph for all of the topics associated to a given course
    """

    q = prepareQuery(
        "SELECT ?topics ?urls WHERE { ?course a vivo:Course; focu:topics ?topics. ?topics rdfs:seeAlso ?urls.}",
        initNs={
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


def get_courses_covering_topic(graph, topicname):
    """
    Query the graph for all courses that cover a given topic, by checking if their documents contain the topic
    """

    print(topicname)

    q = prepareQuery(
        """
            SELECT ?course ?coursesubject ?coursenumber ?coursename (COUNT(?doc) as ?doccount) WHERE { 
            ?course a vivo:Course; 
                    dce:subject ?coursesubject;
                    dbp:number ?coursenumber;
                    dbp:name ?coursename;
                    focu:lectures ?lectures.
            { 
                { ?lectures focu:worksheets ?doc.
                ?doc focu:topics ?topic.
                } UNION
                { ?lectures focu:slides ?doc. 
                ?doc focu:topics ?topic.
                } UNION
                {
                ?lectures focu:readings ?doc.
                ?doc focu:topics ?topic.
                }
            } UNION
            { ?lecture focu:labs ?lab.
                { ?lab focu:worksheets ?doc.
                ?doc focu:topics ?topic.
                } UNION
                { ?lab focu:slides ?doc. 
                ?doc focu:topics ?topic.
                } UNION
                {
                ?lab focu:readings ?doc.
                ?doc focu:topics ?topic.
                }
            } UNION
            { ?lecture focu:tutorials ?tutorial.
                { ?tutorial focu:worksheets ?doc.
                ?doc focu:topics ?topic.
                } UNION
                { ?tutorial focu:slides ?doc. 
                ?doc focu:topics ?topic.
                } UNION
                {
                ?tutorial focu:readings ?doc.
                ?doc focu:topics ?topic.
                }
            }
            ?topic dbp:name ?topicname. 
            } GROUP BY ?course ?coursesubject ?coursename ?coursenumber
            ORDER BY DESC(?doccount)

        """,
        initNs={
            "focudata": FOCUDATA,
            "vivo": VIVO,
            "focu": FOCU,
            "rdfs": RDFS,
            "dce": DCE,
            "dbp": DBP
        }
    )
    print(q)
    rows = list(graph.query(q, initBindings={"topicname": Literal(topicname.lower())}))
    print(rows)
    if rows is None or not rows:
        return None

    courses = []
    for row in rows:
        course = row.get("course", None)
        coursesubject = row.get("coursesubject", None)
        coursenumber = row.get("coursenumber", None)
        coursename = row.get("coursename", None)
        doccount = row.get("doccount", None)

        if course is not None:
            courses.append((str(course), coursesubject, coursenumber, coursename, doccount))
    return courses


def slides_for_lectures_covering_topic(graph, topicname):
    """
    Query the graph for slides of lectures covering topic X
    """

    print(topicname)

    q = prepareQuery(
        """SELECT ?slides
            WHERE {
                ?lec rdf:type focu:Lecture.
                ?lec focu:slides ?slides .
                ?slides focu:topics ?topic.
                ?topic dbp:name ?topicname .
            }""",
        initNs={
            "focu": FOCU,
            "rdf": RDF,
            "dbp": DBP
        }
    )

    rows = list(graph.query(q, initBindings={"topicname": Literal(topicname.lower())}))
    if rows is None or not rows:
        return None

    slidesets = []
    for row in rows:
        slides = row.get("slides", None)
        if slides is not None:
            slidesets.append((str(slides)))
    return slidesets


def get_courses_no_lecture_slides(graph):
    """
    Query the graph for lectures without lecture slides
    """

    q = prepareQuery(
        """SELECT DISTINCT ?course
            WHERE {
                ?course a vivo:Course.
                OPTIONAL {
                ?course focu:lectures ?lectures .
                ?lectures focu:slides ?slides .
            }
            FILTER (!BOUND(?slides))
            }
            """,
        initNs={
            "vivo": VIVO,
            "focu": FOCU,
            "rdf": RDF,
            "dbp": DBP
        }
    )

    rows = list(graph.query(q))
    if rows is None or not rows:
        return None

    courses = []
    for row in rows:
        course = row.get("course", None)
        if course is not None:
            courses.append((str(course)))
    return courses


def courses_from_uni_covering_topic(graph, topicname, university):
    """
    Query the graph for slides of lectures covering topic X
    """

    print(topicname)
    print(university)

    q = prepareQuery(
        """SELECT ?course ?coursesubject ?coursenumber ?coursename 
        WHERE {{ 
                ?course a vivo:Course; 
                        dce:subject ?coursesubject;
                        dbp:number ?coursenumber;
                        dbp:name ?coursename;
                        focu:topics ?topic.
                ?topic a focu:Topic;
                        dbp:name "{topic_name}".
                ?uni a dbo:University;
                    dbp:name "{uniname}";
                    focu:courses ?course.
             }}
            GROUP BY ?course ?coursesubject ?coursenumber ?coursename
        """.format(uniname=university, topic_name=topicname),
        initNs={
            "focu": FOCU,
            "rdf": RDF,
            "dbp": DBP,
            "dbo": DBO,
            "vivo": VIVO,
            "dce": DCE
        }
    )

    rows = list(graph.query(q, initBindings={
        "topicname": Literal(topicname.lower()),
        "uniname": Literal(university.lower())
    }))
    print(list(rows))
    if rows is None or not rows:
        return None

    courses = []
    for row in rows:
        course = row.get("course", None)
        coursesubject = row.get("coursesubject", None)
        coursenumber = row.get("coursenumber", None)
        coursename = row.get("coursename", None)

        if course is not None:
            courses.append((str(course), coursesubject, coursenumber, coursename))
    return courses
