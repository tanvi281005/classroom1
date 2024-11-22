from django.contrib.auth.backends import BaseBackend
from .models import Student
from .models import StudentDetails, Enrollment, Course, Teacher, TeacherCourses, Timetable, Assignment
from .models import Project
from .models import Feedback
from .models import WellnessResource
from .models import Whiteboard
from .models import CodingEnvironment
class StudentBackend(BaseBackend):
    def authenticate(self, request, student_id=None, password=None, **kwargs):
        try:
            student = Student.objects.get(student_id=student_id)
            if not hasattr(student, 'studentdetails'):
                print(f"Missing StudentDetails for student: {student.student_name}")
                return None

            if student.studentdetails.date_of_birth.strftime('%Y-%m-%d') == password:
                return student
        except Student.DoesNotExist:
            print(f"Student with ID {student_id} does not exist")
            return None

    def get_user(self, user_id):
        try:
            return Student.objects.get(pk=user_id)
        except Student.DoesNotExist:
            return None
