from django.shortcuts import redirect, render, get_object_or_404
from .forms import *
from .forms import NoticeForm
from employee.models import Employee,Attendance,Notice,workAssignments
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from employee.utils import send_email_to_employees, get_all_employee_emails
from .models import OfficeLocation
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
import pandas as pd
import joblib
import os
from django.conf import settings
import docx # Import python-docx
import PyPDF2 # Import PyPDF2
import sys
# from employee.ml_models.custom_ml_classes import DynamicOutlierHandler
# import joblib
# sys.modules['__main__'].DynamicOutlierHandler = DynamicOutlierHandler


# Create your views here.
@login_required(login_url='/')
def dashboard(request):
    info = Employee.objects.filter(eID=request.user.username)
    return render(request,"employee/index.html",{'info':info})
    
@login_required(login_url='/')
def attendance(request):
    office = OfficeLocation.objects.first()
    employee = Employee.objects.filter(eID=request.user.username).first()
    attendance_history = Attendance.objects.filter(eId=employee).order_by('-date') if employee else []
    
    # Calculate attendance counts
    office_count = sum(1 for att in attendance_history if att.type == 'Office')
    remote_count = sum(1 for att in attendance_history if att.type == 'Remote')
    total_count = len(attendance_history)

    message = ''
    if request.method == 'POST':
        att_type = request.POST.get('att_type')
        if att_type in ['Office', 'Remote'] and employee:
            # Check if attendance already marked for today
            today = timezone.now().date()
            if not Attendance.objects.filter(eId=employee, date=today).exists():
                Attendance.objects.create(eId=employee, type=att_type)
                message = f"Attendance marked as {att_type}."
                # Re-fetch history and counts after marking
                attendance_history = Attendance.objects.filter(eId=employee).order_by('-date') if employee else []
                office_count = sum(1 for att in attendance_history if att.type == 'Office')
                remote_count = sum(1 for att in attendance_history if att.type == 'Remote')
                total_count = len(attendance_history)
            else:
                 message = "Attendance already marked for today."
        
    return render(request, "employee/attendance.html", {
        "office": office,
        "attendance_history": attendance_history,
        "message": message,
        "office_count": office_count,
        "remote_count": remote_count,
        "total_count": total_count,
    })    

@login_required(login_url='/')
def notice(request):
    notices  = Notice.objects.all()
    if request.method == 'POST':
        # Assuming you have a NoticeForm for posting notices
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save()
            subject = "New Notice Posted"
            message = f"A new notice titled '{notice.title}' has been posted."
            recipient_list = get_all_employee_emails()
            send_email_to_employees(subject, message, recipient_list)
            messages.success(request, 'Notice posted and emails sent!')
    else:
        form = NoticeForm()
    return render(request,"employee/notice.html",{"notices":notices, "form": form})

@login_required(login_url='/')
def noticedetail(request,id):
    noticedetail = Notice.objects.get(Id=id)
    return render(request,"employee/noticedetail.html",{"noticedetail":noticedetail})

@login_required(login_url='/')
def assignWork(request):
    context = {}
    initialData = {
        "assignerId": request.user.username,
    }
    if request.method == "POST":
        form = workform(request.POST, initial=initialData)
        if form.is_valid():
            currentTaskerId = request.POST["taskerId"]
            currentUserId = request.user.username
            if currentTaskerId == currentUserId:
                messages.error(request, "Invalid ID Selected...")
            else:
                work = form.save()
                # Send email to assigned employee
                subject = "New Work Assigned"
                message = f"You have been assigned new work: {work.work}"
                recipient_list = [work.taskerId.email]
                send_email_to_employees(subject, message, recipient_list)
                messages.success(request, "Work is successfully assigned!")
                return redirect("assignwork")  # Redirect to clear the form
    else:
        form = workform(initial=initialData)
    context["form"] = form
    return render(request, "employee/workassign.html", context)

@login_required(login_url='/')
def mywork(request):
    work = workAssignments.objects.filter(taskerId=request.user.username)
    return render(request,"employee/mywork.html",{"work":work})

