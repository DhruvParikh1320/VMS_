import datetime

from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
# Create your views here.
from django.contrib import messages
from .models import user,appointment,auto_email,safety_training,appointment_reject
from django.contrib.auth.hashers import check_password ,make_password
from django.contrib.auth import authenticate, login
from django.core.files.images import get_image_dimensions
from .context_processors import my_constants
from django.db import connection
from django.shortcuts import get_object_or_404
from django.core import signing
from django.urls import reverse
import base64
import os
from PIL import Image
import io
from django.template.loader import render_to_string
from visitor_management import settings
from requests.auth import HTTPBasicAuth
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives
import json
from django.http import JsonResponse
def home(request):
    return redirect('gate_keeper')
    # return HttpResponse('hiiiiiii')

def date_time():
    now = datetime.datetime.now()
    date_time =now.strftime("%y-%m-%d %H:%M:%S")
    return date_time
def generate_vms_string():
    now = datetime.datetime.now()
    vms_string = now.strftime("VMS%d%m%y%H%M%S")
    return vms_string
def register(request, encrypted_appointment_id):
    redirect_url = reverse('register', args=[encrypted_appointment_id])
    constants = my_constants(request)
    database_name = constants['database_name']
    from_email = constants['From_Email']
    try:
        appointment_id = signing.loads(encrypted_appointment_id)
        appointment_id = int(appointment_id)
    except Exception as e:
        messages.error(request, 'Invalid appointment ID.')
        return redirect(redirect_url)
    
    appointmentes = get_object_or_404(appointment, id=appointment_id)
    if appointmentes.status == 'check out':
        message = 'Your Appointment is closed.'
        return render(request, 'registration_form/thank_you.html',{'message':message,'appointment_id':appointment_id})
    
    
    all_employee_id = appointmentes.employee_id
    all_visitor_id = appointmentes.visitors_id
    
    # if user.objects.filter(id=all_visitor_id).exists():
    #     visitor = user.objects.get(id=all_visitor_id)
    #     if visitor.first_name:
    #         message = 'You have been already Registered.'
    #         return render(request, 'registration_form/thank_you.html',{'message':message})
    if all_employee_id:
        sql_query = f'''
            SELECT * FROM {database_name}.users WHERE id = %s
        '''
        with connection.cursor() as cursor:
            cursor.execute(sql_query, [all_employee_id])
            user_data = cursor.fetchone()
            if user_data:
                columns = [col[0] for col in cursor.description]  # Get column names
                user_data_dict = dict(zip(columns, user_data))  # Convert to dictionary
                # Process the user_data_dict as needed
            else:
                messages.error(request, 'No user found for the given ID.')
    if all_visitor_id:
        sql_query_visitor = f'''
            SELECT * FROM {database_name}.users WHERE id = %s
        '''
        with connection.cursor() as cursor:
            cursor.execute(sql_query_visitor, [all_visitor_id])
            visitor_data = cursor.fetchone()
            if visitor_data:
                columns = [col[0] for col in cursor.description]  # Get column names
                user_visitor = dict(zip(columns, visitor_data))
            else:
                messages.error(request, 'No visitor found for the given visitor ID.')
    

    if request.method == 'POST':
        
        firstname = request.POST.get('Firstname', '')

        lastname = request.POST.get('Lastname', '')

        email = request.POST.get('Email', '')

        # password = request.POST.get('Password', '')

        # Confirm_Password = request.POST.get('Confirm_Password', '')

        Address = request.POST.get('Address', '')

        mobiles = request.POST.get('mobile', '')

        gender = request.POST.get('gender', '')
        
        image  = request.POST['user_image']
        
        if image:
            base64_data = image.split(",")[1]  
            binary_data = base64.b64decode(base64_data)  
            image = Image.open(io.BytesIO(binary_data)) 

            # Save the image to a directory
            save_directory = 'user/' 
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
            filename = firstname.replace(' ','_')     
            file_date = generate_vms_string()
            new_file_name =  file_date.replace('VMS','')
            filename = f"{filename}_{new_file_name}.jpg"
            face_image_path = os.path.join(save_directory, filename)

            image.save(face_image_path)
        
        if firstname == ''  or mobiles == '' or lastname == '' or Address == '' or gender == '' or image == '':
            messages.error(request, 'All Filed......', extra_tags='danger')
            return redirect(redirect_url)
        
        if user.objects.filter(id=all_visitor_id).exists():
            visitor = user.objects.get(id=all_visitor_id)
            visitor.first_name = firstname
            visitor.last_name = lastname
            # visitor.email = email
            visitor.mobile = mobiles
            visitor.gender = gender
            visitor.address = Address
            visitor.image = face_image_path
            visitor.updated_at = date_time()
             
            try:
                visitor.save()
                subject_visitor = 'Appointment Confirmation'
                context_visitor = {
                    'text':'Your invitation form successfully Fillup by visitor.'
                }
                
                template_name_visitor = 'registration_form/email_send.html'
                message_visitor = render_to_string(template_name_visitor, context_visitor)
                plain_message_visitor = strip_tags(message_visitor)
                recipient_list_visitor = [user_data_dict['email']]

                mail_visitor = EmailMultiAlternatives(subject_visitor, plain_message_visitor, from_email, recipient_list_visitor)
                mail_visitor.attach_alternative(message_visitor, "text/html")
                mail_visitor.send()
                message = 'Thank you for Registration.'
                return render(request, 'registration_form/thank_you.html',{'thank_message':message,'registered':'false','appointment_id':appointment_id})
            except Exception as e:
                print(e)
                messages.error(request, 'Error while updating visitor.')
                return redirect(redirect_url)
        else:
            messages.error(request, 'Visitor not found for updating.')
        
    else:
        if all_visitor_id:
            visitor = user.objects.get(id=all_visitor_id)
            if visitor.first_name != "":  # Check if visitor is already registered
                message = 'You have been already Registered.'
                return render(request, 'registration_form/thank_you.html', {'thank_message': message, 'registered': 'true','appointment_id':appointment_id})
      
    return render(request,'registration_form/main_file.html',{'user_data_dict':user_data_dict,'user_visitor':user_visitor})



