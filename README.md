# 📊 Result Analytics — College Academic Performance System

A Django-based academic analytics platform designed to manage student records, analyze performance, track backlogs, and generate NBA metrics reports.

---

## 🚀 Project Overview

This project provides a data-driven system to:

- Manage student academic records efficiently  
- Automate SGPA & CGPA calculations  
- Analyze performance across subjects, branches, and categories  
- Track backlogs and identify trends  
- Generate NBA reports (SI & API)  
- Export data in CSV and PDF formats  

---

## ✨ Features

### Student Management
- Stores USN, name, branch, batch, quota, category, etc.

### CSV Upload & Validation
- Bulk upload using CSV  
- Dry-run preview before saving  
- Row-wise error reporting  

### Automated Calculations
- SGPA & CGPA (credit-based)

### Dashboard
- Chart.js-based visual insights  
- Overall performance overview  

### Course Analysis
- Subject-wise, semester-wise, branch-wise stats  

### Category Analysis
- Gender, quota, and category-based insights  

### Backlog Tracking
- Tracks failed subjects  
- Identifies student risk trends  

### NBA Metrics
- Success Index (SI)  
- Academic Performance Index (API)  

### Export
- CSV (students, results, summary)  
- PDF reports  

---

## 🧠 NBA Metrics

- **Success Index (SI)** = (Pass Count / Total Students) × 100  
- **Academic Performance Index (API)** = (SI × Avg SGPA) / 10  

---

## 🛠️ Tech Stack

- Backend: Django 4.x, SQLite  
- Data: pandas, openpyxl  
- Frontend: Bootstrap 5, Chart.js  
- PDF: WeasyPrint  

---

## ⚙️ Setup

```bash
cd result_analytics
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

## 🎯 Course Outcome (CO) Mapping — Detailed

### **CO1: Understanding of MVT (Model-View-Template) Architecture**
**Implementation in Project:**
- Designed a clear separation of concerns using Django’s MVT pattern:
  - **Models:** Represent student data, results, backlog, and NBA metrics  
  - **Views:** Handle business logic such as CSV processing, SGPA/CGPA calculation, and analytics  
  - **Templates:** Render dashboards, reports, and visualizations  
- Implemented structured URL routing for modules like upload, dashboard, course analysis, category analysis, backlog tracking, and exports  

**Outcome Achieved:**
- Demonstrated the ability to build scalable and maintainable web applications using proper architecture  

**SDG Mapping:** SDG 4.1 – Quality Education  

---

### **CO2: Development of Models and Forms with Validation**
**Implementation in Project:**
- Created robust Django models:
  - `Student`, `Subject`, `Result`, `SemesterResult`, `Backlog`, `NBAMetric`, `UploadLog`
- Developed forms for CSV upload with:
  - Field validation  
  - Data type checking  
  - Missing/incorrect value detection  
- Implemented **dry-run validation** before saving data to the database  

**Outcome Achieved:**
- Ensured data integrity, reliability, and error-free data handling in large datasets  

**SDG Mapping:** SDG 4.6 – Literacy and Numeracy Skills  

---

### **CO3: Template Design and Frontend Integration**
**Implementation in Project:**
- Used **template inheritance** (`base.html`) for consistent UI across all pages  
- Built responsive dashboards using **Bootstrap 5**  
- Integrated **Chart.js** for:
  - Performance visualization  
  - Category comparisons  
  - Trend analysis  
- Designed clean and user-friendly interfaces for better usability  

**Outcome Achieved:**
- Demonstrated ability to create interactive and visually appealing web interfaces  

**SDG Mapping:** SDG 4.A – Inclusive and Effective Learning Environments  

---

### **CO4: Generation of Non-HTML Outputs**
**Implementation in Project:**
- Implemented data export features:
  - CSV exports (students, results, summaries, NBA metrics)  
  - PDF reports using WeasyPrint (with browser fallback)  
- Automated calculation of:
  - Success Index (SI)  
  - Academic Performance Index (API)  
- Enabled filtered data export for specific queries  

**Outcome Achieved:**
- Demonstrated capability to generate structured reports for real-world institutional use  

**SDG Mapping:** SDG 16.6 – Effective and Accountable Institutions  

---

### **CO5: Asynchronous Updates using AJAX (Bonus Implementation)**
**Implementation in Project:**
- Integrated AJAX for:
  - Dynamic chart updates without page reload  
  - Real-time filtering and data visualization  
- Improved user experience by reducing load times and avoiding full page refresh  

**Outcome Achieved:**
- Demonstrated understanding of modern web techniques for responsive and efficient applications  

**SDG Mapping:** SDG 9.C – Universal Access to Information and Communication Technology  

---