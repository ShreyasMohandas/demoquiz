from typing import Any
from django.shortcuts import render,redirect,HttpResponse
from .forms import RegisterUser,FileUpload
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin,LoginRequiredMixin
from .models import *
from firstapp import rag
from django.http import FileResponse
from django.views.generic import CreateView,UpdateView,DeleteView,DetailView,ListView
import os
from django.conf import settings

# Create your views here.
def user_register(request):
    RegisterForm=RegisterUser()
    if request.method=='POST':
        RegisterForm=RegisterUser(request.POST)
        if RegisterForm.is_valid():
            RegisterForm.save()
            return redirect('firstapp:login')
        
    return render(request,'firstapp/register.html',{'RegisterForm':RegisterForm})

def user_login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password1')
        user=authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            if user.groups.filter(name='Teacher').exists():
                    teacher = Teacher.objects.get(name=user)
                    return redirect('firstapp:teacher_detail', pk=teacher.pk)
            elif user.groups.filter(name='Students').exists():
                try:
                    student = Students.objects.get(name=user) 
                    return redirect('firstapp:detail-student', pk=student.pk)
                except Students.DoesNotExist:
                    return HttpResponse("Your account is successfully registered, but you are not yet added to the classroom.")
    return render(request,'firstapp/login.html')

@login_required
def home(request):
    user=request.user
    if user.groups.filter(name='Teacher').exists():
                teacher = Teacher.objects.get(name=user)
                return redirect('firstapp:teacher_detail', pk=teacher.pk)
    elif user.groups.filter(name='Students').exists():
        try:
            student = Students.objects.get(name=user)
            return redirect('firstapp:detail-student', pk=student.pk)
        except Students.DoesNotExist:
            return HttpResponse("Your account is successfully registered, but you are not yet added to the classroom.")

@login_required
def user_logout(request):
    logout(request)
    return redirect('firstapp:login')


class addStudent(LoginRequiredMixin,PermissionRequiredMixin,CreateView):
    permission_required='firstapp.add_students'
    model=Students
    fields={'name','teacher'}

    

class teacherdata(LoginRequiredMixin,PermissionRequiredMixin,ListView):
    permission_required='firstapp.add_students'
    model=Teacher
    context_object_name='teachers'

class teacherdetail(LoginRequiredMixin,PermissionRequiredMixin,DetailView):
    permission_required='firstapp.add_students'
    model=Teacher

class studentdetail(LoginRequiredMixin,DetailView):
    model=Students

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context=super().get_context_data(**kwargs)
        student=self.get_object()
        tests=TestAttempt.objects.filter(student=student)
        attempted_tests = [attempt.test.id for attempt in tests]
        context["attempted_tests"]=attempted_tests
        return context


class studentUpdate(LoginRequiredMixin,PermissionRequiredMixin,UpdateView):
    permission_required='firstapp.change_students'
    model=Students
    fields={'name','description'}


def handle_uploaded_file(f):
    with open('modelrev2/media/documents/'+f.name, 'wb+') as destination:   
        for chunk in f.chunks(): 
            destination.write(chunk)  
    rag.start_embedding('modelrev2/media/documents/'+f.name)
    return f.name


def upload_file(request):
    if request.method=='POST':
        form=FileUpload(request.POST,request.FILES)
        if form.is_valid():
            file_path=handle_uploaded_file(request.FILES["file"])
            request.session['uploaded_file_path'] = file_path
            return redirect('firstapp:user-input')
    else:
        form=FileUpload()
    return render(request,'firstapp/upload_file.html',{'form':form})


def ask_question(request):
    if request.method=='POST':
        question=request.POST.get('question')
        return redirect('firstapp:quiz', question=question)
    return render(request,"firstapp/ask_question.html")



@login_required
def quiz(request,question):
    if request.method=='GET':
        request.session['test_name']=question
        question_list=rag.generate_quiz(question)
        request.session['gen_ques']=question_list

        teacher,_=Teacher.objects.get_or_create(name=request.user)
        Test.objects.create(
            teacher=teacher,
            test_name=request.session.get('test_name'),
            test_data=request.session.get('gen_ques'),
            file_path=request.session.get('uploaded_file_path')
        )
        del request.session['uploaded_file_path']
        return redirect('firstapp:teacher_detail',pk=teacher.pk)
    