def visitors(request):
    context = {'function_name': 'Visitors', 'ADMIN_STATIC_PATH': settings.ADMIN_STATIC_PATH}
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        user_type = request.POST.get('user_type', '')
        if not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'registration/login.html', context)
        abc = user.objects.filter(email=email, is_active=True, type="visitors").first()
        if abc is not None :
            if abc.password  is not None:
                if check_password(password, abc.password):
                    user_name = abc.first_name
                    vistior = {'user_email': email, 'user_password': password,'user_name':user_name}
                    request.session['visitors'] = vistior
                    # request.session['user_type'] = user_type
                    # return render(request, 'dashboard/visitors_dashboard/dashboard.html', {'username': user_name})
                    return redirect(f'visitors_dashboard')
                    # return redirect(f'visitors_safety_training')
                
                else:
                    messages.error(request, 'Invalid Email or Password.')
            else:
                messages.error(request, 'Invalid Email or Password.')
        else:
            messages.error(request, 'Invalid Login.')

        return render(request, 'registration/login.html', context)

    return render(request, 'registration/login.html', context)

# def visitors(request):
#     context = {'ADMIN_STATIC_PATH': settings.ADMIN_STATIC_PATH}
#     if request.method == 'POST':
#         email = request.POST.get('email', '')
#         password = request.POST.get('password', '')
#         user_type = request.POST.get('user_type', '')

#         if email == '' or password == '':
#             messages.error(request, 'All fields are required.')
#             context['function_name'] = 'Login'
#             return render(request, 'registration/login.html', context)
        
#         user_instance = user.objects.filter(email=email, is_active=True, type=user_type).first()

#         if user_instance is not None:
#             if check_password(password, user_instance.password):
#                 user_name = user_instance.first_name
                
