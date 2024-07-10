import os
import sys
import django
from google.generativeai.protos import FunctionDeclaration, Schema, Type
from django.core.exceptions import ObjectDoesNotExist

# Set up Django environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modelrev2.settings')
django.setup()

# Import necessary modules
from firstapp.models import *
import google.generativeai as genai

# Configure API key
genai.configure(api_key="AIzaSyDM0bMWBOV-mmmG0lgdgiq022YFQa9CtbI")
os.environ["GOOGLE_API_KEY"] = "AIzaSyDM0bMWBOV-mmmG0lgdgiq022YFQa9CtbI"

# Define the functions with Django ORM
def get_student_tests(student_id: int):
    try:
        student = Students.objects.get(pk=student_id)
        teacher=student.teacher
        tests = Test.objects.filter(teacher=teacher)
        return [test.display_name for test in tests]
    except ObjectDoesNotExist:
        return {"error": "Student not found"}

def get_student_test_attempts(student_id: int):
    try:
        student = Students.objects.get(pk=student_id)
        tests = TestAttempt.objects.filter(student=student)
        return [{
            'test': attempt.test.display_name,
            'marks': attempt.test_marks
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
        return student.name
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

# Define the tools
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
    )
]

# Define safety settings
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Initialize the model
model2 = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=tools,
    safety_settings=safety_settings,
    generation_config={
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    },
    system_instruction=(
        "You are a helpful assistant who uses ONLY the tools given to you to answer specific questions. "
        "For questions related to a student's academic details, you have the following tools:\n"
        "- 'get_student_tests(student_id)': to fetch the tests assigned to the student.\n"
        "- 'get_student_test_attempts(student_id)': to fetch the test attempts made by the student.\n"
        "- 'get_student_topics(student_id)': to fetch the topics related to the student.\n"
        "- 'get_student_name(student_id)': to fetch the student's name.\n"
        "- 'get_student_details(student_id)': to fetch the student's details (name, teacher, description, added date).\n"
    ),
)

# Start chat session with automatic function calling enabled
chat = model2.start_chat(enable_automatic_function_calling=True)

# Send message and handle the response
response = chat.send_message("Summarize whole detail about student with id 2 along with his test attempts and tests given")

# Process the response parts to handle function calls
for part in response.parts:
    if fn := part.function_call:
        function_name = fn.name
        args = fn.args

        if function_name == "get_student_tests":
            result = get_student_tests(args["student_id"])
        elif function_name == "get_student_test_attempts":
            result = get_student_test_attempts(args["student_id"])
        elif function_name == "get_student_topics":
            result = get_student_topics(args["student_id"])
        elif function_name == "get_student_name":
            result = get_student_name(args["student_id"])
        elif function_name == "get_student_details":
            result = get_student_details(args["student_id"])
        else:
            result = {"error": f"Unknown function: {function_name}"}

        response_parts = [
            genai.protos.Part(
                function_response=genai.protos.FunctionResponse(
                    name=function_name,
                    response={"result": result}
                )
            )
        ]
        response = chat.send_message(response_parts)

# If no function call, print the text response directly
if not response.parts[0].function_call:
    print(response.text)
