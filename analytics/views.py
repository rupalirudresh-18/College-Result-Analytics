import json
import csv
import io
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Avg, Count, Q, Sum
from django.contrib import messages
from django.template.loader import render_to_string


class SafeJSONEncoder(json.JSONEncoder):
    """Convert Decimal/float safely so Chart.js always gets numbers, not strings."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def to_json(data):
    """Serialize data ensuring all numeric types stay numeric (not strings)."""
    return json.dumps(data, cls=SafeJSONEncoder)

from .models import Student, Subject, Result, SemesterResult, Backlog, NBAMetric, UploadLog
from .forms import CSVUploadForm, FilterForm, StudentFilterForm
from .utils import parse_csv, save_valid_rows, compute_nba_metrics, get_sample_csv_content


def dashboard(request):
    total_students = Student.objects.count()
    total_branches = Student.objects.values('branch').distinct().count()
    total_results = Result.objects.count()

    pass_count = SemesterResult.objects.filter(pass_fail='P').values('student').distinct().count()
    fail_count = Student.objects.filter(result__pass_fail='F').distinct().count()
    backlog_students = Student.objects.filter(backlog__cleared=False).distinct().count()

    recent_uploads = UploadLog.objects.order_by('-uploaded_at')[:5]

    # Branch-wise student count
    branch_data = list(Student.objects.values('branch').annotate(count=Count('id')).order_by('-count'))

    # Semester-wise average SGPA
    sgpa_data = list(
        SemesterResult.objects.values('semester')
        .annotate(avg=Avg('sgpa'))
        .order_by('semester')
    )

    # Pass/Fail pie data
    total_sem_results = SemesterResult.objects.count()
    total_pass_sr = SemesterResult.objects.filter(pass_fail='P').count()
    total_fail_sr = total_sem_results - total_pass_sr

    context = {
        'total_students': total_students,
        'total_branches': total_branches,
        'total_results': total_results,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'backlog_students': backlog_students,
        'recent_uploads': recent_uploads,
        'branch_data_json': to_json(branch_data),
        'sgpa_data_json': to_json([{'semester': d['semester'], 'avg': round(float(d['avg'] or 0), 2)} for d in sgpa_data]),
        'pass_fail_json': to_json({'pass': total_pass_sr, 'fail': total_fail_sr}),
    }
    return render(request, 'analytics/dashboard.html', context)


def upload_results(request):
    form = CSVUploadForm()
    preview = None
    sample_csv = get_sample_csv_content()

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            confirm = form.cleaned_data.get('confirm_save', False)
            content = csv_file.read()
            result = parse_csv(content)

            if confirm and result['valid']:
                saved = save_valid_rows(result['valid'])
                UploadLog.objects.create(
                    filename=csv_file.name,
                    total_rows=result['total'],
                    valid_rows=len(result['valid']),
                    invalid_rows=len(result['invalid']),
                    saved_rows=saved,
                    status='SUCCESS' if not result['invalid'] else 'PARTIAL',
                    errors_json=json.dumps(result['invalid'][:50])
                )
                messages.success(request, f"✅ Saved {saved} records successfully!")
                return redirect('upload_results')

            preview = result

    upload_logs = UploadLog.objects.order_by('-uploaded_at')[:10]
    return render(request, 'analytics/upload.html', {
        'form': form,
        'preview': preview,
        'upload_logs': upload_logs,
        'sample_csv': sample_csv,
    })


def student_list(request):
    form = StudentFilterForm(request.GET)
    students = Student.objects.all()

    q = request.GET.get('q', '').strip()
    branch = request.GET.get('branch', '').strip()
    batch = request.GET.get('batch', '').strip()

    if q:
        students = students.filter(Q(usn__icontains=q) | Q(name__icontains=q))
    if branch:
        students = students.filter(branch__icontains=branch)
    if batch:
        students = students.filter(batch__icontains=batch)

    # Attach CGPA to each student
    for s in students:
        s.cgpa = s.get_cgpa()
        s.backlog_cnt = s.backlog_count()

    branches = Student.objects.values_list('branch', flat=True).distinct().order_by('branch')
    batches = Student.objects.values_list('batch', flat=True).distinct().order_by('batch')

    return render(request, 'analytics/student_list.html', {
        'students': students,
        'form': form,
        'branches': branches,
        'batches': batches,
        'total': students.count(),
    })


def student_profile(request, usn):
    student = get_object_or_404(Student, usn=usn)
    sem_results = SemesterResult.objects.filter(student=student).order_by('semester')
    backlogs = Backlog.objects.filter(student=student).select_related('subject')

    # Per-semester subject results
    semester_data = []
    for sr in sem_results:
        results = Result.objects.filter(
            student=student,
            semester=sr.semester,
            academic_year=sr.academic_year
        ).select_related('subject').order_by('subject__code')

        # add computed credits_earned per subject
        for r in results:
            if r.pass_fail == 'P':  # or your pass value
                r.computed_credits_earned = float(r.subject.credits or 0)
            else:
                 r.computed_credits_earned = 0

        semester_data.append({
            'sem_result': sr,
            'results': results,
        })

    # SGPA trend
    sgpa_trend = [{'sem': sr.semester, 'sgpa': sr.sgpa} for sr in sem_results]

    cgpa = student.get_cgpa()

    return render(request, 'analytics/student_profile.html', {
        'student': student,
        'sem_results': sem_results,
        'semester_data': semester_data,
        'backlogs': backlogs,
        'cgpa': cgpa,
        'sgpa_trend_json': to_json(sgpa_trend),
    })


def course_analysis(request):
    form = FilterForm(request.GET)
    branch = request.GET.get('branch', '').strip()
    semester = request.GET.get('semester', '').strip()
    academic_year = request.GET.get('academic_year', '').strip()

    sr_qs = SemesterResult.objects.all()
    if branch:
        sr_qs = sr_qs.filter(student__branch__icontains=branch)
    if semester:
        sr_qs = sr_qs.filter(semester=semester)
    if academic_year:
        sr_qs = sr_qs.filter(academic_year__icontains=academic_year)

    # Branch-wise stats
    branch_stats = list(
        sr_qs.values('student__branch')
        .annotate(
            total=Count('student', distinct=True),
            passes=Count('student', distinct=True, filter=Q(pass_fail='P')),
            avg_sgpa=Avg('sgpa'),
        ).order_by('student__branch')
    )
    for b in branch_stats:
        b['pass_pct'] = round((b['passes'] / b['total']) * 100, 1) if b['total'] else 0
        b['fail_pct'] = round(100 - b['pass_pct'], 1)
        b['avg_sgpa'] = round(b['avg_sgpa'] or 0, 2)

    # Semester-wise stats
    sem_stats = list(
        sr_qs.values('semester')
        .annotate(
            total=Count('student', distinct=True),
            passes=Count('student', distinct=True, filter=Q(pass_fail='P')),
            avg_sgpa=Avg('sgpa'),
        ).order_by('semester')
    )
    for s in sem_stats:
        s['pass_pct'] = round((s['passes'] / s['total']) * 100, 1) if s['total'] else 0
        s['avg_sgpa'] = round(s['avg_sgpa'] or 0, 2)

    # Subject-wise pass rate
    subject_stats = list(
        Result.objects.values('subject__code', 'subject__name')
        .annotate(
            total=Count('id'),
            passes=Count('id', filter=Q(pass_fail='P')),
            avg_marks=Avg('total_marks'),
        ).order_by('subject__code')
    )
    for s in subject_stats:
        s['pass_pct'] = round((s['passes'] / s['total']) * 100, 1) if s['total'] else 0
        s['avg_marks'] = round(s['avg_marks'] or 0, 1)

    branches_list = Student.objects.values_list('branch', flat=True).distinct()

    return render(request, 'analytics/course_dashboard.html', {
        'form': form,
        'branch_stats': branch_stats,
        'sem_stats': sem_stats,
        'subject_stats': subject_stats,
        'branch_stats_json': to_json(branch_stats),
        'sem_stats_json': to_json(sem_stats),
        'branches_list': branches_list,
        'filters': {'branch': branch, 'semester': semester, 'academic_year': academic_year},
    })


def category_analysis(request):
    quota_stats = list(
        SemesterResult.objects.values('student__admission_quota')
        .annotate(
            total=Count('student', distinct=True),
            passes=Count('student', distinct=True, filter=Q(pass_fail='P')),
            avg_sgpa=Avg('sgpa'),
        ).order_by('student__admission_quota')
    )
    for q in quota_stats:
        q['pass_pct'] = round((q['passes'] / q['total']) * 100, 1) if q['total'] else 0
        q['avg_sgpa'] = round(q['avg_sgpa'] or 0, 2)
        q['label'] = q['student__admission_quota'] or 'Not Specified'

    category_stats = list(
        SemesterResult.objects.values('student__actual_category')
        .annotate(
            total=Count('student', distinct=True),
            passes=Count('student', distinct=True, filter=Q(pass_fail='P')),
            avg_sgpa=Avg('sgpa'),
        ).order_by('student__actual_category')
    )
    for c in category_stats:
        c['pass_pct'] = round((c['passes'] / c['total']) * 100, 1) if c['total'] else 0
        c['avg_sgpa'] = round(c['avg_sgpa'] or 0, 2)
        c['label'] = c['student__actual_category'] or 'Not Specified'

    gender_stats = list(
        SemesterResult.objects.values('student__gender')
        .annotate(
            total=Count('student', distinct=True),
            avg_sgpa=Avg('sgpa'),
        )
    )

    return render(request, 'analytics/category_comparison.html', {
        'quota_stats': quota_stats,
        'category_stats': category_stats,
        'gender_stats': gender_stats,
        'quota_json': to_json(quota_stats),
        'category_json': to_json(category_stats),
    })


def backlog_view(request):
    branch = request.GET.get('branch', '').strip()
    semester = request.GET.get('semester', '').strip()

    backlogs = Backlog.objects.filter(cleared=False).select_related('student', 'subject')
    if branch:
        backlogs = backlogs.filter(student__branch__icontains=branch)
    if semester:
        backlogs = backlogs.filter(semester=semester)

    # Student-wise backlog count
    student_backlogs = (
        backlogs.values('student__usn', 'student__name', 'student__branch', 'student__batch')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Semester-wise backlog trend
    sem_backlog = list(
        backlogs.values('semester').annotate(count=Count('id')).order_by('semester')
    )

    branches_list = Student.objects.values_list('branch', flat=True).distinct()

    return render(request, 'analytics/backlog.html', {
        'backlogs': backlogs[:100],
        'student_backlogs': student_backlogs[:50],
        'sem_backlog': sem_backlog,
        'sem_backlog_json': to_json(sem_backlog),
        'total_backlog': backlogs.count(),
        'total_backlog_students': backlogs.values('student').distinct().count(),
        'branches_list': branches_list,
        'filters': {'branch': branch, 'semester': semester},
    })


def nba_report(request):
    compute_nba_metrics()
    metrics = NBAMetric.objects.all().order_by('branch', 'semester')

    branch = request.GET.get('branch', '').strip()
    if branch:
        metrics = metrics.filter(branch__icontains=branch)

    branches_list = NBAMetric.objects.values_list('branch', flat=True).distinct()

    chart_data = list(metrics.values('branch', 'semester', 'success_index', 'academic_performance_index', 'avg_sgpa'))
    # Ensure all float fields are proper Python floats, not Decimal
    for row in chart_data:
        row['success_index'] = float(row['success_index'] or 0)
        row['academic_performance_index'] = float(row['academic_performance_index'] or 0)
        row['avg_sgpa'] = float(row['avg_sgpa'] or 0)

    return render(request, 'analytics/nba_report.html', {
        'metrics': metrics,
        'branches_list': branches_list,
        'chart_data_json': to_json(chart_data),
        'filters': {'branch': branch},
    })


def export_nba(request):
    compute_nba_metrics()
    metrics = NBAMetric.objects.all().order_by('branch', 'semester')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="nba_metrics.csv"'
    writer = csv.writer(response)
    writer.writerow(['Branch', 'Semester', 'Academic Year', 'Total Students', 'Pass Count',
                     'Avg SGPA', 'Success Index (SI)', 'Academic Performance Index (API)'])
    for m in metrics:
        writer.writerow([m.branch, m.semester, m.academic_year, m.total_students,
                         m.pass_count, m.avg_sgpa, m.success_index, m.academic_performance_index])
    return response


def export_students_csv(request):
    branch = request.GET.get('branch', '')
    semester = request.GET.get('semester', '')
    students = Student.objects.all()
    if branch:
        students = students.filter(branch__icontains=branch)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['USN', 'Name', 'Branch', 'Batch', 'Section', 'Gender',
                     'Admission Quota', 'Admission Type', 'Category', 'CGPA', 'Backlogs'])
    for s in students:
        writer.writerow([s.usn, s.name, s.branch, s.batch, s.section or '',
                         s.get_gender_display() if s.gender else '',
                         s.admission_quota or '', s.admission_type or '',
                         s.actual_category or '', s.get_cgpa(), s.backlog_count()])
    return response


def export_results_csv(request):
    branch = request.GET.get('branch', '')
    semester = request.GET.get('semester', '')

    results = Result.objects.select_related('student', 'subject').all()
    if branch:
        results = results.filter(student__branch__icontains=branch)
    if semester:
        results = results.filter(semester=semester)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="results_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['USN', 'Name', 'Branch', 'Semester', 'Subject Code', 'Subject Name',
                     'CIE', 'SEE', 'Total', 'Grade', 'Grade Point', 'Pass/Fail'])
    for r in results:
        writer.writerow([r.student.usn, r.student.name, r.student.branch, r.semester,
                         r.subject.code, r.subject.name, r.cie_marks or '', r.see_marks or '',
                         r.total_marks or '', r.grade or '', r.grade_point or '', r.pass_fail])
    return response


def export_summary_csv(request):
    branch_stats = list(
        SemesterResult.objects.values('student__branch', 'semester')
        .annotate(
            total=Count('student', distinct=True),
            passes=Count('student', distinct=True, filter=Q(pass_fail='P')),
            avg_sgpa=Avg('sgpa'),
        ).order_by('student__branch', 'semester')
    )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="summary_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Branch', 'Semester', 'Total Students', 'Pass Count', 'Fail Count', 'Pass %', 'Avg SGPA'])
    for b in branch_stats:
        passes = b['passes']
        total = b['total']
        fails = total - passes
        pass_pct = round((passes / total) * 100, 1) if total else 0
        writer.writerow([b['student__branch'], b['semester'], total, passes, fails, pass_pct,
                         round(b['avg_sgpa'] or 0, 2)])
    return response


def export_pdf(request):
    """
    PDF export with three-tier fallback:
    1. xhtml2pdf  (pure Python, works on Windows/Mac/Linux — pip install xhtml2pdf)
    2. WeasyPrint (Linux preferred, needs GTK libs)
    3. Browser print-friendly HTML page (always works, no extra install)
    """
    report_type = request.GET.get('type', 'summary')

    branch_stats = list(
        SemesterResult.objects.values('student__branch', 'semester')
        .annotate(
            total=Count('student', distinct=True),
            passes=Count('student', distinct=True, filter=Q(pass_fail='P')),
            avg_sgpa=Avg('sgpa'),
        ).order_by('student__branch', 'semester')
    )
    for b in branch_stats:
        b['pass_pct'] = round((b['passes'] / b['total']) * 100, 1) if b['total'] else 0
        b['fail_pct'] = round(100 - b['pass_pct'], 1)
        b['avg_sgpa'] = round(float(b['avg_sgpa'] or 0), 2)

    template_ctx = {
        'branch_stats': branch_stats,
        'report_type': report_type,
        'print_mode': False,
    }

    # ── Tier 1: xhtml2pdf (pure Python, Windows-friendly) ──────────────────
    try:
        from xhtml2pdf import pisa
        html_string = render_to_string('analytics/pdf_report.html', template_ctx)
        buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html_string, dest=buffer)
        if not pisa_status.err:
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="result_analytics_report.pdf"'
            return response
        # pisa had an error — fall through to next tier
    except ImportError:
        pass

    # ── Tier 2: WeasyPrint (works on Linux/macOS with GTK libs) ────────────
    try:
        from weasyprint import HTML as WP_HTML
        html_string = render_to_string('analytics/pdf_report.html', template_ctx)
        pdf_bytes = WP_HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="result_analytics_report.pdf"'
        return response
    except Exception:
        pass

    # ── Tier 3: Browser print-friendly HTML fallback (always works) ─────────
    template_ctx['print_mode'] = True
    return render(request, 'analytics/pdf_report.html', template_ctx)


def download_sample_csv(request):
    content = get_sample_csv_content()
    response = HttpResponse(content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample_results.csv"'
    return response


# ── Subject Detail View ──────────────────────────────────────────────────────

def subject_list(request):
    """List all subjects with quick stats."""
    branch = request.GET.get('branch', '').strip()
    semester = request.GET.get('semester', '').strip()

    subjects = Subject.objects.all().order_by('branch', 'semester', 'code')
    if branch:
        subjects = subjects.filter(branch__icontains=branch)
    if semester:
        subjects = subjects.filter(semester=semester)

    subject_stats = []
    for subj in subjects:
        results = Result.objects.filter(subject=subj)
        total = results.count()
        passes = results.filter(pass_fail='P').count()
        fails = results.filter(pass_fail='F').count()
        avg_marks = results.aggregate(a=Avg('total_marks'))['a']
        avg_gp = results.aggregate(a=Avg('grade_point'))['a']
        subject_stats.append({
            'subject': subj,
            'total': total,
            'passes': passes,
            'fails': fails,
            'pass_pct': round((passes / total) * 100, 1) if total else 0,
            'avg_marks': round(float(avg_marks or 0), 1),
            'avg_gp': round(float(avg_gp or 0), 2),
        })

    branches_list = Subject.objects.values_list('branch', flat=True).distinct().order_by('branch')
    return render(request, 'analytics/subject_list.html', {
        'subject_stats': subject_stats,
        'branches_list': branches_list,
        'filters': {'branch': branch, 'semester': semester},
    })


def subject_detail(request, subject_code):
    """Detailed per-subject view: all students, marks, grades, pass/fail."""
    subject = get_object_or_404(Subject, code=subject_code)

    results = Result.objects.filter(subject=subject).select_related('student').order_by('student__usn')

    # Grade distribution
    grade_dist = {}
    GRADE_ORDER = ['O', 'A+', 'A', 'B+', 'B', 'C', 'D', 'P', 'F']
    for g in GRADE_ORDER:
        grade_dist[g] = results.filter(grade=g).count()

    total = results.count()
    passes = results.filter(pass_fail='P').count()
    fails = results.filter(pass_fail='F').count()
    avg_cie = results.aggregate(a=Avg('cie_marks'))['a']
    avg_see = results.aggregate(a=Avg('see_marks'))['a']
    avg_total = results.aggregate(a=Avg('total_marks'))['a']
    avg_gp = results.aggregate(a=Avg('grade_point'))['a']

    stats = {
        'total': total,
        'passes': passes,
        'fails': fails,
        'pass_pct': round((passes / total) * 100, 1) if total else 0,
        'avg_cie': round(float(avg_cie or 0), 1),
        'avg_see': round(float(avg_see or 0), 1),
        'avg_total': round(float(avg_total or 0), 1),
        'avg_gp': round(float(avg_gp or 0), 2),
    }

    grade_dist_json = to_json([{'grade': g, 'count': grade_dist[g]} for g in GRADE_ORDER if grade_dist[g] > 0])

    return render(request, 'analytics/subject_detail.html', {
        'subject': subject,
        'results': results,
        'stats': stats,
        'grade_dist': grade_dist,
        'grade_dist_json': grade_dist_json,
        'grade_order': GRADE_ORDER,
    })


def export_subject_csv(request, subject_code):
    subject = get_object_or_404(Subject, code=subject_code)
    results = Result.objects.filter(subject=subject).select_related('student').order_by('student__usn')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{subject_code}_results.csv"'
    writer = csv.writer(response)
    writer.writerow(['USN', 'Name', 'Branch', 'Batch', 'Subject Code', 'Subject Name',
                     'Credits', 'CIE', 'SEE', 'Total', 'Grade', 'Grade Point', 'Pass/Fail'])
    for r in results:
        writer.writerow([
            r.student.usn, r.student.name, r.student.branch, r.student.batch,
            subject.code, subject.name, subject.credits,
            r.cie_marks or '', r.see_marks or '', r.total_marks or '',
            r.grade or '', r.grade_point or '', r.get_pass_fail_display()
        ])
    return response


def export_subject_pdf(request, subject_code):
    """Export subject-wise report as PDF using WeasyPrint first."""
    subject = get_object_or_404(Subject, code=subject_code)
    results = Result.objects.filter(subject=subject).select_related('student').order_by('student__usn')

    total = results.count()
    passes = results.filter(pass_fail='P').count()
    fails = total - passes
    avg_total = results.aggregate(a=Avg('total_marks'))['a']

    template_ctx = {
        'report_type': 'subject',
        'subject': subject,
        'results': results,
        'total': total,
        'passes': passes,
        'fails': fails,
        'pass_pct': round((passes / total) * 100, 1) if total else 0,
        'avg_total': round(float(avg_total or 0), 1),
        'print_mode': False,
        'logo_url': True,
    }

    # Tier 1: WeasyPrint
    try:
        from weasyprint import HTML
        html_string = render_to_string('analytics/pdf_subject_report.html', template_ctx)
        pdf_file = HTML(
            string=html_string,
            base_url=request.build_absolute_uri('/')
        ).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{subject_code}_report.pdf"'
        return response

    except Exception as e:
        print("WeasyPrint subject PDF failed:", str(e))

    # Tier 2: Browser HTML fallback
    template_ctx['print_mode'] = True
    return render(request, 'analytics/pdf_subject_report.html', template_ctx)


def export_student_pdf(request, usn):
    """Export individual student report as PDF using WeasyPrint first."""
    student = get_object_or_404(Student, usn=usn)
    sem_results = SemesterResult.objects.filter(student=student).order_by('semester')

    semester_data = []
    cumulative_credits = 0

    for sr in sem_results:
        results = Result.objects.filter(
            student=student,
            semester=sr.semester,
            academic_year=sr.academic_year
        ).select_related('subject').order_by('subject__code')

        # NEW: compute per-subject earned credits for the PDF
        for r in results:
            if r.pass_fail == 'P':  # or your pass value
                r.computed_credits_earned = float(r.subject.credits or 0)
            else:
                r.computed_credits_earned = 0

        cumulative_credits += float(sr.credits_earned or 0)

        semester_data.append({
            'sem_result': sr,
            'results': results,
        })

    backlogs = Backlog.objects.filter(
        student=student,
        cleared=False
    ).select_related('subject')

    cgpa = student.get_cgpa()

    template_ctx = {
        'report_type': 'student',
        'student': student,
        'sem_results': sem_results,
        'semester_data': semester_data,
        'backlogs': backlogs,
        'cgpa': cgpa,
        'cumulative_credits': cumulative_credits,
        'print_mode': False,
        'logo_url': True,
        'qr_url': None,
    }

    # Tier 1: WeasyPrint
    try:
        from weasyprint import HTML
        html_string = render_to_string('analytics/pdf_student_report.html', template_ctx)
        pdf_file = HTML(
            string=html_string,
            base_url=request.build_absolute_uri('/')
        ).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{usn}_report.pdf"'
        return response

    except Exception as e:
        print("WeasyPrint failed:", str(e))

    # Tier 2: Browser fallback
    template_ctx['print_mode'] = True
    return render(request, 'analytics/pdf_student_report.html', template_ctx)

def toppers(request):
    branch = request.GET.get('branch', '').strip()
    batch  = request.GET.get('batch', '').strip()
    top_n  = int(request.GET.get('top_n', 10))

    students = Student.objects.all()
    if branch:
        students = students.filter(branch__icontains=branch)
    if batch:
        students = students.filter(batch__icontains=batch)

    topper_list = []
    for s in students:
        cgpa = s.get_cgpa()
        if cgpa > 0:
            sem_results = SemesterResult.objects.filter(student=s).order_by('semester')
            best_sgpa = max((sr.sgpa for sr in sem_results), default=0)
            topper_list.append({
                'student': s,
                'cgpa': cgpa,
                'best_sgpa': round(best_sgpa, 2),
                'backlogs': s.backlog_count(),
                'sem_count': sem_results.count(),
            })

    topper_list = sorted(topper_list, key=lambda x: x['cgpa'], reverse=True)

    branch_toppers = {}
    for t in topper_list:
        br = t['student'].branch
        if br not in branch_toppers:
            branch_toppers[br] = t

    overall_top = topper_list[:top_n]

    branches_list = Student.objects.values_list('branch', flat=True).distinct().order_by('branch')
    batches_list  = Student.objects.values_list('batch',  flat=True).distinct().order_by('batch')

    cgpa_dist = {'9-10': 0, '8-9': 0, '7-8': 0, '6-7': 0, 'below 6': 0}
    for t in topper_list:
        c = t['cgpa']
        if c >= 9:   cgpa_dist['9-10'] += 1
        elif c >= 8: cgpa_dist['8-9']  += 1
        elif c >= 7: cgpa_dist['7-8']  += 1
        elif c >= 6: cgpa_dist['6-7']  += 1
        else:        cgpa_dist['below 6'] += 1

    return render(request, 'analytics/toppers.html', {
        'overall_top': overall_top,
        'branch_toppers': branch_toppers,
        'topper_list': topper_list,
        'total_ranked': len(topper_list),
        'branches_list': branches_list,
        'batches_list': batches_list,
        'cgpa_dist_json': to_json([{'range': k, 'count': v} for k, v in cgpa_dist.items()]),
        'filters': {'branch': branch, 'batch': batch, 'top_n': top_n},
    })
