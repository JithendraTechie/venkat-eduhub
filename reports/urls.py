from django.urls import path
from .views import course_report, student_payment_summary, export_student_excel, login_view, logout_view

urlpatterns = [
    path('', course_report),
    path('students/', student_payment_summary),
    path('students/export/', export_student_excel),

    path('login/', login_view),
    path('logout/', logout_view),
]