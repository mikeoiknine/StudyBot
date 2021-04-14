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
