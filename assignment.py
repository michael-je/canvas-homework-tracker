from dateutil.parser import parse
from termcolor import colored as color

class Assignment():
    def __init__(self, props):
        self.id = int(props.get('id'))
        self.name = props['name']
        self.notes = props['notes']
        self.subject = props['subject']
        time = props['time']
        date = props['date']
        self.datetime = parse(f'{date} {time}')

    def __str__(self):
        date = color(self.datetime.strftime('%d-%m-%Y'), 'yellow')
        time = color(self.datetime.strftime('%H:%M'), 'blue')
        notes = color(f'({self.notes})', 'grey') if self.notes else ''
        return f'{date} {time} | {self.subject:30} | {self.name} {notes}'
