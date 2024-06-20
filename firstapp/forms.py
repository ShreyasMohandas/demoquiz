from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User,Group
from django import forms


class RegisterUser(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','password1','password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            students_group = Group.objects.get(name='Students')
            user.groups.add(students_group)
        return user
    

class FileUpload(forms.Form):
    file=forms.FileField()
