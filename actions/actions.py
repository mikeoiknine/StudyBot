# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import query
from main import fetch_or_build_graph

graph = fetch_or_build_graph()

class ActionCourseInfo(Action):

    def name(self) -> Text:
        return "action_course_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course = tracker.slots['course']
        if course is None:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []

        course_name, course_description = query.get_course_description(graph, course)
        if course_description is None or course_name is None:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find a description for {course}")
            return []
        
        dispatcher.utter_message(text=f"Here's what I found about {course} - {course_name}:\n{course_description}")
        return []


class ActionCourseTopicsCovered(Action):

    def name(self) -> Text:
        return "action_course_topics_covered"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        course = tracker.slots['course']
        if course is None:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []
        
        topics = query.get_course_topics(graph, course)
        if topics is None or not topics:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any topics covered in {course}")
            return []

        message = f"The topic{'s' if len(topics) > 1 else ''} covered by {course} {'are' if len(topics) > 1 else 'is'}:\n"
        for topic in topics:
            t, link = topic
            message += f"* {t.split('#')[1]} - ({link})\n"
    
        dispatcher.utter_message(text=message)
        return []

class ActionTopicsCoveredInCourse(Action):

    def name(self) -> Text:
        return "action_topic_which_courses"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        topic = tracker.slots['topic']
        if topic is None:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []
        
        courses = query.get_courses_covering_topic(graph, topic)
        if courses is None or not courses:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any courses that cover {topic}")
            return []

        message = f"The following courses{'s' if len(courses) > 1 else ''} {'cover' if len(courses) > 1 else 'covers'} the topic {topic}:\n"
        for course in courses:
            courseuri, coursesubject, coursenumber, coursename, doccount = course
            message += f"* {courseuri.split('#')[1]} - {coursesubject} {coursenumber} {coursename} COUNT: {doccount}\n"
    
        dispatcher.utter_message(text=message)
        return []

class ActionTopicsCoveredInSlides(Action):

    def name(self) -> Text:
        return "action_topic_which_slides"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        topic = tracker.slots['topic']
        if topic is None:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []
        
        slides = query.slides_for_lectures_covering_topic(graph, topic)
        if slides is None or not slides:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any slides that cover {topic}")
            return []

        message = f"The following slides{'s' if len(slides) > 1 else ''} {'cover' if len(slides) > 1 else 'covers'} the topic {topic}:\n"
        for slide in slides:
            message += f"* {slide}\n"
    
        dispatcher.utter_message(text=message)
        return []

class ActionCoursesNoLectureSlides(Action):

    def name(self) -> Text:
        return "action_courses_no_lecture_slides"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        courses = query.get_courses_no_lecture_slides(graph)
        if courses is None or not courses:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any courses that don't have lecture slides")
            return []

        message = f"The following courses{'s' if len(courses) > 1 else ''} {'cover' if len(courses) > 1 else 'covers'} have no lecture slides:\n"
        for course in courses:
            courseuri = course
            message += f"* {courseuri.split('#')[1]}, "
    
        dispatcher.utter_message(text=message)
        return []

class ActionCoursesFromUniCoveringTopic(Action):

    def name(self) -> Text:
        return "action_courses_from_uni_covering_topic"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        topic = tracker.slots['topic']
        university = tracker.slots['university']
        if topic is None or university is None:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []
        
        courses = query.courses_from_uni_covering_topic(graph, topic, university)
        if courses is None or not courses:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any courses that cover {topic} at {university}")
            return []

        message = f"The following courses{'s' if len(courses) > 1 else ''} {'cover' if len(courses) > 1 else 'covers'} the topic {topic} at {university}:\n"
        for course in courses:
            courseuri, coursesubject, coursenumber, coursename = course
            message += f"* {courseuri.split('#')[1]} - {coursesubject} {coursenumber} {coursename}\n"
    
        dispatcher.utter_message(text=message)
        return []
