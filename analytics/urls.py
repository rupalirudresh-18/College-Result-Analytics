from django.urls import path
from . import views

urlpatterns = [
    path('upload/',              views.upload_results,     name='upload_results'),
    path('students/',            views.student_list,       name='student_list'),
    path('students/<str:usn>/',  views.student_profile,    name='student_profile'),
    path('course/',              views.course_analysis,    name='course_analysis'),
    path('category/',            views.category_analysis,  name='category_analysis'),
    path('backlog/',             views.backlog_view,        name='backlog_view'),
    path('nba/',                 views.nba_report,          name='nba_report'),

    # Subject views
    path('subjects/',                             views.subject_list,   name='subject_list'),
    path('subjects/<str:subject_code>/',          views.subject_detail, name='subject_detail'),
    path('toppers/', views.toppers, name='toppers'),
    # Exports
    path('export/nba/',                                  views.export_nba,          name='export_nba'),
    path('export/students/',                             views.export_students_csv,  name='export_students'),
    path('export/results/',                              views.export_results_csv,   name='export_results'),
    path('export/summary/',                              views.export_summary_csv,   name='export_summary'),
    path('export/pdf/',                                  views.export_pdf,           name='export_pdf'),
    path('export/subject/<str:subject_code>/csv/',       views.export_subject_csv,   name='export_subject_csv'),
    path('export/subject/<str:subject_code>/pdf/',       views.export_subject_pdf,   name='export_subject_pdf'),
    path('export/student/<str:usn>/pdf/',                views.export_student_pdf,   name='export_student_pdf'),
    path('download/sample/',                             views.download_sample_csv,  name='download_sample'),
]
