# Generated by Django 5.0.1 on 2024-08-09 22:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.OneToOneField(limit_choices_to={'groups__name': 'Teacher'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Students',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.OneToOneField(limit_choices_to={'groups__name': 'Students'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='firstapp.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_data', models.JSONField()),
                ('display_name', models.CharField(max_length=100)),
                ('test_name', models.CharField(max_length=100)),
                ('test_total_marks', models.PositiveBigIntegerField()),
                ('file_path', models.CharField(max_length=1000)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='firstapp.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Topics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=200)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='firstapp.students')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topic_test', to='firstapp.test')),
            ],
        ),
        migrations.CreateModel(
            name='TestAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Submitted_data', models.JSONField(default=dict, null=True)),
                ('test_marks', models.PositiveBigIntegerField(default=0)),
                ('attempt_start', models.DateTimeField()),
                ('attempt_end', models.DateTimeField(blank=True, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_history', to='firstapp.students')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test', to='firstapp.test')),
            ],
            options={
                'unique_together': {('student', 'test')},
            },
        ),
    ]
