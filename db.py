import sqlite3
from datetime import datetime
from os import path

from .assignment import Assignment

class DBHandler():
    def __init__(self, db_path):
        self.db_path = path.dirname(path.realpath(__file__)) + '/' + db_path
        if not path.exists(self.db_path):
            self.db_create()

    def db_create(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE assignments (
                id text,
                name text,
                notes text,
                date text,
                time text,
                course_name text
            )
            """
        )
        conn.commit()
        conn.close()
        
    def create_assignment(self, assignment):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO assignments VALUES (
                :id,
                :name,
                :notes,
                :date,
                :time,
                :course_name
            )
            """,
            {
                'id': assignment.id,
                'name': assignment.name,
                'notes': assignment.notes,
                'date': assignment.datetime.strftime('%d-%m-%Y'),
                'time': assignment.datetime.strftime('%H:%M'),
                'course_name': assignment.course_name
            }
        )
        conn.commit()
        conn.close()

    def get_assignments(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            """
            SELECT * FROM assignments
            """
        )
        assignments = c.fetchall()
        conn.close()
        return [Assignment(dict(assignment)) for assignment in assignments]

    def delete_assignment(self, assignment):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM assignments WHERE id=?', (assignment.id,))
        conn.commit()
        conn.close()

if __name__ == '__main__':
    props = {
        'course_name': 'course_name',
        'name': 'name',
        'notes': 'notes',
        'date': '09-04-2022',
        'time': '16:30'
    }
    assignment = Assignment(props)

    db_path = './test.db'
    db = DBHandler(db_path)
    db.create_assignment(assignment)
    assignments = db.get_assignments()
    print(assignments)
