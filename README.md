

# COMP 474/6741 Intelligent Systems (Winter 2021)

The overall goal of this project is to build Studybot, an intelligent agent that can
answer university course-related questions using a knowledge graph and natural language
processing. For example, Studybot will be able to answer questions such as, “What is course COMP 474 about?”, “Which topics were covered in the second lecture in COMP474?” and “Which courses at Concordia teach deep learning?”


<u>Project structure.</u> 

This first assignment primarily focuses on constructing the knowledge base, whereas the second part will target some enhancements, the natural language processing interface, as well as the overall integration.


<u>Studybot’s Knowledge Graph Vocabulary.</u>

To be able to answer questions, Studybot needs knowledge about courses, lectures, and their content. Thus, the first step in this part of the project is the construction of a knowledge graph, built using standard W3C technologies, in particular RDF and RDFS. You have to model your graph to represent at least the information below (you can add more information that you find useful):


### Universities.  - ***Information about universities:***
1. Name of the university
2. Link to the university’s entry in DBpedia and/or Wikidata

### Courses. - ***Information about courses offered at a university, including:***
1. Course name (e.g., “Intelligent Systems”)
2. Course subject (e.g., “COMP”, “SOEN”)
3. Course number (e.g., “474”)
4. Course description (e.g., “Knowledge representation and reasoning. Uncertainty and conflict resolution . . . ”)
5. A link (rdfs:seeAlso) to a web page with the course information, if available.
6. Course outline, if available.


### Lectures. - ***Information about lectures in a course, including:***
1. Lecture number (sequential count)
2. Lecture name, if available (e.g., “Knowledge Graphs”)
3. Lecture content, such as:
    * Slides
    *  Worksheets
    * Readings (book chapters, web pages, etc.)
    * Other material (videos, images, etc.)
4. A link (rdfs:seeAlso) to a web page with the lecture information, if available


### Labs/tutorials. - ***Information about lecture-related events, such as labs or tutorials.***
They can have the same information as lectures. Additionally, each lab/tutorial is associated with a specific lecture.


### Topics.  - ***Information about the topics that are covered in a course (like the course description) or a lecture in a course (for example, on a slide)***. 

A topic must be linked to either DBpedia and/or Wikidata. For example, the topic “Expert system” in a course description would be linked to http://dbpedia.org/resource/Expert system.

