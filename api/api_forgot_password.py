
import random
import string

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password,make_password
from visitors_app.models import user,roles,countries,states,cities,location,areas
from visitors_app.context_processors import my_constants
import os
from django.conf import settings
from visitors_app.views import date_time


class Userforgot_passwordView(APIView):
    def post(self, request):
        
        constants = my_constants(request)
        
        email = request.data.get('email','')
        
        if not email:
            return Response({"status": "false", "message": "Email id is required."})
        
                            
        user_exist = user.objects.filter(email = email,is_active=1,type='employee').first()

        if user_exist:
            
            new_password = generate_random_string()
            
            try:
                    send_fogot_password_email(user_exist, new_password,constants)
                    
            except Exception as e:
                
                return Response({"status": "false", "message": f"Error sending email: {str(e)}"})
            
            user_exist.password = make_password(new_password)
            
            user_exist.updated_at = date_time()
            
            user_exist.save()
            
            return Response({"status": "true", "message": "New password successfully sent to your email id."})
        
        else:
            
            return Response({"status": "false", "message": "Email ID does not exist."})


def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


def send_fogot_password_email(user, new_password,constants):
    subject = 'Forgot Password'
    template_name = 'api_templates\\forgot_password.html'
    message = render_to_string(template_name, {'new_password': new_password})
    plain_message = strip_tags(message)
    from_email = constants['From_Email']
    recipient_list = [user.email]
    mail = EmailMultiAlternatives(subject, plain_message, from_email, recipient_list)
    mail.attach_alternative(message, "text/html")

    try:
        mail.send()
        return Response({"status": "false", "message": "successfully sent to your email."})
        # print("forgot_password email sent successfully.")
    except Exception as e:
        return Response({"status": "false", "message": "Error sending registration email:{e}"})
        # print(f"Error sending registration email: {e}")
        