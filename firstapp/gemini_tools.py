from django.utils import timezone
from google.generativeai.protos import FunctionDeclaration, Schema, Type
from django.core.exceptions import ObjectDoesNotExist
from firstapp.models import *


def get_student_tests(student_id: int):
    try:
        student = Students.objects.get(pk=student_id)
        teacher=student.teacher
        tests = Test.objects.filter(teacher=teacher)
        return [{"assigned test name":test.display_name,
                 "test total marks":test.test_total_marks} for test in tests]
    except ObjectDoesNotExist:
        return {"error": "Student not found"}

def get_student_test_attempts(student_id: int):
    try:
        student = Students.objects.get(pk=student_id)
        tests = TestAttempt.objects.filter(student=student)
        return [{
            'test': attempt.test.display_name,
            'obtained marks': attempt.test_marks,
            'total marks of test':attempt.test.test_total_marks
        } for attempt in tests]
    except ObjectDoesNotExist:
        return {"error": "Student not found"}

def get_student_topics(student_id: int):
    try:
        student = Students.objects.get(pk=student_id)
        topics = Topics.objects.filter(student=student)
        return [topic.topic for topic in topics]
    except ObjectDoesNotExist:
        return {"error": "Student not found"}

def get_student_name(student_id: int):
    try:
        student = Students.objects.get(pk=student_id)
        return student.name.username
    except ObjectDoesNotExist:
        return {"error": "Student not found"}

def get_student_details(student_id: int):
    try:
        student = Students.objects.get(pk=student_id)
        return {
            "name": student.name.username,
            "teacher": student.teacher.name.username,
            "description": student.description,
            "added_date": student.added_at.isoformat()
        }
    except ObjectDoesNotExist:
        return {"error": "Student not found"}
    
def get_upcoming_tests(student_id: int):
    try:
        student = Students.objects.get(pk=student_id)
        teacher = student.teacher
        upcoming_tests = Test.objects.filter(teacher=teacher, start_time__gte=timezone.now())
        return [{"test name": test.display_name, "scheduled time": test.start_time} for test in upcoming_tests]
    except ObjectDoesNotExist:
        return {"error": "Student not found"}

def personalized_greeting(student_id: int):
    try:
        student = Students.objects.get(pk=student_id)
        name = student.name.username
        upcoming_tests = get_upcoming_tests(student_id)
        
        greeting = f"Welcome back, {name}!"
        
        if upcoming_tests:
            test_info = "You have the following upcoming test(s):\n"
            for test in upcoming_tests:
                test_info += f"- {test['test name']} on {test['scheduled time'].strftime('%Y-%m-%d %H:%M')}\n"
        else:
            test_info = "You have no upcoming tests scheduled."

        greeting_message = f"{greeting}\n\n{test_info}\n\nIs there anything else you need help with?"

        return greeting_message

    except ObjectDoesNotExist:
        return {"error": "Student not found"}





tools = [
    FunctionDeclaration(
        name="get_student_tests",
        description="Fetch the tests assigned to the student.",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"student_id": Schema(type=Type.NUMBER)},
            required=["student_id"]
        )
    ),
    FunctionDeclaration(
        name="get_student_test_attempts",
        description="Fetch the test attempts made by the student.",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"student_id": Schema(type=Type.NUMBER)},
            required=["student_id"]
        )
    ),
    FunctionDeclaration(
        name="get_student_topics",
        description="Fetch the topics related to the student.",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"student_id": Schema(type=Type.NUMBER)},
            required=["student_id"]
        )
    ),
    FunctionDeclaration(
        name="get_student_name",
        description="Fetch the student's name.",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"student_id": Schema(type=Type.NUMBER)},
            required=["student_id"]
        )
    ),
    FunctionDeclaration(
        name="get_student_details",
        description="Fetch the student's details (name, teacher, description, added date).",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"student_id": Schema(type=Type.NUMBER)},
            required=["student_id"]
        )
    ),
    FunctionDeclaration(
        name="get_upcoming_tests",
        description="Fetch the upcoming tests for the student.",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"student_id": Schema(type=Type.NUMBER)},
            required=["student_id"]
        )
    ),
    FunctionDeclaration(
        name="personalized_greeting",
        description="Generate a personalized greeting for the student, informing them of upcoming tests and offering assistance.",
        parameters=Schema(
            type=Type.OBJECT,
            properties={"student_id": Schema(type=Type.NUMBER)},
            required=["student_id"]
        )
    )
]