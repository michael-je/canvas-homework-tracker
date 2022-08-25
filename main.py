from datetime import datetime
from canvasapi import Canvas
import random

from .db import DBHandler
from .assignment import Assignment
from .cfg import API_URL, API_KEY, DB_PATH, TEST

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
    print('List updated')


def show_assignments(db, _canvas):
    assignments = db.get_assignments()
    assignments = list(filter(lambda x: x.datetime > datetime.now(), assignments))
    if not assignments:
        print('no assignments to show')
        return
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
    print('Assignment added')


def main():
    ans = ''
    while ans not in ['s', 'n', 'u']: # TODO: add [m]ark and [d]elete
        ans = input('[s]how, [n]ew, [u]pdate? > ')

    canvas = Canvas(API_URL, API_KEY)
    db = DBHandler(DB_PATH)

    if ans == 'u':
        update_assignments(db, canvas)

    if ans == 's':
        show_assignments(db, canvas)

    if ans == 'n':
        create_new_assignment(db, canvas)

    #if ans == 'd':
    #    assignments = db.get_assignments()
    #    if not assignments:
    #        print('no assignments to show')
    #        return 
    #    assignments.sort(key=lambda x: x.datetime.timestamp())
    #    for n, assignment in enumerate(assignments):
    #        old_str = '(old) ' if assignment.datetime.timestamp() < datetime.now().timestamp() else ''
    #        print(f'{old_str}{n+1:2}. {str(assignment)}')
    #    n = 0
    #    while n not in range(1, len(assignments) + 1):
    #        try:
    #            n = int(input('which assignment to delete? > '))
    #        except ValueError:
    #            pass
    #    db.delete_assignment(assignments[n-1])
    #    print('assignment deleted')
        

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nexiting')
