from django.contrib import admin
from .models import *

admin.site.register(Students)
admin.site.register(Teacher)
admin.site.register(Test)
admin.site.register(TestAttempt)
admin.site.register(Topics)