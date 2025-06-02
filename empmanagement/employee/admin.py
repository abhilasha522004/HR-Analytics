from django.contrib import admin
from employee.models import Employee,Attendance,Notice, OfficeLocation
from django import forms

# Register your models here.
admin.site.register(Employee)
admin.site.register(Attendance)
admin.site.register(Notice)
admin.site.register(OfficeLocation)