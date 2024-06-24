from django.urls import path,include
from firstapp import views

app_name = 'firstapp'

urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('register/',views.user_register,name='register'),
    path('add-student/',views.addStudent.as_view(),name='add-student'),
    path('update-student/<int:pk>/',views.studentUpdate.as_view(),name='update-student'),
    path('list-teachers/',views.teacherdata.as_view(),name='list-teachers'),
    path('teacher/<int:pk>/', views.teacherdetail.as_view(), name='teacher_detail'),
    path('students/<int:pk>/',views.studentdetail.as_view(),name='detail-student'),
    path("ask-question/",views.ask_question,name="user-input"),
    path('upload-file/',views.upload_file,name='upload-file'),
    path('quiz/<str:question>/', views.quiz, name='quiz'),
    path('attend-test/<int:test_id>',views.attend_quiz,name='attend-test'),
    path('improvement-test/<int:topic_id>',views.rectification_quiz,name='improvement-test'),
    path('preview-test/<int:id>/student/<int:stud_id>/',views.preview_test,name='preview-test'),
    path('download-file/<path:file_path>',views.download_file,name='download-file'),
]