@login_required(login_url='/')
def workdetails(request,wid):
    workdetails = workAssignments.objects.get(id=wid);
    return render(request,"employee/workdetails.html",{"workdetails":workdetails})

@login_required(login_url='/')
def makeRequest(request):
    context={}
    initialData = {
        "requesterId" : request.user.username,
    }
    flag = ""
    requestForm = makeRequestForm(request.POST or None, initial=initialData)
    if request.method == 'POST':
        requestForm = makeRequestForm(request.POST)
        if requestForm.is_valid():
            currentRequesterId = request.POST["destinationEmployeeId"]
            currentUserId = request.user.username
            if currentRequesterId == currentUserId:
                flag="Invalid ID Selected..."
            else:
                flag="Request Submitted"
                req = requestForm.save()
                # Send email to destination employee
                subject = "New Request Issued"
                message = f"A new request has been issued by {req.requesterId.firstName}."
                recipient_list = [req.destinationEmployeeId.email]
                send_email_to_employees(subject, message, recipient_list)
    context['requestForm']=requestForm
    context['flag'] = flag
    return render(request,"employee/request.html",context)

@login_required(login_url='/')
def viewRequest(request):
    requests = Requests.objects.filter(destinationEmployeeId=request.user.username)
    return render(request,"employee/viewRequest.html",{"requests":requests})

@login_required(login_url='/')
def requestdetails(request,rid):
    requestdetail = Requests.objects.get(id=rid)
    return render(request,"employee/requestdetails.html",{"requestdetail":requestdetail})

@login_required(login_url='/')
def assignedworklist(request):
    works = workAssignments.objects.filter(assignerId=request.user.username).all()
    return render(request,"employee/assignedworklist.html",{"works":works})

@login_required(login_url='/')
def deletework(request, wid):
    obj = get_object_or_404(workAssignments, id=wid)
    obj.delete()
    return render(request,"employee/assignedworklist.html")

@login_required(login_url='/')
def updatework(request,wid):
    work = workAssignments.objects.get(id=wid)
    form = workform(request.POST or None, instance=work)
    flag = ""
    if form.is_valid():
        currentTaskerId = request.POST["taskerId"]
        currentUserId = request.user.username
        if currentTaskerId == currentUserId:
            flag="Invalid ID Selected..."
        else:
            flag = "Work Updated Successfully!!"
            form.save()
    return render(request,"employee/updatework.html", {'currentWork': work, "filledForm": form, "flag":flag})

# @login_required(login_url='/')
# @user_passes_test(lambda u: u.is_superuser)
# def attrition_prediction(request):
#     if not request.user.is_superuser:
#         return render(request, '403.html')

#     # Paths
#     hr_model_path = os.path.join(settings.BASE_DIR, 'employee', 'ml_models', 'hr_model.pkl')
#     data_path = os.path.join(settings.BASE_DIR, 'employee', 'ml_models', 'Modified_HR_Employee_Attrition_Data1.csv')

#     predictions = []
#     error_message = None

#     try:
#         # Load model and dataset
#         hr_model = joblib.load(hr_model_path)
#         df = pd.read_csv(data_path)

#         # Make predictions
#         predictions = hr_model.predict(df)
#         df['Turnover_Probability'] = predictions

#         # Count predictions
#         attrition_count = sum(predictions == 1)
#         no_attrition_count = sum(predictions == 0)
#         total_employees = len(predictions)

#         # Data for pie chart
#         chart_data = {
#             'labels': ['Not Leaving', 'Leaving'],
#             'data': [int(no_attrition_count), int(attrition_count)],
#         }

#     except FileNotFoundError:
#         error_message = "Model or data file not found. Please check that 'hr_model.pkl' and the CSV are in the correct path."
#     except Exception as e:
#         error_message = f"Error during prediction: {e}"

#     return render(request, "employee/attrition_prediction.html", {
#         'predictions': predictions,
#         'chart_data': chart_data if 'chart_data' in locals() else None,
#         'error_message': error_message,
#         'total_employees': total_employees if 'total_employees' in locals() else 0,
#     })


