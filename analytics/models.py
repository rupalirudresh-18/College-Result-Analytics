from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    ADMISSION_QUOTA_CHOICES = [
        ('MGMT', 'Management'), ('GOV', 'Government'), ('NRI', 'NRI'), ('SNQ', 'SNQ'), ('OTHER', 'Other')
    ]
    ADMISSION_TYPE_CHOICES = [
        ('LATERAL', 'Lateral Entry'), ('REGULAR', 'Regular'), ('OTHER', 'Other')
    ]

    usn = models.CharField(max_length=20, unique=True, verbose_name='USN')
    name = models.CharField(max_length=100, verbose_name='Student Name')
    branch = models.CharField(max_length=100, verbose_name='Branch')
    batch = models.CharField(max_length=20, verbose_name='Batch')
    section = models.CharField(max_length=10, verbose_name='Section', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    admission_quota = models.CharField(max_length=20, choices=ADMISSION_QUOTA_CHOICES, blank=True, null=True)
    admission_type = models.CharField(max_length=20, choices=ADMISSION_TYPE_CHOICES, blank=True, null=True)
    actual_category = models.CharField(max_length=50, blank=True, null=True)
    seat_category_claimed = models.CharField(max_length=50, blank=True, null=True)
    seat_category_alloted = models.CharField(max_length=50, blank=True, null=True)
    domicile_state = models.CharField(max_length=100, blank=True, null=True)
    domicile_place = models.CharField(max_length=100, blank=True, null=True)
    cet_rank = models.CharField(max_length=20, blank=True, null=True, verbose_name='CET/COMEDK/DCET Rank')
    achievements = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usn} - {self.name}"

    def get_cgpa(self):
        results = self.semesterresult_set.all()
        if not results:
            return 0.0
        total_credits = sum(r.total_credits for r in results if r.total_credits)
        weighted_sum = sum(r.sgpa * r.total_credits for r in results if r.total_credits and r.sgpa)
        return round(weighted_sum / total_credits, 2) if total_credits else 0.0

    def has_backlog(self):
        return self.result_set.filter(pass_fail='F').exists()

    def backlog_count(self):
        return self.result_set.filter(pass_fail='F').count()

    class Meta:
        ordering = ['usn']


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='Subject Code')
    name = models.CharField(max_length=200, verbose_name='Subject Name')
    credits = models.FloatField(default=4, validators=[MinValueValidator(0), MaxValueValidator(10)])
    branch = models.CharField(max_length=100, blank=True, null=True)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)], blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']


class Result(models.Model):
    PASS_FAIL_CHOICES = [('P', 'Pass'), ('F', 'Fail'), ('A', 'Absent'), ('W', 'Withheld')]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    academic_year = models.CharField(max_length=20, blank=True, null=True)

    cie_marks = models.FloatField(blank=True, null=True, verbose_name='CIE Marks')
    see_marks = models.FloatField(blank=True, null=True, verbose_name='SEE Marks')
    total_marks = models.FloatField(blank=True, null=True)
    grade = models.CharField(max_length=5, blank=True, null=True)
    grade_point = models.FloatField(blank=True, null=True)
    pass_fail = models.CharField(max_length=1, choices=PASS_FAIL_CHOICES, default='P')

    class Meta:
        unique_together = ('student', 'subject', 'semester', 'academic_year')
        ordering = ['student', 'semester', 'subject']

    def __str__(self):
        return f"{self.student.usn} - {self.subject.code} - Sem {self.semester}"


class SemesterResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    academic_year = models.CharField(max_length=20, blank=True, null=True)
    sgpa = models.FloatField(default=0.0)
    total_credits = models.FloatField(default=0.0)
    credits_earned = models.FloatField(default=0.0)
    pass_fail = models.CharField(max_length=1, choices=[('P', 'Pass'), ('F', 'Fail')], default='P')

    class Meta:
        unique_together = ('student', 'semester', 'academic_year')
        ordering = ['student', 'semester']

    def __str__(self):
        return f"{self.student.usn} - Sem {self.semester} - SGPA {self.sgpa}"


class Backlog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.IntegerField()
    academic_year = models.CharField(max_length=20, blank=True, null=True)
    cleared = models.BooleanField(default=False)
    cleared_year = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'subject', 'semester')

    def __str__(self):
        return f"{self.student.usn} - {self.subject.code} backlog"


class NBAMetric(models.Model):
    branch = models.CharField(max_length=100)
    semester = models.IntegerField()
    academic_year = models.CharField(max_length=20)
    total_students = models.IntegerField(default=0)
    pass_count = models.IntegerField(default=0)
    avg_sgpa = models.FloatField(default=0.0)
    success_index = models.FloatField(default=0.0, verbose_name='Success Index (SI)')
    academic_performance_index = models.FloatField(default=0.0, verbose_name='Academic Performance Index (API)')
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('branch', 'semester', 'academic_year')

    def __str__(self):
        return f"NBA {self.branch} Sem {self.semester} {self.academic_year}"


class UploadLog(models.Model):
    STATUS_CHOICES = [('SUCCESS', 'Success'), ('PARTIAL', 'Partial'), ('FAILED', 'Failed')]
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_rows = models.IntegerField(default=0)
    valid_rows = models.IntegerField(default=0)
    invalid_rows = models.IntegerField(default=0)
    saved_rows = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SUCCESS')
    errors_json = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.filename} ({self.uploaded_at.strftime('%d %b %Y')})"