def attend_quiz(request,test_id):
    if request.method=='GET':
        test=Test.objects.get(id=test_id)
        return render(request,"firstapp/quiz.html",context=test.test_data)
    elif request.method == 'POST':
        student,_=Students.objects.get_or_create(name=request.user)
        submitted_data=request.POST
        test=Test.objects.get(id=test_id)
        question_list=test.test_data
        obtained_marks=0
        topicstags=[]
        for i in range(1,len(question_list['questions'])+1):
            question_list['questions'][i-1].update({'answer_given_value':submitted_data['question--'+str(i)]})
            if submitted_data['question--'+str(i)] == question_list['questions'][i-1]['correct_answer']:
                question_list['questions'][i-1].update({'answer_given':'correct'})
                obtained_marks+=int(question_list['questions'][i-1]['marks'])
            else:
                question_list['questions'][i-1].update({'answer_given':'incorrect'})
                for i in question_list['questions'][i-1]['tags']:
                    if i not in topicstags:
                        topicstags.append(i)
                        Topics.objects.create(
                            student=student,
                            topic=i,
                            test=test
                        )
        test_marks=rag.calculate_total_marks(question_list)
        TestAttempt.objects.create(
            student=student,
            test=test,
            Submitted_data=question_list['questions'],
            test_marks=obtained_marks,
            test_total_marks=test_marks
        )

        return render(
            request,'firstapp/result_page.html',
                    {
                        'marks_obtained':obtained_marks,
                        'total_marks': test_marks,
                        'questions':question_list['questions'],
                        'preview':None,
                        'student_pk':student.name.pk
                    }
            )
    

def preview_test(request,id):
    student,_=Students.objects.get_or_create(name=request.user)
    test=TestAttempt.objects.get(student_id=student.id,test_id=id)
    return render(request,'firstapp/result_page.html',{'marks_obtained':test.test_marks,'total_marks': test.test_total_marks,'questions':test.Submitted_data,'preview':None,'student_pk':student.name.pk})


def download_file(request,file_path):
    file_abs_path = 'modelrev2/media/documents/'+file_path
    file= FileResponse(open(file_abs_path,'rb'))
    file['Content-Disposition'] = f'attachment; filename="{file_path}"'
    return file


def rectification_quiz(request,topic_id):
    student,_=Students.objects.get_or_create(name=request.user)
    if request.method=='GET':
        topic=Topics.objects.get(id=topic_id,student_id=student.id)
        test=Test.objects.get(id=topic.test_id)
        rag.start_embedding('modelrev2/media/documents/'+test.file_path)
        question_list=rag.generate_quiz("generate 15 questions with 7 questions easy, 5 questions medium and 3 questions hard level on "+topic.topic+" to master this topic")
        request.session['gen_ques']=question_list
        return render(request,"firstapp/quiz.html",context=question_list)
    elif request.method == 'POST':
        submitted_data=request.POST
        question_list=request.session.get('gen_ques')
        obtained_marks=0
        for i in range(1,len(question_list['questions'])+1):
            question_list['questions'][i-1].update({'answer_given_value':submitted_data['question--'+str(i)]})
            if submitted_data['question--'+str(i)] == question_list['questions'][i-1]['correct_answer']:
                question_list['questions'][i-1].update({'answer_given':'correct'})
                obtained_marks+=int(question_list['questions'][i-1]['marks'])
            else:
                question_list['questions'][i-1].update({'answer_given':'incorrect'})
        test_marks=rag.calculate_total_marks(question_list)
        print(obtained_marks,test_marks)
        if obtained_marks/test_marks>0.8:
            Topics.objects.filter(id=topic_id).delete()
        return render(
            request,'firstapp/result_page.html',
                    {
                        'marks_obtained':obtained_marks,
                        'total_marks': test_marks,
                        'questions':question_list['questions'],
                        'preview':None,
                        'student_pk':student.name.pk
                    }
            )

