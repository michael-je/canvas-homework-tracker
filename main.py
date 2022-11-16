from datetime import datetime
from canvasapi import Canvas
import random
import re

from .db import DBHandler
from .assignment import Assignment
from .cfg import API_URL, API_KEY, DB_PATH, TEST
from .utils import NoAssignmentsError, SelectionOutOfBoundsError, POSITIVE_RESPONSES, NEGATIVE_RESPONSES

if TEST:
    DB_PATH = 'test.db'


def get_selections(assignments, message=None):
    print_assignments(assignments)
    if message:
        print(message)
    print('Use commas and dashes to select multiple assignments, i.e: 1,3,4-8')

    input_regex = r'^\d+(-\d+)?(,\d+|,\d+-\d+)*$'
    input_valid = False
    while not input_valid:
        user_input = input('Enter your selection > ')
        input_valid = bool(re.match(input_regex, user_input))
    
    selections = []
    selected_ranges = user_input.split(',')
    for selected_range in selected_ranges:
        selected_range = selected_range.split('-')
        if len(selected_range) == 2:
            lower_bound = int(selected_range[0])
            upper_bound = int(selected_range[1])
            for i in range(lower_bound, upper_bound + 1):
                selections.append(i)
        else:
            selections.append(int(selected_range[0]))

    selections = list(set(selections))
    selections.sort()
    if selections[-1] > len(assignments):
        raise SelectionOutOfBoundsError
    return selections


def filter_and_sort_assignments(assignments, filter_past_and_complete=False):
    if filter_past_and_complete:
        assignments = list(filter(
            lambda a: a.timestamp > datetime.now().timestamp() and not a.complete, assignments
        ))
    assignments.sort(key=lambda a: a.timestamp)
    return assignments


def update_assignments(db, canvas):
    c_courses = canvas.get_courses()
    old_assignments = db.get_assignments()

    for c_course in c_courses:
        c_assignments = c_course.get_assignments()
        for c_assignment in c_assignments:
            try: 
                assignment_props = {
                    'id': c_assignment.id,
                    'name': c_assignment.name,
                    'course_name': c_course.name,
                    'timestamp': c_assignment.due_at_date.timestamp(),
                    'notes': ''
                }
            except AttributeError:
                continue
            assignment = Assignment(assignment_props)
            if assignment.id not in [assignment.id for assignment in old_assignments]:
                db.create_assignment(assignment)


def print_assignments(assignments):
    if not assignments:
        raise NoAssignmentsError
    for n, assignment in enumerate(assignments):
        print(f'{n+1:2}. {str(assignment)}')


def create_new_assignment(db, canvas):
    c_courses = canvas.get_courses()
    course_names = [c_course.name for c_course in c_courses
        if len(list(c_course.get_assignments()))]
    ans = 0
    for n, course in enumerate(course_names):
        print(f'[{n+1}] {course}')
    while ans not in range(1, len(course_names) + 1):
        try:
            ans = int(input('course? > '))
        except ValueError:
            pass
    course_name = course_names[ans-1]
    
    assignment_name = input('project name? > ')

    date_and_time = datetime.now()
    date_valid = False
    while not date_valid:
        date_in = input('date? [DD-MM-YYYY] > ')
        vals = date_in.split('-')
        if vals[0] == '':
            vals.pop()
        try:
            vals = [int(val) for val in vals]
            if len(vals) >= 1:
                date_and_time = date_and_time.replace(day=vals[0])
            if len(vals) >= 2:
                date_and_time = date_and_time.replace(month=vals[1])
            if len(vals) >= 3:
                date_and_time = date_and_time.replace(year=vals[2])
            date_valid = True
        except (ValueError, TypeError):
            print('incorrect date format')

    time_valid = False
    while not time_valid:
        time_in = input('time? [HH:MM] > ')
        vals = time_in.split(':')
        if vals[0] == '':
            vals.pop()
        try:
            vals = [int(val) for val in vals]
            date_and_time = date_and_time.replace(hour=vals[0])
            if len(vals) >= 2:
                date_and_time = date_and_time.replace(minute=vals[1])
            else:
                date_and_time = date_and_time.replace(minute=0)
            time_valid = True
        except (ValueError, TypeError, IndexError) as err:
            print('incorrect time format')

    notes = input('notes? > ')

    props = {
        'id': -int(random.random() * 1000000000), # shitfix
        'name': assignment_name,
        'course_name': course_name,
        'timestamp': date_and_time.gettimestamp(),
        'notes': notes
    }
    assignment = Assignment(props)
    db.create_assignment(assignment)


def mark_assignment_complete(db, canvas):
    """
    Inverts an assignment's complete status.
    
    Returns the new complete status of the assignment (True/False)
    """
    assignments = db.get_assignments()
    assignments = filter_and_sort_assignments(assignments)

    selections = get_selections(assignments, message='which assignment(s) to mark?')
    for selection in selections:
        assignment = assignments[selection-1]
        assignment.complete = not assignment.complete

        if assignment.complete == False:
            answer = ''
            print(f'are you sure you want to mark assignment "{assignment.name}" as incomplete?')
            while answer not in (POSITIVE_RESPONSES + NEGATIVE_RESPONSES):
                answer = input('y/n > ')
            if answer in NEGATIVE_RESPONSES:
                continue

        db.update_assignment(assignment)


def delete_assignment(db, canvas):
    assignments = db.get_assignments()
    assignments = filter_and_sort_assignments(assignments)

    selections = get_selections(assignments, message='which assignment(s) to delete?')
    for selection in selections:
        db.delete_assignment(assignments[selection-1])


def main():
    ans = ''
    while ans not in ['s', 'a', 'n', 'm', 'd', 'u']:
        ans = input('[s]how, show [a]ll, [n]ew, [m]ark complete, [d]elete, [u]pdate? > ')

    canvas = Canvas(API_URL, API_KEY)
    db = DBHandler(DB_PATH)

    if ans == 's':
        assignments = db.get_assignments()
        assignments = filter_and_sort_assignments(assignments, filter_past_and_complete=True)
        print_assignments(assignments)

    if ans == 'a':
        assignments = db.get_assignments()
        assignments = filter_and_sort_assignments(assignments)
        print_assignments(assignments)

    if ans == 'n':
        create_new_assignment(db, canvas)
        print('New assignment created')

    if ans == 'm':
        result = mark_assignment_complete(db, canvas)
        print('assignment(s) marked')

    if ans == 'd':
        delete_assignment(db, canvas)
        print('assignment(s) deleted')

    if ans == 'u':
        update_assignments(db, canvas)
        print('List updated')
        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nexiting')
    except (NoAssignmentsError, SelectionOutOfBoundsError) as e:
        print(e)
