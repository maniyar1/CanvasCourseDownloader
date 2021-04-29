#!/bin/env python3
import os
import sys
import argparse

import canvasapi.course, canvasapi.user, canvasapi.file

from src.assignment import Assignment
from src.filesystem import FileSystem
from src.module import Module
from src.util import safe_name


parser = argparse.ArgumentParser(description='Download and store files from Canvas courses')
parser.add_argument('-i', '--interactive', action='store_true')


class Course:
    def __init__(self, canvas_course: canvasapi.course.Course, canvas_user: canvasapi.user.User, canvas_api: canvasapi.Canvas):
        self.course = canvas_course
        self.user = canvas_user
        self.api = canvas_api

        self.id = self.course.id
        self.name = self.course.name
        self.start_date = self.course.start_at
        self.end_date = self.course.end_at
        self.created_date = self.course.created_at

        self.modules = [Module(module, self.course) for module in self.course.get_modules()]
        self.assignments = [Assignment(assignment, self.user, self.api) for assignment in self.course.get_assignments()]

        self.files = FileSystem(self.course)
        print(self.files)


    def download(self):
        print("boop")
        dir_name = f"./downloads/{safe_name(self.id, self.name)}"

        # If the course downloads directory doesn't exist, make it if not os.path.exists(dir_name): os.makedirs(dir_name)

        # Download all course modules and their module items
        print("boop1")
        for module in self.modules:
            module.download(dir_name + "/modules")

        # Download all of the assignments and their submissions
        print("boop2")
        for assignment in self.assignments:
            assignment.download(dir_name + "/assignments")

        self.files.download(dir_name + "/files")

        # TODO: Write JSON representation of the course and assignments here
        # self.__dict__  # Make sure this recursively dumps, or do it inside the assignment download too


if __name__ == "__main__":
    import canvasapi

    API_URL = os.getenv("CANVAS_API_URL", "NO_API_URL_SET")
    API_KEY = os.getenv("CANVAS_API_KEY", "NO_API_KEY_SET")
    args = parser.parse_args()

    if args.interactive:
        API_URL = input("Please enter the API URL to use\n")
        API_KEY = input("Please enter the API KEY to use\n")
        canvas = canvasapi.Canvas(API_URL, API_KEY)
        user = canvas.get_current_user()


        courses = canvas.get_courses()
        for course in courses:
            c = Course(course, user, canvas)
            c.download()
    elif API_KEY != "NO_API_KEY_SET" and API_URL != "NO_API_URL_SET":
        canvas = canvasapi.Canvas(API_URL, API_KEY)
        user = canvas.get_current_user()

        courses = canvas.get_courses()
        for course in courses:
            course.download()
    else:
        print("CANVAS_API_KEY or CANVAS_API_URL environment variables are not set and this script is not in interactive mode.", file = sys.stderr)
