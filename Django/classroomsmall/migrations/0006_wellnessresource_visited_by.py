# Generated by Django 5.1.1 on 2024-10-26 05:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroomsmall', '0005_alter_student_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='wellnessresource',
            name='visited_by',
            field=models.ManyToManyField(blank=True, related_name='visited_resources', to=settings.AUTH_USER_MODEL),
        ),
    ]
