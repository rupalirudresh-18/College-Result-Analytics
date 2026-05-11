"""
Management command to load demo/sample data into the database.
Usage: python manage.py load_demo_data
"""
from django.core.management.base import BaseCommand
from analytics.utils import parse_csv, save_valid_rows


DEMO_CSV = """USN,Name,Branch,Semester,Batch,Section,Gender,Admission_Quota,Admission_Type,Actual_Category,Seat_Category_Claimed,Seat_Category_Alloted,Domicile_State,Domicile_Place,CET_Rank,Achievements,Subject_Code,Subject_Name,Credits,CIE,SEE,Total,Grade,Grade_Point,Pass_Fail,Academic_Year
1RV21CS001,Aditya Kumar,Computer Science,3,2021-25,A,M,GOV,REGULAR,GM,GM,GM,Karnataka,Bangalore,12345,Best Project Award,21CS31,Data Structures,4,38,52,90,O,10,P,2022-23
1RV21CS001,Aditya Kumar,Computer Science,3,2021-25,A,M,GOV,REGULAR,GM,GM,GM,Karnataka,Bangalore,12345,Best Project Award,21CS32,Design and Analysis of Algorithms,3,35,48,83,A,9,P,2022-23
1RV21CS001,Aditya Kumar,Computer Science,3,2021-25,A,M,GOV,REGULAR,GM,GM,GM,Karnataka,Bangalore,12345,Best Project Award,21CS33,Computer Organization,3,30,42,72,B,8,P,2022-23
1RV21CS001,Aditya Kumar,Computer Science,3,2021-25,A,M,GOV,REGULAR,GM,GM,GM,Karnataka,Bangalore,12345,Best Project Award,21MA31,Mathematics III,4,32,44,76,B,8,P,2022-23
1RV21CS002,Priya Sharma,Computer Science,3,2021-25,A,F,GOV,REGULAR,SC,SC,SC,Karnataka,Mysore,45678,Sports Captain,21CS31,Data Structures,4,40,55,95,O,10,P,2022-23
1RV21CS002,Priya Sharma,Computer Science,3,2021-25,A,F,GOV,REGULAR,SC,SC,SC,Karnataka,Mysore,45678,Sports Captain,21CS32,Design and Analysis of Algorithms,3,28,35,63,C,7,P,2022-23
1RV21CS002,Priya Sharma,Computer Science,3,2021-25,A,F,GOV,REGULAR,SC,SC,SC,Karnataka,Mysore,45678,Sports Captain,21CS33,Computer Organization,3,35,45,80,A,9,P,2022-23
1RV21CS002,Priya Sharma,Computer Science,3,2021-25,A,F,GOV,REGULAR,SC,SC,SC,Karnataka,Mysore,45678,Sports Captain,21MA31,Mathematics III,4,38,50,88,O,10,P,2022-23
1RV21CS003,Ravi Bhat,Computer Science,3,2021-25,A,M,MGMT,REGULAR,GM,GM,GM,Karnataka,Mangalore,67890,,21CS31,Data Structures,4,25,30,55,D,6,P,2022-23
1RV21CS003,Ravi Bhat,Computer Science,3,2021-25,A,M,MGMT,REGULAR,GM,GM,GM,Karnataka,Mangalore,67890,,21CS32,Design and Analysis of Algorithms,3,20,22,42,F,0,F,2022-23
1RV21CS003,Ravi Bhat,Computer Science,3,2021-25,A,M,MGMT,REGULAR,GM,GM,GM,Karnataka,Mangalore,67890,,21CS33,Computer Organization,3,28,36,64,C,7,P,2022-23
1RV21CS003,Ravi Bhat,Computer Science,3,2021-25,A,M,MGMT,REGULAR,GM,GM,GM,Karnataka,Mangalore,67890,,21MA31,Mathematics III,4,22,28,50,D,6,P,2022-23
1RV21CS004,Sneha Iyer,Computer Science,3,2021-25,B,F,GOV,LATERAL,OBC,OBC,OBC,Tamil Nadu,Chennai,11111,Cultural Fest Winner,21CS31,Data Structures,4,36,50,86,A,9,P,2022-23
1RV21CS004,Sneha Iyer,Computer Science,3,2021-25,B,F,GOV,LATERAL,OBC,OBC,OBC,Tamil Nadu,Chennai,11111,Cultural Fest Winner,21CS32,Design and Analysis of Algorithms,3,33,46,79,B,8,P,2022-23
1RV21CS004,Sneha Iyer,Computer Science,3,2021-25,B,F,GOV,LATERAL,OBC,OBC,OBC,Tamil Nadu,Chennai,11111,Cultural Fest Winner,21CS33,Computer Organization,3,38,52,90,O,10,P,2022-23
1RV21CS004,Sneha Iyer,Computer Science,3,2021-25,B,F,GOV,LATERAL,OBC,OBC,OBC,Tamil Nadu,Chennai,11111,Cultural Fest Winner,21MA31,Mathematics III,4,40,58,98,O,10,P,2022-23
1RV21EC001,Rahul Verma,Electronics,3,2021-25,A,M,MGMT,REGULAR,GM,GM,GM,Karnataka,Hubli,23456,,21EC31,Analog Circuits,4,25,30,55,D,6,P,2022-23
1RV21EC001,Rahul Verma,Electronics,3,2021-25,A,M,MGMT,REGULAR,GM,GM,GM,Karnataka,Hubli,23456,,21EC32,Signals and Systems,3,20,25,45,F,0,F,2022-23
1RV21EC001,Rahul Verma,Electronics,3,2021-25,A,M,MGMT,REGULAR,GM,GM,GM,Karnataka,Hubli,23456,,21EC33,Digital Electronics,3,30,40,70,B,8,P,2022-23
1RV21EC001,Rahul Verma,Electronics,3,2021-25,A,M,MGMT,REGULAR,GM,GM,GM,Karnataka,Hubli,23456,,21MA31,Mathematics III,4,28,35,63,C,7,P,2022-23
1RV21EC002,Divya Nair,Electronics,3,2021-25,A,F,GOV,REGULAR,ST,ST,ST,Kerala,Kochi,34567,NSS Volunteer,21EC31,Analog Circuits,4,38,50,88,O,10,P,2022-23
1RV21EC002,Divya Nair,Electronics,3,2021-25,A,F,GOV,REGULAR,ST,ST,ST,Kerala,Kochi,34567,NSS Volunteer,21EC32,Signals and Systems,3,35,46,81,A,9,P,2022-23
1RV21EC002,Divya Nair,Electronics,3,2021-25,A,F,GOV,REGULAR,ST,ST,ST,Kerala,Kochi,34567,NSS Volunteer,21EC33,Digital Electronics,3,32,44,76,B,8,P,2022-23
1RV21EC002,Divya Nair,Electronics,3,2021-25,A,F,GOV,REGULAR,ST,ST,ST,Kerala,Kochi,34567,NSS Volunteer,21MA31,Mathematics III,4,30,42,72,B,8,P,2022-23
1RV21ME001,Kiran Patil,Mechanical,3,2021-25,A,M,GOV,REGULAR,GM,GM,GM,Maharashtra,Pune,56789,,21ME31,Fluid Mechanics,4,35,45,80,A,9,P,2022-23
1RV21ME001,Kiran Patil,Mechanical,3,2021-25,A,M,GOV,REGULAR,GM,GM,GM,Maharashtra,Pune,56789,,21ME32,Thermodynamics,3,32,40,72,B,8,P,2022-23
1RV21ME001,Kiran Patil,Mechanical,3,2021-25,A,M,GOV,REGULAR,GM,GM,GM,Maharashtra,Pune,56789,,21ME33,Machine Design,3,28,36,64,C,7,P,2022-23
1RV21ME001,Kiran Patil,Mechanical,3,2021-25,A,M,GOV,REGULAR,GM,GM,GM,Maharashtra,Pune,56789,,21MA31,Mathematics III,4,25,32,57,D,6,P,2022-23
1RV21ME002,Ananya Desai,Mechanical,3,2021-25,A,F,MGMT,REGULAR,OBC,OBC,OBC,Karnataka,Belgaum,78901,Basketball State Level,21ME31,Fluid Mechanics,4,28,35,63,C,7,P,2022-23
1RV21ME002,Ananya Desai,Mechanical,3,2021-25,A,F,MGMT,REGULAR,OBC,OBC,OBC,Karnataka,Belgaum,78901,Basketball State Level,21ME32,Thermodynamics,3,22,28,50,D,6,P,2022-23
1RV21ME002,Ananya Desai,Mechanical,3,2021-25,A,F,MGMT,REGULAR,OBC,OBC,OBC,Karnataka,Belgaum,78901,Basketball State Level,21ME33,Machine Design,3,18,20,38,F,0,F,2022-23
1RV21ME002,Ananya Desai,Mechanical,3,2021-25,A,F,MGMT,REGULAR,OBC,OBC,OBC,Karnataka,Belgaum,78901,Basketball State Level,21MA31,Mathematics III,4,30,38,68,C,7,P,2022-23
1RV21CS001,Aditya Kumar,Computer Science,4,2021-25,A,M,GOV,REGULAR,GM,GM,GM,Karnataka,Bangalore,12345,Best Project Award,21CS41,Operating Systems,4,36,50,86,A,9,P,2023-24
1RV21CS001,Aditya Kumar,Computer Science,4,2021-25,A,M,GOV,REGULAR,GM,GM,GM,Karnataka,Bangalore,12345,Best Project Award,21CS42,Database Management,3,38,52,90,O,10,P,2023-24
1RV21CS001,Aditya Kumar,Computer Science,4,2021-25,A,M,GOV,REGULAR,GM,GM,GM,Karnataka,Bangalore,12345,Best Project Award,21CS43,Computer Networks,3,34,46,80,A,9,P,2023-24
1RV21CS002,Priya Sharma,Computer Science,4,2021-25,A,F,GOV,REGULAR,SC,SC,SC,Karnataka,Mysore,45678,Sports Captain,21CS41,Operating Systems,4,40,55,95,O,10,P,2023-24
1RV21CS002,Priya Sharma,Computer Science,4,2021-25,A,F,GOV,REGULAR,SC,SC,SC,Karnataka,Mysore,45678,Sports Captain,21CS42,Database Management,3,35,48,83,A,9,P,2023-24
1RV21CS002,Priya Sharma,Computer Science,4,2021-25,A,F,GOV,REGULAR,SC,SC,SC,Karnataka,Mysore,45678,Sports Captain,21CS43,Computer Networks,3,30,42,72,B,8,P,2023-24
"""


class Command(BaseCommand):
    help = 'Load demo student and result data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n📚 Loading demo data...'))

        result = parse_csv(DEMO_CSV.encode('utf-8'))

        self.stdout.write(f'  Total rows: {result["total"]}')
        self.stdout.write(f'  Valid rows: {len(result["valid"])}')
        self.stdout.write(f'  Invalid rows: {len(result["invalid"])}')

        if result['invalid']:
            for err in result['invalid']:
                self.stdout.write(self.style.WARNING(f'  Row {err["row"]}: {err["errors"]}'))

        if result['valid']:
            saved = save_valid_rows(result['valid'])
            self.stdout.write(self.style.SUCCESS(f'\n✅ Saved {saved} records successfully!'))
            self.stdout.write('   Open http://127.0.0.1:8000 to explore the data.\n')
        else:
            self.stdout.write(self.style.ERROR('No valid rows to save.'))
