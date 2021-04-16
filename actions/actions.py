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