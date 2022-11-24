import json

def get_student_id_from_json(name):
    f = open('student_id.json')
    data = json.load(f)
    return data[name]

student_id = get_student_id_from_json('pung')
print(f'Hello, {student_id}')




