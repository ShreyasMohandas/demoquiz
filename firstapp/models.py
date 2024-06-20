from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Teacher(models.Model):
    name = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'Teacher'})

    def get_absolute_url(self):
        return reverse('firstapp:teacher_detail', kwargs={'pk': self.name.pk})

    def __str__(self):
        return self.name.username

class Students(models.Model):
    name = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'Students'})
    teacher = models.ForeignKey(Teacher, related_name='students',on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    def get_absolute_url(self):
        return reverse('firstapp:detail-student', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name.username

class Test(models.Model):
    teacher = models.ForeignKey(Teacher, related_name='tests', on_delete=models.CASCADE)
    test_data=models.JSONField()
    test_name=models.CharField(max_length=100)
    file_path=models.CharField(max_length=1000)


    def __str__(self):
        return self.test_name
    

class TestAttempt(models.Model):
    student=models.ForeignKey(Students,related_name='test_history',on_delete=models.CASCADE)
    test=models.ForeignKey(Test,related_name='test',on_delete=models.CASCADE)
    Submitted_data=models.JSONField()
    test_marks=models.PositiveBigIntegerField()
    test_total_marks=models.PositiveBigIntegerField()

    class Meta:
        unique_together = ('student' , 'test')

    def __str__(self) -> str:
        return self.test.test_name
    

class Topics(models.Model):
    student = models.ForeignKey(Students, related_name='topics', on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    test=models.ForeignKey(Test,related_name='topic_test',on_delete=models.CASCADE)

    def __str__(self):
        return self.topic

