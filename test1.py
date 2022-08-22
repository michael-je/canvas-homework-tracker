from canvasapi import Canvas

API_URL = 'https://reykjavik.instructure.com'
API_KEY = '9197~kJ6GHKV8koH0eqSrCUD7IqZnQM9WLYSmQlPUz2xzqSKhiiVYI3yuMYMqt3ZpEmHI'

canvas = Canvas(API_URL, API_KEY)

courses = canvas.get_courses()

for course in courses:
    print(course.name)
    assignments = course.get_assignments()
    for assignment in assignments:
        try: 
            print('\t', assignment.name, 'due at:', assignment.due_at_date)
        except AttributeError:
            pass

