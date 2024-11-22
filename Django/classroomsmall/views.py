from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
from django.contrib.auth import login
from .forms import StudentLoginForm
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Student
from .models import StudentDetails,Enrollment, TeacherCourses, Teacher
from .models import StudentAssignment
from .models import Course
from .models import Assignment
from .models import Project
from .models import Timetable
from .models import Feedback
from .models import WellnessResource
from .models import Whiteboard
from .models import CodingEnvironment
from .forms import AssignmentForm, StudentAssignmentForm
from django.utils import timezone
from django.contrib import messages
import requests
def index(request):
    return render(request, 'index.html')

def login_student(request):
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')

        if not student_id or not password:
            return render(request, 'login_student.html', {'error': 'Please provide both student ID and password'})

        try:
            student = Student.objects.get(student_id=student_id)

         
            if student.studentdetails.date_of_birth.strftime('%Y-%m-%d') == password:
                user, created = User.objects.get_or_create(username=student_id)
                if created:
                    user.set_password(password)
                    user.save()

                if student.user is None:
                    student.user = user
                    student.save()

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                return redirect('classroom')
            else:
                return render(request, 'login_student.html', {'error': 'Invalid login credentials'})

        except Student.DoesNotExist:
            return render(request, 'login_student.html', {'error': 'Invalid login credentials'})

    return render(request, 'login_student.html')

