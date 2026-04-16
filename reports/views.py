from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum, Count, Q, Value, DecimalField
from django.db.models.functions import Coalesce
from datetime import datetime

from courses.models import Course
from enrollments.models import Enrollment
from fees.models import Payment

@login_required
def course_report(request):
    print("USER:", request.user)
    from enrollments.models import Enrollment
    from courses.models import Course
    from fees.models import Payment
    from django.db.models import Sum, Value, DecimalField
    from django.db.models.functions import Coalesce
    import json

    course_id = request.GET.get('course')
    start = request.GET.get('start')
    end = request.GET.get('end')

    courses = Course.objects.all()
    data = []

    for course in courses:

        # filter by selected course
        if course_id and str(course.id) != course_id:
            continue

        enrollments = Enrollment.objects.filter(course=course)

        # date filter on enrollments
        if start:
            enrollments = enrollments.filter(start_date__gte=start)
        if end:
            enrollments = enrollments.filter(start_date__lte=end)

        # payments filter
        payments = Payment.objects.filter(enrollment__course=course)

        if start:
            payments = payments.filter(date__gte=start)
        if end:
            payments = payments.filter(date__lte=end)

        # counts
        total_students = enrollments.count()
        active = enrollments.filter(status='active').count()
        completed = enrollments.filter(status='completed').count()

        # total fee
        total_fee = course.fee * total_students

        # total paid
        total_paid = payments.aggregate(
            v=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        )['v']

        data.append({
            'course': course.name,
            'students': total_students,
            'active': active,
            'completed': completed,
            'revenue': total_paid,
            'pending': total_fee - total_paid
        })

    # totals
    total_students_all = sum(d['students'] for d in data)
    total_revenue_all = sum(d['revenue'] for d in data)
    total_pending_all = sum(d['pending'] for d in data)

    # 🔥 chart data
    chart_labels = [d['course'] for d in data]
    chart_students = [d['students'] for d in data]
    chart_revenue = [float(d['revenue']) for d in data]

    return render(request, 'reports/course_report.html', {
        'data': data,
        'courses': courses,
        'total_students_all': total_students_all,
        'total_revenue_all': total_revenue_all,
        'total_pending_all': total_pending_all,

        # charts
        'chart_labels': json.dumps(chart_labels),
        'chart_students': json.dumps(chart_students),
        'chart_revenue': json.dumps(chart_revenue),
    })

@login_required
def student_payment_summary(request):
    from enrollments.models import Enrollment
    from fees.models import Payment
    from django.db.models import Sum, Value, DecimalField
    from django.db.models.functions import Coalesce

    search = request.GET.get('search')   # ✅ STEP 1

    enrollments = Enrollment.objects.select_related('student', 'course')

    if search:   # ✅ STEP 2
        enrollments = enrollments.filter(student__name__icontains=search)

    data = []

    for e in enrollments:
        total_fee = e.course.fee

        total_paid = Payment.objects.filter(
            enrollment=e
        ).aggregate(
            v=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        )['v']

        data.append({
            'student': e.student.name,
            'course': e.course.name,
            'total_fee': total_fee,
            'paid': total_paid,
            'pending': total_fee - total_paid
        })

    return render(request, 'reports/student_summary.html', {'data': data})


@login_required
def export_student_excel(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access Denied")
    import openpyxl
    from django.http import HttpResponse
    from enrollments.models import Enrollment
    from fees.models import Payment
    from django.db.models import Sum, Value, DecimalField
    from django.db.models.functions import Coalesce

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Student Payments"

    # Header
    ws.append(['Student', 'Course', 'Total Fee', 'Paid', 'Pending'])

    enrollments = Enrollment.objects.select_related('student', 'course')

    for e in enrollments:
        total_fee = e.course.fee

        total_paid = Payment.objects.filter(
            enrollment=e
        ).aggregate(
            v=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        )['v']

        ws.append([
            e.student.name,
            e.course.name,
            float(total_fee),
            float(total_paid),
            float(total_fee - total_paid)
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=student_report.xlsx'

    wb.save(response)
    return response

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')