# @login_required(login_url='/')
# def course_recommendation(request):
#     recommended_courses = None
#     error_message = None
#     course_input = ''

#     # Define paths to pipeline and data files
#     pipeline_path = os.path.join(settings.BASE_DIR, 'employee', 'ml_models', 'course_pipeline.pkl')
#     courses_data_path = os.path.join(settings.BASE_DIR, 'employee', 'ml_models', 'cleaned_courses.csv')

#     try:
#         # Load the pipeline and courses data
#         pipeline = joblib.load(pipeline_path)
#         courses_df = pd.read_csv(courses_data_path)

#         if request.method == 'POST':
#             course_input = request.POST.get('course_input', '')
#             if course_input:
#                 # --- Placeholder for Course Recommendation Logic ---
#                 # This is where you would use the loaded pipeline and courses_df
#                 # to find recommendations based on course_input.
#                 # The exact logic depends on your model and data.
                
#                 # Example placeholder logic: find courses matching keywords in input
#                 recommended_courses = courses_df[courses_df['course_name'].str.contains(course_input, case=False, na=False)].to_dict('records')
#                 # You would replace this with logic using your actual ML pipeline
#                 # recommended_courses = your_recommendation_function(pipeline, courses_df, course_input)
#                 # --------------------------------------------------
#             else:
#                 error_message = "Please enter some text for course recommendation."

#     except FileNotFoundError:
#         error_message = "Course ML pipeline or data file not found. Please ensure 'course_pipeline.pkl' and 'cleaned_courses.csv' are in the 'employee/ml_models/' directory."
#     except Exception as e:
#         error_message = f"An error occurred during course recommendation: {e}"

#     return render(request, "employee/course_recommendation.html", {
#         'recommended_courses': recommended_courses,
#         'error_message': error_message,
#         'course_input': course_input,
#     })

@login_required(login_url='/')
def ats_checker(request):
    ats_score = None
    error_message = None
    skills_input = ''
    resume_text = ''

    if request.method == 'POST':
        skills_input = request.POST.get('skills_input', '')
        if 'resume_file' in request.FILES:
            resume_file = request.FILES['resume_file']
            
            # --- Logic for Reading Resume Content based on File Type ---
            try:
                file_extension = os.path.splitext(resume_file.name)[1].lower()
                
                if file_extension == '.pdf':
                    # Read PDF file
                    reader = PyPDF2.PdfReader(resume_file)
                    resume_text = ''.join([page.extract_text() for page in reader.pages])
                elif file_extension == '.docx':
                    # Read DOCX file
                    document = docx.Document(resume_file)
                    resume_text = '\n'.join([paragraph.text for paragraph in document.paragraphs])
                elif file_extension == '.txt':
                    # Read plain text file
                    resume_text = resume_file.read().decode('utf-8')
                else:
                    error_message = "Unsupported file type. Please upload a .pdf, .docx, or .txt file."

                # --- Placeholder for ATS Checking Logic (using resume_text) ---
                # This is where you would compare the skills_input to the resume_text
                # and calculate an ATS score or matching percentage.
                # The exact logic depends on your requirements.

                if not error_message and skills_input and resume_text:
                    # Simple example: count how many skills appear in the resume text
                    required_skills = [skill.strip() for skill in skills_input.split(',')]
                    matching_skills_count = sum(skill.lower() in resume_text.lower() for skill in required_skills)
                    total_skills = len(required_skills)
                    
                    if total_skills > 0:
                         ats_score = (matching_skills_count / total_skills) * 100
                         ats_score = round(ats_score, 2) # Round to 2 decimal places
                    else:
                         ats_score = 0 # No skills provided

                elif not error_message and not skills_input:
                     error_message = "Please provide required skills."
                elif not error_message and not resume_text:
                     error_message = "Could not extract text from the resume file."

                # ---------------------------------------------------------

            except Exception as e:
                error_message = f"Error reading resume file or processing: {e}"
        else:
            error_message = "Please upload a resume file."

    return render(request, "employee/ats_checker.html", {
        'ats_score': ats_score,
        'error_message': error_message,
        'skills_input': skills_input,
    })