def student_info(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    student_details = get_object_or_404(StudentDetails, student_id=student)
    context = {
        'student': student,
        'student_details': student_details,
    }
    return render(request, 'student_info.html', context)

from django.urls import reverse
def login_teacher(request):
    if request.method == "POST":
        teacher_id = request.POST.get('teacher_id')
        password = request.POST.get('password')

        if not teacher_id or not password:
            return render(request, 'login_teacher.html', {'error': 'Please provide both teacher ID and password'})

        try:
            
            teacher = Teacher.objects.get(teacher_id=teacher_id)

            if teacher.password == password: 
                return redirect(reverse('teacher_portal') + f'?teacher_id={teacher.teacher_id}')
            else:
                return render(request, 'login_teacher.html', {'error': 'Invalid login credentials'})

        except Teacher.DoesNotExist:
            return render(request, 'login_teacher.html', {'error': 'Invalid login credentials'})

    return render(request, 'login_teacher.html')


def study_material(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'study_material.html', {'course': course})




def assignments(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    assignments = Assignment.objects.filter(course=course)
    return render(request, 'assignments.html', {'course': course, 'assignments': assignments})


def projects(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    projects = Project.objects.filter(course=course)
    return render(request, 'projects.html', {'course': course, 'projects': projects})


def quiz(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'quiz.html', {'course': course})

from constance import config

@login_required
def classroom(request):
    user = request.user
    student = user.student_info
    timetable = Timetable.objects.filter(student=student).select_related('course')

    student_details = get_object_or_404(StudentDetails, student=student)
    enrolled_courses = Enrollment.objects.filter(student=student).values_list('course', flat=True)
    assignments = Assignment.objects.filter(course__in=enrolled_courses)

    study_material_notification = config.STUDY_MATERIALS_UPLOAD_NOTIFICATION
    video_upload_notification = config.VIDEO_UPLOAD_NOTIFICATION  
    assignment_upload_notification=config.ASSIGNMENT_UPLOAD_NOTIFICATION
    return render(request, 'classroom.html', {
        'timetable': timetable,
        'student': student,
        'student_details': student_details,
        'assignments': assignments,
        'study_material_notification': study_material_notification,
        'video_upload_notification': video_upload_notification,
        'assignment_upload_notification': assignment_upload_notification,  
    })


@login_required
def classes(request):
    user = request.user

    student_id = request.GET.get('student_id')
    
    if student_id:
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            student = None
            courses_with_resources = []
    else:
        try:
            student = user.student_info
        except Student.DoesNotExist:
            student = None

    if student:
        enrolled_courses = Enrollment.objects.filter(student=student).select_related('course')
        print("Enrolled courses:", enrolled_courses)

        courses_with_resources = []
        
        for enrollment in enrolled_courses:
            course = enrollment.course

            assignments = Assignment.objects.filter(course=course)
            projects = Project.objects.filter(course=course)
            study_materials = course.study_materials.splitlines()  
            video_lectures = course.video_lectures.splitlines()    
            courses_with_resources.append({
                'course': course,
                'assignments': assignments,
                'projects': projects,
                'study_materials': study_materials,
                'video_lectures': video_lectures,
            })
    else:
       
        courses_with_resources = []
    return render(request, 'classes.html', {'courses_with_resources': courses_with_resources})

def teachers(request):
    teachers = [] 
    student_id = request.GET.get('student_id')  

    if student_id:
        try:
            student = Student.objects.get(pk=student_id) 
            enrolled_courses = Enrollment.objects.filter(student=student)  
            teacher_ids = enrolled_courses.values_list('course__teachercourses__teacher_id', flat=True).distinct()
            teachers = Teacher.objects.filter(teacher_id__in=teacher_ids)  
        except Student.DoesNotExist:
            teachers = []  

    return render(request, 'teachers.html', {'teachers': teachers})

def calendar_page(request):
    return render(request, 'calendar_page.html')

def calendar_page23(request):
    return render(request, 'calendar23.html')

def calendar_2024_25(request):
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    return render(request, 'calendar_2024_25.html', {'months': months})




@login_required  
def whiteboard(request):
    try:
       
        student = Student.objects.get(user=request.user)  
        
       
        student_whiteboard = Whiteboard.objects.filter(student=student).order_by('-created_at')  

        if request.method == 'POST':  
            content = request.POST.get('content')
            drawing_data = request.POST.get('drawing_data') 
            if content or drawing_data: 
                Whiteboard.objects.create(student=student, content=content, drawing_data=drawing_data)  
                return redirect('whiteboard') 

      
        return render(request, 'whiteboard.html', {'whiteboard': student_whiteboard})

    except Student.DoesNotExist:
        return render(request, 'whiteboard.html', {'error': 'Student not found.'})
    
@login_required
def wellness_resources(request):
    resources = WellnessResource.objects.all()
    visited_resource_ids = request.user.visited_resources.values_list('resource_id', flat=True)
    
    if request.method == "POST":
        visited_ids = request.POST.getlist('visited')
        for resource in resources:
            if str(resource.resource_id) in visited_ids:
                resource.visited_by.add(request.user)
            else:
                resource.visited_by.remove(request.user)
        return redirect('wellness_resources')

    return render(request, 'wellness_resources.html', {
        'resources': resources,
        'visited_resource_ids': visited_resource_ids
    })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def run_code(request):
    try:
        body = request.data
        code = body.get('code')
        language = body.get('language')
        inputs = body.get('inputs','')

       
        if not language:
            return Response({'error': 'Compiling language must not be null.'}, status=status.HTTP_400_BAD_REQUEST)
        if not code:
            return Response({'error': 'Code must not be empty.'}, status=status.HTTP_400_BAD_REQUEST)

       
        if inputs:
            input_lines = inputs.splitlines()
            if language.lower() == 'java':
                input_code = "\n".join(
                    [f"int var{i + 1} = scanner.nextInt();" for i in range(len(input_lines))]
                )
                code = f"""
import java.util.Scanner;

public class Main {{
    public static void main(String[] args) {{
        Scanner scanner = new Scanner(System.in);
        {input_code}
        {code}
    }}
}}
"""
            elif language.lower() == 'c':
                input_code = "\n".join([f"int var{i + 1}; scanf(\"%d\", &var{i + 1});" for i in range(len(input_lines))])
                code = f"#include <stdio.h>\n\nint main() {{\n    {input_code}\n    {code}\n    return 0;\n}}"
            elif language.lower() == 'cpp':
                input_code = "\n".join([f"int var{i + 1}; std::cin >> var{i + 1};" for i in range(len(input_lines))])
                code = f"#include <iostream>\nusing namespace std;\n\nint main() {{\n    {input_code}\n    {code}\n    return 0;\n}}"
            else:
                return Response({'error': f'Unsupported language: {language}'}, status=status.HTTP_400_BAD_REQUEST)

        
        api_key = 'f5703ce8ef65cb101620700fe157f8b0' 
        client_secret = '1d9b97552ceff6cbb7adfad8b9b8a897b235b50ba3e8c5187f67251d64df03d8'  
        url = "https://api.jdoodle.com/v1/execute"

        language_versions = {
            'java': '2',
            'c': '0',
            'cpp': '0'
        }

        version_index = language_versions.get(language.lower())
        if version_index is None:
            return Response({'error': f'Unsupported language: {language}'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "script": code,
            "language": language.lower(),
            "versionIndex": version_index,
            "clientId": api_key,
            "clientSecret": client_secret
        }

        response = requests.post(url, json=data)
        print("JDoodle API Response:", response.json()) 
        if response.status_code != 200:
            return Response({'error': 'Failed to execute code.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        if response.status_code != 200:
            return Response({'error': 'Failed to execute code.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

       
        return Response(response.json(), status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON format.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@login_required
def practice_code(request):
    try:
        student = Student.objects.get(user=request.user)
        snippets = CodingEnvironment.objects.filter(student=student)
    except Student.DoesNotExist:
        snippets = [] 

    return render(request, 'practice_code.html', {'snippets': snippets})

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_code(request):
    language_used = request.data.get('language')
    code = request.data.get('code')

    try:
        student = Student.objects.get(user=request.user)
        if language_used and code:
            CodingEnvironment.objects.create(student=student, language_used=language_used, code=code)
            return Response({'message': 'Code saved successfully.'}, status=201)
        else:
            return Response({'error': 'Language or code not provided.'}, status=400)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found.'}, status=404)
    


'''@login_required
def teacher_portal(request):
    # Get the teacher ID from the GET request
    teacher_id = request.GET.get('teacher_id')
    
    # Return an empty view if teacher_id is not provided
    if not teacher_id:
        return render(request, 'teacher_portal.html', {
            'teacher_name': None,
            'teachers_with_courses': [],
            'teacher_id': None,
        })
    
    # Fetch the teacher and courses taught by this teacher
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    teacher_name = teacher.teacher_name
    teachers_with_courses = [
        {
            'course_id': course.course.course_id,
            'course_name': course.course.course_name,
        }
        for course in TeacherCourses.objects.filter(teacher=teacher).select_related('course')
    ]

    return render(request, 'teacher_portal.html', {
        'teacher_name': teacher_name,
        'teachers_with_courses': teachers_with_courses,
        'teacher_id': teacher_id,  # Include teacher_id in the context
    })
    '''

from django import forms
class UploadVideoForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.none())  
    video_url = forms.URLField(required=True)  
    title = forms.CharField(max_length=255, required=True)  

    def __init__(self, *args, **kwargs):
        teacher_courses = kwargs.pop('teacher_courses', [])
        super().__init__(*args, **kwargs)
       
        self.fields['course'].queryset = teacher_courses

from django.contrib import messages 
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@login_required
def upload_video(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    teacher_courses = Course.objects.filter(teachercourses__teacher=teacher)

    if request.method == 'POST':
        form = UploadVideoForm(request.POST, teacher_courses=teacher_courses)
        if form.is_valid():
            course = form.cleaned_data['course']
            video_url = form.cleaned_data['video_url']
            video_title = form.cleaned_data['title']

            if course.video_lectures:
                course.video_lectures += f"\n{video_url}|{video_title}"
            else:
                course.video_lectures = f"{video_url}|{video_title}"
            course.save()

            notification_message = f"New video '{video_title}' uploaded to {course.course_name}."
            config.VIDEO_UPLOAD_NOTIFICATION = notification_message

            for enrollment in Enrollment.objects.filter(course=course):
                student = enrollment.student
                messages.info(request, f"Notification to {student.student_name}: {notification_message}")

            messages.success(request, f"Video '{video_title}' uploaded to {course.course_name} successfully!")
            return redirect('video_lectures', teacher_id=teacher_id)
        else:
            messages.error(request, "Invalid form submission.")

    form = UploadVideoForm(teacher_courses=teacher_courses)
    return render(request, 'upload_video.html', {
        'teacher': teacher,
        'form': form,
        'teacher_courses': teacher_courses
    })



@login_required
def video_lectures(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    courses = TeacherCourses.objects.filter(teacher=teacher).select_related('course')

    video_lectures = {}
    for course in courses:
        videos = []
        for entry in course.course.video_lectures.splitlines():
            if entry.strip(): 
                parts = entry.split('|')  
                if len(parts) == 2: 
                    video_url, title = parts
                   
                    video_id = extract_video_id(video_url)
                    if video_id:
                        thumbnail_url = f'https://img.youtube.com/vi/{video_id}/0.jpg'
                        videos.append({'url': video_url, 'thumbnail': thumbnail_url, 'title': title})
                    else:
                        print(f"Invalid URL: {video_url}")  
        video_lectures[course.course.course_name] = videos

    return render(request, 'video_lectures.html', {
        'video_lectures': video_lectures,
        'teacher': teacher,
        'teacher_id': teacher_id,
    })


def extract_video_id(url):
    """Extracts the video ID from a YouTube URL."""
   
    url = url.split('?')[0]  
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1]
    elif "v=" in url:
        return url.split("v=")[-1].split("&")[0] 
    elif "watch?v=" in url:
        return url.split("watch?v=")[-1].split("&")[0]  
    elif "youtube.com/live/" in url:
        return url.split("live/")[-1]  
    elif "youtube.com/embed/" in url:
        return url.split("embed/")[-1]  
    return None  


from django.core.files.storage import FileSystemStorage  

class UploadMaterialForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.none())  
    material_file = forms.FileField(required=True)  

    def __init__(self, *args, **kwargs):
        teacher_courses = kwargs.pop('teacher_courses', [])
        super().__init__(*args, **kwargs)
       
        self.fields['course'].queryset = teacher_courses

from constance import config

@login_required
def upload_material(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    teacher_courses = Course.objects.filter(teachercourses__teacher=teacher)

    if request.method == 'POST':
        form = UploadMaterialForm(request.POST, request.FILES, teacher_courses=teacher_courses)
        if form.is_valid():
            course = form.cleaned_data['course']
            material_file = request.FILES['material_file']

            fs = FileSystemStorage()
            filename = fs.save(material_file.name, material_file)
            uploaded_file_url = fs.url(filename)

            if course.study_materials:
                course.study_materials += f"\n{uploaded_file_url}|{material_file.name}"
            else:
                course.study_materials = f"{uploaded_file_url}|{material_file.name}"
            course.save()

            config.STUDY_MATERIALS_UPLOAD_NOTIFICATION = f"New study material '{material_file.name}' uploaded to {course.course_name}."

            messages.success(request, f"Material '{material_file.name}' uploaded to {course.course_name} successfully!")
            return redirect('study_materials', teacher_id=teacher_id)
        else:
            messages.error(request, "Invalid form submission.")

    form = UploadMaterialForm(teacher_courses=teacher_courses)
    return render(request, 'upload_material.html', {
        'teacher': teacher,
        'form': form,
        'teacher_courses': teacher_courses
    })


@login_required
def study_materials(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    courses = TeacherCourses.objects.filter(teacher=teacher).select_related('course')

    study_materials = {}
    for course in courses:
        materials = []
        for entry in course.course.study_materials.splitlines():
            if entry.strip():  
                parts = entry.split('|')  
                if len(parts) == 2:  
                    file_url, title = parts
                    materials.append({'url': file_url, 'title': title})
        
        study_materials[course.course.course_name] = materials

    return render(request, 'study_materials.html', {
        'study_materials': study_materials,
        'teacher': teacher,
        'teacher_id': teacher_id,
    })
from django.views import View
class StudentVideosView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id)

        video_lectures = []
        if course.video_lectures:
            entries = course.video_lectures.strip().split("\n")
            for entry in entries:
               
                url_title = entry.split("|")
                if len(url_title) == 2:
                    video_url, video_title = url_title
                    video_lectures.append({
                        'url': video_url,
                        'title': video_title
                    })

        context = {
            'course': course,
            'video_lectures': video_lectures,
        }
        return render(request, 'student_videos.html', context)

class StudentStudyMaterialsView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        
        study_materials = []
        if course.study_materials:
            materials_list = course.study_materials.split('\n')
            study_materials = [material.split('|') for material in materials_list if '|' in material]

        context = {
            'course': course,
            'study_materials': study_materials, 
        }
        return render(request, 'student_study.html', context)

def teacher_portal(request):
    teacher_id = request.GET.get('teacher_id')  
    teachers_with_courses = []  
    teacher_name = None 

    if teacher_id:
        try:
           
            teacher = Teacher.objects.get(pk=teacher_id)
            teacher_name = teacher.teacher_name 

            courses_taught = TeacherCourses.objects.filter(teacher=teacher).select_related('course')

            for course in courses_taught:
                teachers_with_courses.append({
                    'course_id': course.course.course_id, 
                    'course_name': course.course.course_name,  
                })
        except Teacher.DoesNotExist:
            teachers_with_courses = [] 
    return render(request, 'teacher_portal.html', {
        'teacher_name': teacher_name,
        'teacher_id': teacher_id,
        'teachers_with_courses': teachers_with_courses
    })

def teacherprofile(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    
    courses = TeacherCourses.objects.filter(teacher=teacher)
    
    return render(request, 'teacherprofile.html', {
        'teacher': teacher,
        'courses': courses
    })





def assignments(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    assignments = Assignment.objects.filter(course=course)
    submitted_assignments = StudentAssignment.objects.filter(assignment__course=course)
    print(course.course_id)
    return render(request, 'assignments.html', {
        'course': course,
        'assignments': assignments,
        'submitted_assignments': submitted_assignments,
    })


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync




def course_assignments(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    assignments = Assignment.objects.filter(course=course)
    
    student_profile = getattr(request.user, 'student_info', None)
    current_date = timezone.now().date()
    if student_profile is None:
        messages.error(request, "You need to be a registered student to view assignments.")
        return redirect('home')  
    student_submissions = {
        assignment.id: StudentAssignment.objects.filter(assignment=assignment, student=student_profile).first()
        for assignment in assignments
    }
    
    return render(request, 'course_assignments.html', {
        'course': course,
        'assignments': assignments,
        'student_submissions': student_submissions,
        'current_date': current_date,
    })


from .forms import StudentAssignmentForm

from django.utils import timezone  

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    student_profile = get_object_or_404(Student, user=request.user)

    if request.method == 'POST':
        form = StudentAssignmentForm(request.POST, request.FILES)
        
        if form.is_valid():
            student_assignment, created = StudentAssignment.objects.get_or_create(
                assignment=assignment,
                student=student_profile,
                defaults={
                    'submission_status': 'Submitted',
                    'submission_date': timezone.now(),
                    'submission_file': form.cleaned_data['submission_file'],
                }
            )
            
            if not created:
                student_assignment.submission_file = form.cleaned_data['submission_file']
                student_assignment.submission_status = 'Submitted'
                student_assignment.submission_date = timezone.now()
                student_assignment.save()

            messages.success(request, 'Assignment submitted successfully.')
            return redirect('course_assignments', course_id=assignment.course.pk)
    else:
        form = StudentAssignmentForm()

    return redirect('course_assignments', course_id=assignment.course.pk)

@login_required
def upload_assignment(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()

            config.ASSIGNMENT_UPLOAD_NOTIFICATION = f"New assignment '{assignment.title}' has been uploaded to {course.course_name}."
            
            messages.success(request, 'Assignment uploaded successfully.')
            return JsonResponse({'success': True, 'assignment': {'title': assignment.title, 'description': assignment.description, 'file_url': assignment.assignment_file.url}})

        return JsonResponse({'success': False, 'errors': form.errors.as_json()})
    else:
        form = AssignmentForm()

    return render(request, 'upload_assignment.html', {'form': form, 'course': course})

from django.core.mail import send_mail
from django.http import HttpResponse
def forgot_password(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        try:
            student = Student.objects.get(student_id=student_id)
           
            student_details = StudentDetails.objects.get(student=student)
            dob = student_details.date_of_birth.strftime('%Y-%m-%d')  
            send_mail(
                'Your Password',
                f'Your password is: {dob}',
                'nayanima2102@gmail.com',  
                [student.email],
                fail_silently=False,
            )
            messages.success(request, 'An email has been sent with your password.')
            return redirect('login_student') 

        except Student.DoesNotExist:
            messages.error(request, 'Student ID not found.')
        except StudentDetails.DoesNotExist:
            messages.error(request, 'Student details not found.')

    return render(request, 'forgot_password.html')

def forgot_password_teacher(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        try:
            teacher = Teacher.objects.get(teacher_id=teacher_id)
            send_mail(
                'Your Password',
                f'Your password is: {teacher.password}',
                'nayanima2102@gmail.com',  
                [teacher.email],
                fail_silently=False,
            )
            messages.success(request, 'An email has been sent with your password.')
            return redirect('login_teacher') 

        except Teacher.DoesNotExist:
            messages.error(request, 'Teacher ID not found.')

    return render(request, 'forgot_password_teacher.html')
