# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import query


class ActionCourseInfo(Action):

    def name(self) -> Text:
        return "action_course_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course = tracker.slots['course']
        if course is None or not course:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []

        res = query.get_course_description(course)
        if res is None or res[0] is None or res[1] is None:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find a description for {course}")
            return []

        name, description = res
        dispatcher.utter_message(text=f"Here's what I found about {course} - {name}:\n{description}")
        return []


class ActionCourseEventCount(Action):

    def name(self) -> Text:
        return "action_course_event_count"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course = tracker.slots['course']
        event_type = tracker.slots['event_type']
        if course is None or event_type is None:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []

        event_type = event_type.lower().strip()
        if event_type in set(['lectures', 'lecture', 'lec', 'lecs']):
            event_type = 'lectures'
            count = query.get_lecture_count(course)
        elif event_type in set(['labs', 'lab', 'laboratories', 'laboratory']):
            event_type = 'labs'
            count = query.get_lab_count(course)
        elif event_type in set(['tutorials', 'tutorial', 'tut', 'tuts']):
            event_type = 'tutorials'
            count = query.get_tutorial_count(course)

        if count is None:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find how many {event_type} there are in {course}")
            return []

        dispatcher.utter_message(text=f"There are {count} {event_type} in {course}")
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

        topics = query.get_course_topics(course)
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

        courses = query.get_courses_covering_topic(topic)
        if courses is None or not courses:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any courses that cover {topic}")
            return []

        message = f"The following course{'s' if len(courses) > 1 else ''} {'cover' if len(courses) > 1 else 'covers'} the topic {topic}:\n"
        for course in courses:
            course_subject, course_number, course_name, doc_count = course
            message += f"* {course_subject} {course_number} - {course_name} COUNT: {doc_count}\n"

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

        slides = query.get_slides_covering_topic(topic)
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

        courses = query.get_courses_without_slides()
        if courses is None or not courses:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any courses that don't have lecture slides")
            return []

        message = f"The following course{'s have' if len(courses) > 1 else ' has'} no lecture slides:\n"
        for course in courses:
            course_uri = course
            message += f"* {course_uri.split('#')[1]}, "

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

        courses = query.get_courses_covering_topic_at_university(topic, university)
        if courses is None or not courses:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any courses that cover {topic} at {university}")
            return []

        message = f"The following course{'s' if len(courses) > 1 else ''} at {university} {'cover' if len(courses) > 1 else 'covers'} the topic {topic}:\n"
        for course in courses:
            course_subject, course_number, course_name = course
            message += f"* {course_subject} {course_number} - {course_name}\n"

        dispatcher.utter_message(text=message)
        return []


class ActionCoursesOfferedByUni(Action):

    def name(self) -> Text:
        return "action_courses_offered_by_uni"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        university = tracker.slots['university']
        if university is None:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []

        courses = query.get_courses_offered_at_university(university)
        if courses is None or not courses:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any courses offered by {university}")
            return []

        message = f"The following course{'s are' if len(courses) > 1 else ' is'} offered by {university}:\n"
        for course in courses:
            course_uri = course
            message += f"* {course_uri.split('#')[1]}"

        dispatcher.utter_message(text=message)
        return []


class ActionCoursesWithLabs(Action):

    def name(self) -> Text:
        return "action_courses_with_labs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        courses = query.get_courses_with_labs()
        if courses is None or not courses:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any courses that have a lab component")
            return []

        message = f"The following course{'s have' if len(courses) > 1 else ' has'} a lab component:\n"
        for course in courses:
            course_uri = course
            message += f"* {course_uri.split('#')[1]}\n"

        dispatcher.utter_message(text=message)
        return []


class ActionTopicsCourseInCourseEvent(Action):

    def name(self) -> Text:
        return "action_topics_in_course_event"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course = tracker.slots['course']
        event_type = tracker.slots['event_type']
        number = tracker.slots['lec']

        if course is None or event_type is None or number is None:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []

        event_type = event_type.lower().strip()
        if event_type in set(['lectures', 'lecture', 'lec', 'lecs']):
            event_type = 'Lecture'
            topics = query.get_topics_covered_in_lecture(course, number)
        elif event_type in set(['labs', 'lab', 'laboratories', 'laboratory']):
            event_type = 'Lab'
            topics = query.get_topics_covered_in_lab(course, number)
        elif event_type in set(['tutorials', 'tutorial', 'tut', 'tuts']):
            event_type = 'Tutorial'
            topics = query.get_topics_covered_in_tutorial(course, number)

        if topics is None or not topics:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any topics in {event_type} {number} of course {course}")
            return []

        message = f"The following topic{'s are' if len(topics) > 1 else ' is'} covered in {event_type} {number} of course {course}:\n"
        for topic in topics:
            event, topic_uri, resource_uri = topic
            message += f"* {event_type} {number} - {event.split('#')[1]} covers {topic_uri.split('#')[1]} in {resource_uri}\n"

        dispatcher.utter_message(text=message)
        return []


class ActionCoursesByLevel(Action):

    def name(self) -> Text:
        return "action_courses_by_level"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        level = tracker.slots['level']
        university = tracker.slots['university']
        if level is None or university is None:
            dispatcher.utter_message(text=f"Sorry, I'm not sure I understand")
            return []

        courses = query.get_courses_by_level_at_university(level, university)
        if courses is None or not courses:
            dispatcher.utter_message(text=f"Sorry, I can't seem to find any {level[0]}00-level courses at {university}")
            return []

        message = f"The following courses{'s' if len(courses) > 1 else ''} {'cover' if len(courses) > 1 else 'covers'} are level {level} at {university}:\n"
        for course in courses:
            courseuri = course
            message += f"* {courseuri.split('#')[1]}, "

        dispatcher.utter_message(text=message)
        return []
