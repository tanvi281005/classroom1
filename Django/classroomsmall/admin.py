from django.contrib import admin
from .models import Student
from .models import StudentDetails
from .models import StudentAssignment
from .models import Course
from .models import Teacher
from .models import TeacherCourses
from .models import Enrollment
from .models import Assignment
from .models import Project
from .models import Timetable
from .models import Feedback
from .models import WellnessResource
from .models import Whiteboard
from .models import CodingEnvironment
# Register your models here.
admin.site.register(Student)
admin.site.register(StudentDetails)
admin.site.register(StudentAssignment)
admin.site.register(Course)
admin.site.register(Teacher)
admin.site.register(TeacherCourses)
admin.site.register(Enrollment)
admin.site.register(Assignment)
admin.site.register(Project)
admin.site.register(Timetable)
admin.site.register(Feedback)
admin.site.register(WellnessResource)
admin.site.register(Whiteboard)
admin.site.register(CodingEnvironment)