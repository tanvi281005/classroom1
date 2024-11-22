from django.db import models
from django.contrib.auth.models import AbstractBaseUser, User
from django.utils import timezone

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_info', null=True)
    student_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    language_preference = models.CharField(max_length=50, help_text='Preferred language of the student.')
    dashboard_layout = models.JSONField(default=dict)

    def __str__(self):
        return self.student_name

class StudentDetails(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='studentdetails')
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    parent_contact = models.CharField(max_length=10)
    city = models.CharField(max_length=255)
    gender = models.CharField(max_length=6, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    date_of_birth = models.DateField()
    grade_level = models.CharField(max_length=9, choices=[
        ('Freshman', 'Freshman'),
        ('Sophomore', 'Sophomore'),
        ('Junior', 'Junior'),
        ('Senior', 'Senior')
    ])
    emergency_contact = models.CharField(max_length=10)

    def __str__(self):
        return self.student.student_name

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255)
    course_description = models.TextField()
    study_materials = models.TextField()
    video_lectures = models.TextField()

    def __str__(self):
        return self.course_name

class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    teacher_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=10)
    specialization = models.CharField(max_length=255)
    password = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.teacher_name

class TeacherCourses(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher.teacher_name} - {self.course.course_name}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.student_name} enrolled in {self.course.course_name}"

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    assignment_file = models.FileField(upload_to='assignments/')

    def __str__(self):
        return self.title

class Project(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    project_title = models.CharField(max_length=255)
    details = models.TextField()

    def __str__(self):
        return self.project_title

class StudentAssignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    submission_status = models.CharField(max_length=9, choices=[
        ('Pending', 'Pending'),
        ('Submitted', 'Submitted'),
        ('Graded', 'Graded')
    ], default='Pending')
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    submission_date = models.DateField(null=True)
    submission_file = models.FileField(upload_to='submissions/', null=True, blank=True)

    def __str__(self):
        return f"{self.student.student_name} - {self.assignment.title}"

class Timetable(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_time = models.TimeField()
    day_of_week = models.CharField(max_length=9, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')
    ])

    def __str__(self):
        return f"{self.student.student_name} - {self.course.course_name} on {self.day_of_week}"

class Feedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    rating = models.IntegerField()

    def __str__(self):
        return f"Feedback by {self.student.student_name} for {self.course.course_name}"

class CodingEnvironment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    language_used = models.CharField(max_length=50)
    code = models.TextField()

    def __str__(self):
        return f"{self.student.student_name} - {self.language_used}"

class WellnessResource(models.Model):
    resource_id = models.AutoField(primary_key=True)
    resource_name = models.CharField(max_length=255)
    description = models.TextField()
    resource_type = models.CharField(max_length=8, choices=[
        ('Video', 'Video'),
        ('Article', 'Article'),
        ('Exercise', 'Exercise')
    ])
    visited_by = models.ManyToManyField(User, related_name="visited_resources", blank=True)
    link = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.resource_name

class Whiteboard(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)
    drawing_data = models.TextField(blank=True)

    def __str__(self):
        return f"Whiteboard of {self.student.student_name}"

