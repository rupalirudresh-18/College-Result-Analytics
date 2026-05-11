from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usn', models.CharField(max_length=20, unique=True, verbose_name='USN')),
                ('name', models.CharField(max_length=100, verbose_name='Student Name')),
                ('branch', models.CharField(max_length=100, verbose_name='Branch')),
                ('batch', models.CharField(max_length=20, verbose_name='Batch')),
                ('section', models.CharField(blank=True, max_length=10, null=True, verbose_name='Section')),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1, null=True)),
                ('admission_quota', models.CharField(blank=True, choices=[('MGMT', 'Management'), ('GOV', 'Government'), ('NRI', 'NRI'), ('SNQ', 'SNQ'), ('OTHER', 'Other')], max_length=20, null=True)),
                ('admission_type', models.CharField(blank=True, choices=[('LATERAL', 'Lateral Entry'), ('REGULAR', 'Regular'), ('OTHER', 'Other')], max_length=20, null=True)),
                ('actual_category', models.CharField(blank=True, max_length=50, null=True)),
                ('seat_category_claimed', models.CharField(blank=True, max_length=50, null=True)),
                ('seat_category_alloted', models.CharField(blank=True, max_length=50, null=True)),
                ('domicile_state', models.CharField(blank=True, max_length=100, null=True)),
                ('domicile_place', models.CharField(blank=True, max_length=100, null=True)),
                ('cet_rank', models.CharField(blank=True, max_length=20, null=True, verbose_name='CET/COMEDK/DCET Rank')),
                ('achievements', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['usn']},
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='Subject Code')),
                ('name', models.CharField(max_length=200, verbose_name='Subject Name')),
                ('credits', models.FloatField(default=4, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('branch', models.CharField(blank=True, max_length=100, null=True)),
                ('semester', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
            ],
            options={'ordering': ['code']},
        ),
        migrations.CreateModel(
            name='UploadLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('total_rows', models.IntegerField(default=0)),
                ('valid_rows', models.IntegerField(default=0)),
                ('invalid_rows', models.IntegerField(default=0)),
                ('saved_rows', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('SUCCESS', 'Success'), ('PARTIAL', 'Partial'), ('FAILED', 'Failed')], default='SUCCESS', max_length=10)),
                ('errors_json', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('academic_year', models.CharField(blank=True, max_length=20, null=True)),
                ('cie_marks', models.FloatField(blank=True, null=True, verbose_name='CIE Marks')),
                ('see_marks', models.FloatField(blank=True, null=True, verbose_name='SEE Marks')),
                ('total_marks', models.FloatField(blank=True, null=True)),
                ('grade', models.CharField(blank=True, max_length=5, null=True)),
                ('grade_point', models.FloatField(blank=True, null=True)),
                ('pass_fail', models.CharField(choices=[('P', 'Pass'), ('F', 'Fail'), ('A', 'Absent'), ('W', 'Withheld')], default='P', max_length=1)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.subject')),
            ],
            options={'ordering': ['student', 'semester', 'subject']},
        ),
        migrations.CreateModel(
            name='SemesterResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('academic_year', models.CharField(blank=True, max_length=20, null=True)),
                ('sgpa', models.FloatField(default=0.0)),
                ('total_credits', models.FloatField(default=0.0)),
                ('credits_earned', models.FloatField(default=0.0)),
                ('pass_fail', models.CharField(choices=[('P', 'Pass'), ('F', 'Fail')], default='P', max_length=1)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.student')),
            ],
            options={'ordering': ['student', 'semester']},
        ),
        migrations.CreateModel(
            name='NBAMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(max_length=100)),
                ('semester', models.IntegerField()),
                ('academic_year', models.CharField(max_length=20)),
                ('total_students', models.IntegerField(default=0)),
                ('pass_count', models.IntegerField(default=0)),
                ('avg_sgpa', models.FloatField(default=0.0)),
                ('success_index', models.FloatField(default=0.0, verbose_name='Success Index (SI)')),
                ('academic_performance_index', models.FloatField(default=0.0, verbose_name='Academic Performance Index (API)')),
                ('computed_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Backlog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField()),
                ('academic_year', models.CharField(blank=True, max_length=20, null=True)),
                ('cleared', models.BooleanField(default=False)),
                ('cleared_year', models.CharField(blank=True, max_length=20, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.subject')),
            ],
        ),
        migrations.AddConstraint(
            model_name='result',
            constraint=models.UniqueConstraint(fields=['student', 'subject', 'semester', 'academic_year'], name='unique_result'),
        ),
        migrations.AlterUniqueTogether(
            name='semesterresult',
            unique_together={('student', 'semester', 'academic_year')},
        ),
        migrations.AlterUniqueTogether(
            name='nbametric',
            unique_together={('branch', 'semester', 'academic_year')},
        ),
        migrations.AlterUniqueTogether(
            name='backlog',
            unique_together={('student', 'subject', 'semester')},
        ),
    ]
