from dateutil.parser import parse
from termcolor import colored as color
from .cfg import COURSE_NAME_TRUNCLEN

class Assignment():
    def __init__(self, props):
        self.id = int(props.get('id'))
        self.name = props['name']
        self.notes = props['notes']
        self.course_name = props['course_name']
        time = props['time']
        date = props['date']
        self.datetime = parse(f'{date} {time}')
        self.complete = bool(props.get('complete', False))

    def truncate_name(self):
        if len(self.name) > COURSE_NAME_TRUNCLEN:
            self.name = self.name[:COURSE_NAME_TRUNCLEN] + '...'
        return self.name

    def __str__(self):
        text_colors = {
            'complete_mark': 'green',
            'date': 'yellow',
            'time': 'blue',
            'course_name': 'white',
            'name': 'white',
            'notes': 'grey',
        }
        if self.complete:
            for prop in ['date', 'time', 'course_name', 'name', 'notes']:
                text_colors[prop] = 'grey'
        

        complete_mark = color('X' if self.complete else ' ', text_colors['complete_mark'])
        date = color(self.datetime.strftime('%d-%m-%Y'), text_colors['date'])
        time = color(self.datetime.strftime('%H:%M'), text_colors['time'])
        course_name = color(self.course_name, text_colors['course_name'])
        name = color(self.name, text_colors['name'])
        notes = color(f'({self.notes})', text_colors['notes']) if self.notes else ''
        self.truncate_name()
        
        return f'[{complete_mark}] {date} {time} | {course_name:40} | {name} {notes}'

    def get_props(self, db_readable=False):
        props = {
            'id': self.id,
            'name': self.name,
            'notes': self.notes,
            'date': self.datetime.strftime('%d-%m-%Y'),
            'time': self.datetime.strftime('%H:%M'),
            'course_name': self.course_name,
            'complete': int(self.complete) if db_readable else self.complete
        }
        return props