#                 # Store user information in session
#                 user_data = {
#                     'user_email': email,
#                     'user_name': user_name,
#                     'user_type': user_type,
#                 }
                
                
#                 # Redirect to the appropriate dashboard based on user type
#                 if user_type == 'admin':
#                     context['function_name'] = 'Admin Dashboard'
#                     return redirect('admin_dashboard')
#                 elif user_type == 'gate_keeper':
#                     request.session['gate_keeper'] = user_data
#                     context['gate_keeper'] = 'gate_keeper'
#                     return redirect('gate_keeper_dashboard')
#                 elif user_type == 'employee':
#                     context['function_name'] = 'Employee Dashboard'
#                     return redirect('employee_dashboard')
#                 elif user_type == 'visitor':
#                     context['function_name'] = 'Visitor Dashboard'
#                     return redirect('visitor_dashboard')
#                 else:
#                     messages.error(request, 'Invalid user type.')
#                     context['function_name'] = 'Login'
#                     return render(request, 'registration/login.html', context)
#             else:
#                 messages.error(request, 'Invalid login password.')
#                 context['function_name'] = 'Login'
#         else:
#             messages.error(request, 'Invalid login.')
#             context['function_name'] = 'Login'

#         return render(request, 'registration/login.html', context)

#     # Default context for GET request
#     context['function_name'] = 'Login'
#     return render(request, 'registration/login.html', context)



# def visitors_sign_up(request):
#     context = {'function_name': 'Visitors', 'ADMIN_STATIC_PATH': settings.ADMIN_STATIC_PATH}
#     constants = my_constants(request)
#     from_email = constants['From_Email']
#     if request.method == 'POST':
#         firstname = request.POST.get('first_name', '')
#         lastname = request.POST.get('last_name', '')
#         email = request.POST.get('email', '')
#         password = request.POST.get('Password', '')
#         Confirm_Password = request.POST.get('Confirm_Password', '')

#         if password != Confirm_Password:
#             messages.error(request, 'Password and Confirm Password does not match.')
#             return render(request, 'dashboard/visitors_dashboard/sign_up.html', context)
#         if user.objects.filter(email=email).exists():
#             messages.error(request, 'Email already exists.')
#             return render(request, 'dashboard/visitors_dashboard/sign_up.html', context)
#         if password == '' or Confirm_Password == '' or email == '' or firstname == '' or lastname == '':
#             messages.error(request, 'All fields are required.')
#             return render(request, 'dashboard/visitors_dashboard/sign_up.html', context)
#         if password == Confirm_Password:
#             password = make_password(password)
            
#         user_instance = user(first_name=firstname, last_name=lastname, email=email, password=password,is_active=0,employee_code=0,type='visitors')
#         user_instance.save()
#         # Email to visitor
#         visitor_subject = "Thank You for Registration"
#         visitor_message = f"""
#         Dear {firstname} {lastname},

#         Thank you for registering with us. Your registration is under review. 
#         You will be able to log in once approved by the admin.

#         Regards,
#         Visitor Management System
#         """
#         send_mail(visitor_subject, visitor_message, from_email, [email])

#         # Email to admin
#         admin_subject = "New Visitor Registration Approval Needed"
#         admin_message = f"""
#         A new visitor has registered:
#         Id = {user_instance.id}
#         Name: {firstname} {lastname}
#         Email: {email}

#         Please review and approve the registration.

#         Regards,
#         Visitor Management System
#         """
#         # admin_email = "admin@example.com" 
#         email_string = auto_email.objects.values_list('email', flat=True).first()  # Get the first (and possibly only) email string
#         if email_string:
#             # Split the comma-separated email addresses into a list
#             to_email = [email.strip() for email in email_string.split(',')]
#         else:
#             to_email = []
#         send_mail(admin_subject, admin_message, from_email, to_email)
#         messages.success(request, 'User registered successfully.')
#         return redirect('visitors')

#     return render(request, 'dashboard/visitors_dashboard/sign_up.html',context)







