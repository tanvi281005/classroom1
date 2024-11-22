from django import forms

class StudentLoginForm(forms.Form):
    student_id = forms.IntegerField(label="Student ID")
    password = forms.CharField(widget=forms.PasswordInput, label="Date of Birth (YYYY-MM-DD)")

from .models import Assignment, StudentAssignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [ 'title', 'description', 'due_date', 'assignment_file']

class StudentAssignmentForm(forms.ModelForm):
    class Meta:
        model = StudentAssignment
        fields = ['submission_file']