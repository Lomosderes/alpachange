from django.contrib import admin
from .models import Teacher, Course, Review

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'department', 'average_rating')
    search_fields = ('first_name', 'last_name', 'department')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'course', 'user', 'is_anonymous', 'created_at')
    list_filter = ('is_anonymous', 'created_at', 'teacher')
    search_fields = ('comment', 'teacher__last_name', 'course__name')
