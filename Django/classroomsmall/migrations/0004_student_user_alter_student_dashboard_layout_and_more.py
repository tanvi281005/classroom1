# Generated by Django 5.1.1 on 2024-10-23 06:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroomsmall', '0003_alter_studentdetails_student'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='student',
            name='dashboard_layout',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='student',
            name='language_preference',
            field=models.CharField(help_text='Preferred language of the student.', max_length=50),
        ),
    ]
