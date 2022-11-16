from termcolor import colored as color
from datetime import datetime

from .cfg import COURSE_NAME_TRUNCLEN

class Assignment():
    def __init__(self, props):
        self.id = int(props.get('id'))
        self.name = props['name']
        self.notes = props['notes']
        self.course_name = props['course_name']
        self.timestamp = int(props['timestamp'])
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
            for prop in ['timestamp', 'course_name', 'name', 'notes']:
                text_colors[prop] = 'grey'

        datetime_obj = datetime.fromtimestamp(self.timestamp)
        formatted_date = datetime_obj.strftime('%H-%M')
        formatted_time = datetime_obj.strftime('%d-%m-%Y')

        complete_mark = color('X' if self.complete else ' ', text_colors['complete_mark'])
        date = color(formatted_date, text_colors['date'])
        time = color(formatted_time, text_colors['time'])
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
            'timestamp': self.timestamp,
            'course_name': self.course_name,
            'complete': int(self.complete) if db_readable else self.complete
        }
        return props

