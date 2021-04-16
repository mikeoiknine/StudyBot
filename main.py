import time
import query

from rdflib import Graph
from graph import build_graph

def generate_graph():
    print("Building graph...")
    start_time = time.time()
    g = build_graph()
    print("Done, took:", (time.time() - start_time), "seconds")
    return g

def fetch_or_build_graph():
    graph = Graph()
    graph.parse("Graph.nt", format="ntriples")

    if graph is None:
        graph = generate_graph()
        graph += generate_mock_topic_triples()

        graph.serialize(destination="Graph.nt", format="ntriples")

    return graph


def generate_mock_topic_triples():
    """
    Since topics aren't being parsed for the first part of the project,
    we simply add some mock topics to the graph for now.
    """
    from rdflib import Graph, URIRef, Namespace, Literal
    from rdflib.namespace import RDF, RDFS
    FOCU = Namespace("http://focu.io/schema#")
    FOCUDATA = Namespace("http://focu.io/data#")
    DBP = Namespace("http://dbpedia.org/property/")

    g = Graph()

    # Add topic
    topic = URIRef(FOCUDATA + "Knowledge_Graph")
    g.add((topic, RDF.type, FOCU.Topic))
    g.add((topic, DBP.name, Literal("Knowledge Graph")))
    g.add((topic, RDFS.seeAlso, URIRef(
        "https://dbpedia.org/resource/Knowledge_Graph")))

    # Add relationship between course and topic
    comp_474 = URIRef(FOCUDATA + "COMP_474")
    g.add((comp_474, FOCU.topics, topic))

    # Add relationship between specific lecture and topic
    lecture_knowledge_graphs = URIRef(FOCUDATA + "Knowledge_Graphs")
    g.add((lecture_knowledge_graphs, FOCU.topics, topic))

    return g


if __name__ == "__main__":
    graph = fetch_or_build_graph()
    # print(query.get_lecture_count(graph, "Comp 474"))
    print(query.get_course_topics(graph, "Comp 474"))
    # graph = generate_graph()
    # graph += generate_mock_topic_triples()

    # graph.serialize(destination="Graph.nt", format="ntriples")
