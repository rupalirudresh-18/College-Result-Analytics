from django import forms


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Upload CSV File',
        help_text='Upload a CSV file with student result data.',
        widget=forms.FileInput(attrs={'accept': '.csv', 'class': 'form-control'})
    )
    confirm_save = forms.BooleanField(
        required=False,
        label='Save valid records to database',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class FilterForm(forms.Form):
    SEMESTER_CHOICES = [('', 'All Semesters')] + [(i, f'Semester {i}') for i in range(1, 9)]

    branch = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science'})
    )
    semester = forms.ChoiceField(
        required=False,
        choices=SEMESTER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    batch = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2021-25'})
    )
    academic_year = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2022-23'})
    )


class StudentFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by USN or Name'})
    )
    branch = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Branch'})
    )
    batch = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Batch'})
    )
    semester = forms.ChoiceField(
        required=False,
        choices=[('', 'All')] + [(i, f'Sem {i}') for i in range(1, 9)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
