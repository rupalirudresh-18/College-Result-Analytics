from django.contrib import admin
from .models import Student, Subject, Result, SemesterResult, Backlog, NBAMetric, UploadLog


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['usn', 'name', 'branch', 'batch', 'section', 'gender', 'admission_quota']
    search_fields = ['usn', 'name']
    list_filter = ['branch', 'batch', 'gender', 'admission_quota']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'branch', 'semester']
    search_fields = ['code', 'name']
    list_filter = ['branch', 'semester']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'semester', 'cie_marks', 'see_marks', 'total_marks', 'grade', 'pass_fail']
    list_filter = ['semester', 'pass_fail', 'student__branch']
    search_fields = ['student__usn', 'student__name', 'subject__code']


@admin.register(SemesterResult)
class SemesterResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'semester', 'sgpa', 'total_credits', 'credits_earned', 'pass_fail']
    list_filter = ['semester', 'pass_fail']


@admin.register(Backlog)
class BacklogAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'semester', 'cleared', 'cleared_year']
    list_filter = ['cleared', 'semester']


@admin.register(NBAMetric)
class NBAMetricAdmin(admin.ModelAdmin):
    list_display = ['branch', 'semester', 'academic_year', 'total_students', 'pass_count', 'success_index', 'academic_performance_index']
    list_filter = ['branch', 'semester']


@admin.register(UploadLog)
class UploadLogAdmin(admin.ModelAdmin):
    list_display = ['filename', 'uploaded_at', 'total_rows', 'valid_rows', 'invalid_rows', 'saved_rows', 'status']
    list_filter = ['status']
