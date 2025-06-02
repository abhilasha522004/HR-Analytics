from django.core.mail import send_mail
from django.conf import settings
from employee.models import Employee

def send_email_to_employees(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        getattr(settings, 'EMAIL_HOST_USER', None),  # From email (None for console backend)
        recipient_list,
        fail_silently=False,
    )

def get_all_employee_emails():
    return list(Employee.objects.values_list('email', flat=True)) 