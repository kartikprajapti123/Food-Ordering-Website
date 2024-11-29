from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_email_with_template(subject, recipient_email, template_name, context):
    html_message = render_to_string(template_name, context)
    
    try:
        send_mail(
            subject=subject,
            message='',  
            from_email=settings.DEFAULT_FROM_EMAIL,  
            recipient_list=[recipient_email],
            fail_silently=False,  
            html_message=html_message 
        )
        return True
    except Exception as e:
        # Log or handle the exception as needed
        print(f"Failed to send email: {e}")
        return False
