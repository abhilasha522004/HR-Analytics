
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from employee.models import Employee
from django.core.exceptions import ObjectDoesNotExist

# Login view 
def login_user(request):
    if request.method == "POST":
        id = request.POST["id"]
        password = request.POST["password"]
        user = authenticate(request, username=id, password=password)
        if user is not None:
            login(request, user)
            return redirect("/ems/dashboard")
        else:
            messages.error(request, "Invalid Credentials")
            return redirect("/")
    return render(request, "employee/Login.html")

# Logout view 
def logout_user(request):
    logout(request)
    return redirect("/")


def signup(request):
    if request.method == "POST":
        # Safely get form data with defaults
        employee_id = request.POST.get("id", "").strip()
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("cnfpass", "").strip()

        # Validate required fields
        if not employee_id:
            messages.error(request, "Employee ID is required")
            return redirect("/signup")
            
        if not password or not confirm_password:
            messages.error(request, "Password fields are required")
            return redirect("/signup")

        # Check password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("/signup")

        # Check if employee exists
        try:
            employee = Employee.objects.get(eID=employee_id)
        except ObjectDoesNotExist:
            messages.error(request, "Invalid Employee ID - please contact admin")
            return redirect("/signup")
        except Exception as e:
            messages.error(request, "System error, please try again")
            return redirect("/signup")

        # Check if user already exists
        if User.objects.filter(username=employee_id).exists():
            messages.info(request, "Employee already registered")
            return redirect("/signup")

        # Create new user
        try:
            user = User.objects.create_user(
                username=employee_id,
                password=password
            )
            messages.success(request, "Registered successfully! Please login.")
            return redirect("/")
        except Exception as e:
            messages.error(request, "Registration failed, please try again")
            return redirect("/signup")

    return render(request, "employee/signup.html")