def visitors_sign_up(request):
    context = {'function_name': 'Visitors', 'ADMIN_STATIC_PATH': settings.ADMIN_STATIC_PATH}
    constants = my_constants(request)
    from_email = constants['From_Email']
    
    if request.method == 'POST':
        firstname = request.POST.get('first_name', '')
        lastname = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        password = request.POST.get('Password', '')
        confirm_password = request.POST.get('Confirm_Password', '')

        # Validate input
        if password != confirm_password:
            messages.error(request, 'Password and Confirm Password do not match.')
            return render(request, 'dashboard/visitors_dashboard/sign_up.html', context)
        
        if user.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'dashboard/visitors_dashboard/sign_up.html', context)
        
        if not all([firstname, lastname, email, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'dashboard/visitors_dashboard/sign_up.html', context)
        
        # Hash the password
        password = make_password(password)
        
        # Save the user
        user_instance = user(
            first_name=firstname, 
            last_name=lastname, 
            email=email, 
            password=password,
            is_active=0, 
            employee_code=0, 
            type='visitors'
        )
        user_instance.save()

        # Send email to visitor
        visitor_subject = "Thank You for Registration"
        visitor_message = f"""
        Dear {firstname} {lastname},

        Thank you for registering with us. Your registration is under review. 
        You will be able to log in once approved by the admin.

        Regards,
        Visitor Management System
        """
        send_mail(visitor_subject, visitor_message, from_email, [email])

        # Send email to admin
        admin_subject = "New Visitor Registration Approval Needed"
        admin_message = f"""
        A new visitor has registered:
        Id = {user_instance.id}
        Name: {firstname} {lastname}
        Email: {email}

        Please review and approve the registration.

        Regards,
        Visitor Management System
        """
        email_string = auto_email.objects.values_list('email', flat=True).first()
        to_email = [email.strip() for email in email_string.split(',')] if email_string else []
        send_mail(admin_subject, admin_message, from_email, to_email)

        # Show success message and stay on the page for 1 minute before redirect
        messages.success(request, 'User registered successfully.')
        return render(request, 'dashboard/visitors_dashboard/sign_up.html', {**context, 'redirect_url': '/visitors'})

    return render(request, 'dashboard/visitors_dashboard/sign_up.html', context)
def visitors_logout(request):
    if request.session.get('visitors'):
        del request.session['visitors']
    return redirect('visitors')
# admin_layout.html
def dashboard_view(request, user_type):
    username = request.session.get('visitors')
    if not username or request.session.get('user_type') != user_type:
        return redirect('visitors')

    context = {'username': username}

    return render(request, f'dashboard/{user_type}_dashboard/dashboard.html', context)


# def visitors_dashboard(request):
#     # return dashboard_view(request, 'visitors')
#     username = request.session.get('visitors')

#     # user_type = request.session.get('user_type')
#     # print('user_type:-', user_type)

#     if not username :
#         return redirect('visitors')
#         # return redirect('gate_keeper')
#     all_appointment = appointment.objects.all().count()
#     username['all_appointment'] = all_appointment
#     context = {'username': username}
#     email = username['user_email']
#     user_name = username['user_name']
#     useres = user.objects.filter(email=email, first_name=user_name).first()
#     user_image = useres.image

    
#     return render(request, 'dashboard/visitors_dashboard/dashboard.html', context)

    # return render(request,'dashboard/visitors_dashboard/dashboard.html',{'username':username})



def fetch_appointment_data(query, params):
    """Reusable function to execute SQL queries and return results."""
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in data]

def fetch_count(query, params):
    """Reusable function to execute count queries."""
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        result = cursor.fetchone()
        return result[0] if result else 0
    
