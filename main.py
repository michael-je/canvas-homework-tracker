from datetime import datetime
from canvasapi import Canvas
import random

from .db import DBHandler
from .assignment import Assignment
from .cfg import API_URL, API_KEY, DB_PATH, TEST
from .utils import NoAssignmentsError

if TEST:
    DB_PATH = 'test.db'

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
                    'date': c_assignment.due_at_date.strftime('%d-%m-%Y'),
                    'time': c_assignment.due_at_date.strftime('%H:%M'),
                    'notes': ''
                }
            except AttributeError:
                continue
            assignment = Assignment(assignment_props)
            if assignment.id not in [assignment.id for assignment in old_assignments]:
                db.create_assignment(assignment)


def show_assignments(db, _canvas, hide_past_and_complete=True):
    assignments = db.get_assignments()
    if hide_past_and_complete:
        assignments = list(filter(lambda a: a.datetime > datetime.now() and not a.complete, assignments))
    if not assignments:
        raise NoAssignmentsError
    assignments.sort(key=lambda x: x.datetime.timestamp())
    for n, assignment in enumerate(assignments):
        print(f'{n+1:2}. {str(assignment)}')


def create_new_assignment(db, canvas):
    c_courses = canvas.get_courses() # TODO: get rid of this api call, but keep it dynamic
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
        'date': date_and_time.strftime('%d-%m-%Y'),
        'time': date_and_time.strftime('%H:%M'),
        'notes': notes
    }
    assignment = Assignment(props)
    db.create_assignment(assignment)


def mark_assignment_complete(db, canvas):
    """
    Inverts an assignment's complete status.
    
    Returns the new complete status of the assignment (True/False)
    """
    show_assignments(db, canvas, hide_past_and_complete=False)
    assignments = db.get_assignments()
    assignments.sort(key=lambda x: x.datetime.timestamp())
    n = 0
    while n not in range(1, len(assignments) + 1):
        try:
            n = int(input('which assignment to mark? > '))
        except ValueError:
            pass
    assignment = assignments[n-1]
    assignment.complete = not assignment.complete
    db.update_assignment(assignment)
    return assignment.complete


def delete_assignment(db, canvas):
    assignments = db.get_assignments()
    if not assignments:
        raise NoAssignmentsError
    assignments.sort(key=lambda x: x.datetime.timestamp())
    show_assignments(db, canvas, hide_past_and_complete=False)
    n = 0
    while n not in range(1, len(assignments) + 1):
        try:
            n = int(input('which assignment to delete? > '))
        except ValueError:
            pass
    db.delete_assignment(assignments[n-1])


def main():
    ans = ''
    while ans not in ['s', 'a', 'n', 'm', 'd', 'u']:
        ans = input('[s]how, show [a]ll, [n]ew, [m]ark complete, [d]elete, [u]pdate? > ')

    canvas = Canvas(API_URL, API_KEY)
    db = DBHandler(DB_PATH)

    if ans == 's':
        show_assignments(db, canvas)

    if ans == 'a':
        show_assignments(db, canvas, hide_past_and_complete=False)

    if ans == 'n':
        create_new_assignment(db, canvas)
        print('New assignment created')

    if ans == 'm':
        result = mark_assignment_complete(db, canvas)
        if result:
            print('assignment marked as complete')
        else:
            print('assignment unmarked')

    if ans == 'd':
        delete_assignment(db, canvas)
        print('assignment deleted')

    if ans == 'u':
        update_assignments(db, canvas)
        print('List updated')
        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nexiting')
    except NoAssignmentsError as e:
        print(e)
