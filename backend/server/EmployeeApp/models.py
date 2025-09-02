import mongoengine as me

class Employee(me.Document):
    employee_id = me.IntField(primary_key=True)
    first_name = me.StringField(max_length=100)
    last_name = me.StringField(max_length=100)
    email = me.EmailField(unique=True)
    password = me.StringField(max_length=500)  # hash later
    department_id = me.IntField()

    meta = {
        "collection": "employees"
    }