def visitors_dashboard(request):
    # Call my_constants to get domain and user information
    constants = my_constants(request)
    database_name = constants['database_name']
    today_date = f"20{date_time().split(' ')[0]}"
    username = request.session.get('visitors')
    if not username:
        return redirect('visitors')
    user_data = constants.get('user_data', {})
    user_id = user_data.get('id')
    useres = user.objects.filter(id=user_id).first()  
    video = None
    if not useres.is_safety_training:  # Assuming it's a boolean field
        # last_video = safety_training.objects.order_by('-id')
        last_video = safety_training.objects.filter(is_active=True).order_by('-id').first()
        if last_video:
            video = last_video.video_file

        # return render(request, 'dashboard/visitors_dashboard/visitors_safety_training.html', {
        #     'last_video': video,
        #     'user_id':user_id
        # })
    
    # all_appointment = appointment.objects.filter(visitors_id=user_id).count()
    # username['all_appointment'] = all_appointment


    # now = datetime.datetime.now()
    # date = now.strftime("%Y-%m-%d")
    # time = now.strftime("%I:%M %p").lstrip('0')  # 12-hour format

    # # SQL date and time filter
    # date_filter = f"""
    #             AND(appointment.date > '{date}' OR (appointment.date = '{date}' AND appointment.time > '{time}'))

    #         """
    # user_id_filter = f"AND appointment.visitors_id = {user_id}"
    # # First SQL query to get the count of appointments
    # sql_query_count = f"""
    #             SELECT 
    #                 COUNT(*) AS appointment_count
    #             FROM 
    #                 vms.appointment
    #             INNER JOIN 
    #                 vms.users AS visitors ON visitors.id = appointment.visitors_id
    #             INNER JOIN 
    #                 vms.users AS employees ON employees.id = appointment.employee_id
    #             WHERE 1=1
    #             {date_filter}{user_id_filter};
    #         """

    # with connection.cursor() as cursor:
    #     cursor.execute(sql_query_count)
    #     database_all_data = cursor.fetchall()

    # Upcoming_appointment = database_all_data[0][0] if database_all_data else 0

    # context = {

    #     'username': username,
    #     'DOMAIN_NAME': constants['DOMAIN_NAME'],
    #     'DOMAIN_ICON': constants['DOMAIN_ICON'],
    #     'user_data': constants['user_data'],
    #     'all_appointment': all_appointment,
    #     'Upcoming_appointment':Upcoming_appointment
    # }
    base_query = f"""
        SELECT 
            appointment.*, 
            visitors.first_name AS visitors_name, 
            visitors.last_name AS visitors_last_name, 
            visitors.uni_id AS visitors_uni_id,
            visitors.image AS visitors_image,
            visitors.email AS visitors_email,
            visitors.mobile AS visitors_mobile,
            employees.first_name AS employee_name,
            employees.last_name AS employee_last_name,
            employees.uni_id AS employee_uni_id,
            appointment.check_in_time AS start_time,
            appointment.check_out_time AS stop_time,
            created_by.first_name AS created_by_first_name,
            created_by.last_name AS created_by_last_name
        FROM 
            {database_name}.appointment
        INNER JOIN 
            {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
        INNER JOIN 
            {database_name}.users AS employees ON employees.id = appointment.employee_id
        INNER JOIN 
            {database_name}.users AS created_by ON created_by.id = appointment.created_by
        WHERE date = %s AND visitors_id = %s
    """

    # Query definitions

    queries = {
        "check_out": f"{base_query} AND check_out_time IS NOT NULL AND check_out_time != '' ORDER BY visitors.id DESC",
        "check_in": f"{base_query} AND check_in_time IS NOT NULL AND check_in_time != '' AND check_out_time = '' ORDER BY visitors.id DESC",
        "pending": f"{base_query} AND check_in_time = '' AND check_out_time = '' ORDER BY visitors.id DESC",
    }

    counts = {
        "check_in_count": f"SELECT COUNT(*) FROM ({queries['check_in']}) AS count_query",
        "check_out_count": f"SELECT COUNT(*) FROM ({queries['check_out']}) AS count_query",
        "total_visitors_count": f"SELECT COUNT(*) FROM ({base_query}) AS count_query",
        "pending_count": f"SELECT COUNT(*) FROM ({queries['pending']}) AS count_query",
    }

    # Fetch data
    context_data = {
        "all_check_out_dtl": fetch_appointment_data(queries["check_out"], [today_date, user_id]),
        "all_check_in_dtl": fetch_appointment_data(queries["check_in"], [today_date, user_id]),
        "all_pending_list": fetch_appointment_data(queries["pending"], [today_date, user_id]),
    }

    # Fetch counts
    context_counts = {
        key: fetch_count(value, [today_date, user_id])
        for key, value in counts.items()
    }

    # Combine context
    context = {
        "username": username,
        "DOMAIN_NAME": constants["DOMAIN_NAME"],
        "DOMAIN_ICON": constants["DOMAIN_ICON"],
        "employee_data": constants["employee_data"],
        **context_data,
        **context_counts,
        'last_video': video,
        'user_id':user_id,
        'useres':useres,
    }
    return render(request, 'dashboard/visitors_dashboard/dashboard.html', context)






