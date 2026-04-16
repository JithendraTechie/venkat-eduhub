from django.contrib import admin

# Register your models here.
from .models import Student
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'guardian', 'joined_date')
    search_fields = ('name', 'phone')
    list_filter = ('year', 'joined_date')

admin.site.register(Student, StudentAdmin)