def visitors_safety_training(request):    
    constants = my_constants(request)    
    username = request.session.get('visitors')
    user_data = constants['user_data']
    user_id = user_data.get('user_id')

    useres = user.objects.filter(id=user_id).first()  
    if not useres:
        return redirect('visitors')
    
    if not useres.is_safety_training: 
        last_video = safety_training.objects.filter(is_active=True).order_by('-id').first()
        video = last_video.video_file if last_video else None
        return render(request, 'dashboard/visitors_dashboard/visitors_safety_training.html', {
            'last_video': video,
            'user_id': user_id  
        })
    else:        
        return render(request, 'dashboard/visitors_dashboard/visitors_safety_training.html', {
            'last_video': last_video,
            'user_id': user_id, 
        })

def update_safety_training_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')

            useres = user.objects.get(id=user_id)
            useres.is_safety_training = True 
            useres.save()

            return JsonResponse({'message': 'Safety training completed successfully!'})
        except Exception as e:
            return JsonResponse({'message': f"Error: {str(e)}"}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=400)

def visitors_appointment_reject(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON data from the request body
            appointment_id = data.get('appointment_id')
            status = data.get('status')
            reason = data.get('reason')
            date = data.get('date')
            time = data.get('time')

            # Ensure you're getting the appointment object
            appointmentes = appointment.objects.filter(id=appointment_id).first()
            if appointmentes:
                appointmentes.status = status
                appointmentes.save()

                appointmentes_rejection = appointment_reject.objects.create(
                    appointment_id=appointment_id,
                    reason=reason,
                    date=date,
                    time=time,
                    created_at=date_time()
                )
                appointmentes_rejection.save()

                return JsonResponse({'status': 'true', 'message': 'Status updated successfully.'})

            else:
                return JsonResponse({'status': 'false', 'message': 'Appointment not found.'})

        except Exception as e:
            return JsonResponse({'status': 'false', 'message': str(e)})

    return JsonResponse({'status': 'false', 'message': 'Invalid request method.'})


def visitors_self_safety_training(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')  
        
        if not request_id:
            messages.error(request, 'Invalid request ID.', extra_tags='danger')
            return render(request, 'dashboard\\visitors_dashboard\\visitors_self_safety_training.html')

        # Check if appointment exists
        appointment_instance = appointment.objects.filter(id=request_id).first()
        if not appointment_instance:
            messages.error(request, 'Appointment not found.', extra_tags='danger')
            return render(request, 'dashboard\\visitors_dashboard\\visitors_self_safety_training.html')

        # Retrieve visitor ID from the appointment
        visitor_id = appointment_instance.visitors_id
        visitor_instance = user.objects.filter(id=visitor_id).first()
        if not visitor_instance:
            messages.error(request, 'Visitor ID not found in the database.', extra_tags='danger')
            return render(request, 'dashboard\\visitors_dashboard\\visitors_self_safety_training.html') 

        # Check if the visitor has completed safety training
        if visitor_instance.is_safety_training:
            return JsonResponse({'status': 'true', 'message': 'Safety training already completed.'})
        else:
            request.session['user_id'] = visitor_instance.id
            return redirect('visitors_safety_training') 

    # For non-POST requests, you can add a handler if needed
    # messages.error(request, 'Invalid request method.', extra_tags='danger')
    return render(request, 'dashboard\\visitors_dashboard\\visitors_self_safety_training.html')
        