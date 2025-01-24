import datetime

from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
# Create your views here.
from django.contrib import messages
from visitors_app.models import user,appointment,visitors_log,roles,countries,states,cities,location,company,department,areas,appointment_reject,website_setting
from django.contrib.auth.hashers import check_password ,make_password
from django.contrib.auth import authenticate, login
from django.core.files.images import get_image_dimensions
from django.http import JsonResponse
from django.db import connection
from visitors_app.views import date_time,generate_vms_string
from django.shortcuts import get_object_or_404
from visitors_app.context_processors import my_constants
from django.shortcuts import render
from django.template.loader import render_to_string
import base64
import os
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.shortcuts import render
from PIL import Image
import io
import requests
from requests.auth import HTTPBasicAuth
from django.core.signing import BadSignature
import requests
from requests.auth import HTTPBasicAuth
from django.core import signing
import json
from gate_keeper_app.whatsapps_send_notification import whatsapps_send_notifications

def gate_keeper_visitor_add(request):
    constants = my_constants(request)
    
    username = request.session.get('gate_keeper')
    if not username:
        return redirect('gate_keeper')
    user_data = constants.get('gate_keeper_data', {})
    from_email = constants['From_Email']
    user_id = user_data.get('id')
    all_employee = user.objects.filter(type='employee', is_active=1)
    locationes = location.objects.filter(status=1)
    companyes = company.objects.filter(status=1)
    departmentes = department.objects.all()
    role = roles.objects.all()
    # WDMS_API_ENDPOINT = constants['WDMS_API_ENDPOINT']
    # api_url_areas = f'{WDMS_API_ENDPOINT}personnel/api/areas/'
    # api_url_employees = f'{WDMS_API_ENDPOINT}personnel/api/employees/?areas=1'
    # api_username = 'admin'
    # api_password = 'admin'
    
    # try:
    #     # Fetch areas data
    #     response_areas = requests.get(api_url_areas, auth=HTTPBasicAuth(api_username, api_password))
    #     response_areas.raise_for_status()
    #     api_data_areas = response_areas.json()
        
    #     # Fetch employees data
    #     response_employees = requests.get(api_url_employees, auth=HTTPBasicAuth(api_username, api_password))
    #     response_employees.raise_for_status()
    #     api_data_employees = response_employees.json()
    #     print('api_data_employees_1:-',api_data_employees)       
        
    #     employees_without_areas = api_data_employees
    #     print('api_data_employees_2:-',employees_without_areas)

    # except requests.RequestException as e:
    #     print(f"API request error: {e}")
    #     messages.error(request, "Failed to fetch data from API.", extra_tags='danger')
    #     api_data_areas = {'data': []}
    #     api_data_employees = {'data': []}
        
    if request.method == "POST":
        
        user_ides = request.POST['user_id']
        if user_ides:
            user_ides_chane = int(user_ides)
            visitor_user = user.objects.filter(id=user_ides_chane).first()
            all_users = user.objects.get(id=user_ides_chane)
        
        employee_id = request.POST['employee']
        date = request.POST['date']
        time = request.POST['time']
        purpose = request.POST['Purpose']
        visitors_type = request.POST['visitors_type']
        detail = request.POST['detail']
        firstname = request.POST['Firstname']
        lastname = request.POST['Lastname']
        email = request.POST['Email']
        # password = request.POST['Password']
        # confirm_password = request.POST['Confirm_Password']
        address = request.POST['Address']
        mobile = request.POST['mobile']
        gender = request.POST['gender']
        company_id = request.POST['company_id']
        department_id = request.POST['department_id']
        status = request.POST['status']
        location_id = request.POST['location_id']
        image  = request.POST['user_image']
        visitors_timing = request.POST['visitors_timing']
        # employee_code = request.POST['employee_code']
        # employees_API = request.POST['employe_API']
        # area = request.POST.getlist('Area[]')
        # area = [item.replace(" ", "").replace("'", "") for item in area]
        
        # # Convert each cleaned string to an integer
        # area = list(map(int, area))
        
        
        if  'user' in image:
            filename = image

        else:
            base64_data = image.split(",")[1]
            binary_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(binary_data))

            save_directory = 'user/' 
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
            filename = firstname.replace(' ','_')
            file_date = generate_vms_string()
            new_file_name =  file_date.replace('VMS','')
            filename = f"{filename}_{new_file_name}.jpg"
            face_image_path = os.path.join(save_directory, filename)

            image.save(face_image_path)
        # if image:
        #     base64_data = image.split(",")[1]  
        #     binary_data = base64.b64decode(base64_data) 
        #     image = Image.open(io.BytesIO(binary_data))  

        #     save_directory = 'user/'  
        #     if not os.path.exists(save_directory):
        #         os.makedirs(save_directory)
        #     filename = firstname.replace(' ','_')     
        #     file_date = generate_vms_string()
        #     new_file_name =  file_date.replace('VMS','')
        #     filename = f"{filename}_{new_file_name}.jpg"
        #     face_image_path = os.path.join(save_directory, filename)

        #     image.save(face_image_path)
        
        
        # if email != '':
        #     if user.objects.filter(email=email).exists():
        #         messages.error(request, 'User Email already exists.', extra_tags='danger')
        #         return redirect('gate_keeper_visitor_add')
        # else:
        #     email = None
        
        
        if user_ides in  '':
            if email != '':
                if user.objects.filter(email=email).exists():
                    messages.error(request, 'User Email already exists.', extra_tags='danger')
                    return redirect('gate_keeper_visitor_add')
            else:
                email = None
        else:
            email = email
            pass
        
        # if user.objects.filter(employee_code=employee_code).exists():
        #     messages.error(request, 'Employee Code already exists.', extra_tags='danger')
        #     return redirect('gate_keeper_visitor_add')

        # if password != confirm_password:
        #     messages.error(request, 'Passwords do not match.', extra_tags='danger')
        #     return redirect('gate_keeper_visitor_add')

        # if not password or not confirm_password:
        #     messages.error(request, 'Password fields cannot be empty.', extra_tags='danger')
        #     return redirect('gate_keeper_visitor_add')

        # password = make_password(password)
        created_at = date_time()
        updated_at = date_time()

        if (employee_id == '' or employee_id == 'Choose employee' or 
            date == '' or time == '' or purpose == '' or 
            visitors_type == 'Choose visitors type' or visitors_type == '' or 
            firstname == '' or 
            lastname == '' or address == '' or gender == '' or 
            company_id == '' or company_id == '-- Select Company  --' or 
            department_id == '' or department_id == '-- Select Department --' or 
            location_id == '' or location_id == '-- Select Location --' or 
            status == ''):
            messages.error(request, "All fields are required.", extra_tags="danger")
            return render(request, 'dashboard/gate_keeper_dashboard/gate_keeper_visitor_add.html', {
                'username': username, 'all_employee': all_employee, 'locationes': locationes, 
                'companyes': companyes, 'departmentes': departmentes, 'roles': role
            })
            # return render(request, 'dashboard/gate_keeper_dashboard/gate_keeper_visitor_add.html', {
            #     'username': username, 'all_employee': all_employee, 'locationes': locationes, 
            #     'companyes': companyes, 'departmentes': departmentes, 'roles': role,
            #     'api_data': api_data_areas, 'api_data_employees': api_data_employees,'employees_without_areas':employees_without_areas
            # }) 
        try:
            if user_ides in  '':
                new_user = user.objects.create(
                    first_name=firstname,
                    last_name=lastname,
                    email=email,
                    address=address,
                    mobile=mobile,
                    gender=gender,
                    image=filename,
                    type='visitors',
                    company_id=0,
                    department_id=0,
                    location_id=0,
                    is_active=status,
                    created_at=created_at,
                    uni_id=generate_vms_string(),
                    created_by=user_id,
                    employee_code= 0,
                    designation_id = 1
                )
                
                # api_url = f'{WDMS_API_ENDPOINT}personnel/api/employees/{employees_API}/'
                # data = {
                #     'area': area,  # Directly pass the list
                # }
                # try:
                #     # Send the PATCH request to update the employee data
                #     response = requests.patch(api_url, json=data, auth=HTTPBasicAuth(api_username, api_password))
                #     response.raise_for_status()  # Raises an HTTPError for bad responses
    
                #     # Handle success
                #     if response.status_code == 200:
                new_user.save()
                new_user.save()                    
                new_appointment = appointment.objects.create(
                    employee_id=employee_id,
                    date=date,
                    time=time,
                    status='pending',
                    purpose=purpose,
                    visitors_type=visitors_type,
                    detail=detail,
                    visitors_id=new_user.id,  # Assuming there's a ForeignKey relationship
                    created_at=date_time(),
                    created_by=user_id,
                    visitors_timing =visitors_timing,
                    employee_approval = None
                   
                )
                new_appointment.save() 
                employee_email = user.objects.filter(id=employee_id).first()
                
                if employee_email != '':
                    try:
                        appointment_id = new_appointment.id
                        encrypted_appointment_id = signing.dumps(appointment_id)
                        base_url = request.build_absolute_uri('/')[:-1]
                        subject_employee = 'New Visitor Appointment'
                        context_employee = {
                            'employee_data':employee_email,
                            'visitor_data':new_user,
                            'new_appointment':new_appointment,
                            'accept_url': f"{base_url}/accept/{encrypted_appointment_id}",
                            'reject_url': f"{base_url}/reject/{encrypted_appointment_id}",
                        }
                                                                       
                        template_name_employee = 'dashboard/admin_dashboard/admin_notifitation/employee_notification_email.html'
                        
                        message_employee = render_to_string(template_name_employee, context_employee)
                        plain_message_employee = strip_tags(message_employee)
                        recipient_list_employee = [employee_email]
    
                        mail_employee = EmailMultiAlternatives(subject_employee, plain_message_employee, from_email, recipient_list_employee)
                        mail_employee.attach_alternative(message_employee, "text/html")
                        mail_employee.send()
                    except Exception as e:
                        print('eamil_send_error', e)
                        messages.error(request, f"Error: {e}", extra_tags="danger")
                try:
                    if employee_email.mobile != '':
                        # visitor_name = new_user.first_name
                        visitor_name = new_user.first_name
                        if visitor_name == '':
                            visitor_name = '(visitor name)'
                        else:
                            visitor_name = visitor_name
                        employee_mobile = employee_email.mobile
                        employee_name= employee_email.first_name
                        visitor_name= visitor_name if visitor_name else 'Default Visitor Name'
                        accept_url = f"{base_url}/accept/{encrypted_appointment_id}"
                        reject_url= f"{base_url}/reject/{encrypted_appointment_id}"
                        website_settings = website_setting.objects.first()
                        if website_settings.whatsapp_notification == 1:
                            whatsapps_send_notifications(request,employee_mobile,employee_name,visitor_name,accept_url,reject_url)
                except requests.exceptions.RequestException as e:
                     messages.error(request, f"Error: {e}", extra_tags="danger")
                if email != '' and email != None:
                    try:
                        appointment_id = new_appointment.id
                        encrypted_appointment_id = signing.dumps(appointment_id)
                        confirmation_link = f"{base_url}/register/{encrypted_appointment_id}"
                        subject_visitor = 'Appointment Confirmation'
                        context_visitor = {
                            'visitor_data':new_user,
                            'employee_data':employee_email,
                            'new_appointment':new_appointment,
                            'confirmation_link':confirmation_link,
                            'is_link':False
                            
                        }
                        
                        template_name_visitor = 'dashboard/admin_dashboard/admin_notifitation/visitor_confirmation_email.html'
                        message_visitor = render_to_string(template_name_visitor, context_visitor)
                        plain_message_visitor = strip_tags(message_visitor)
                        recipient_list_visitor = [email]
    
                        mail_visitor = EmailMultiAlternatives(subject_visitor, plain_message_visitor, from_email, recipient_list_visitor)
                        mail_visitor.attach_alternative(message_visitor, "text/html")
                        mail_visitor.send()
    
                        messages.success(request, "Appointment successfully created.", extra_tags="success")
                        return redirect('gate_keeper_visitor_verification')
                    except requests.RequestException as e:
                        print(f"API request error: {e}")
                        messages.error(request, f"API request error: {e}", extra_tags="danger")
                        return redirect('gate_keeper_visitor_verification')
                else:
                    messages.success(request, "Appointment successfully created.", extra_tags="success")
                    return redirect('gate_keeper_visitor_verification')
            else:
                all_users.first_name = firstname
                all_users.last_name = lastname
                all_users.email = email
                # all_users.password = password
                all_users.address = address
                all_users.mobile = mobile
                all_users.gender = gender
                all_users.image = filename
                all_users.type = 'visitors'
                all_users.company_id = company_id
                all_users.department_id = department_id
                all_users.location_id = location_id
                all_users.is_active = status
                all_users.created_at = created_at
                all_users.uni_id = generate_vms_string()
                all_users.created_by = user_id
                all_users.employee_code = 0
                all_users.designation_id = 1
                all_users.save()

                new_appointment = appointment.objects.create(
                    employee_id=employee_id,
                    date=date,
                    time=time,
                    status='pending',
                    purpose=purpose,
                    visitors_type=visitors_type,
                    detail=detail,
                    visitors_id=user_ides,  # Assuming there's a ForeignKey relationship
                    created_at=date_time(),
                    created_by=user_id,
                    # access_card_id=employees_API,
                    visitors_timing=visitors_timing,
                    employee_approval = None
                )
                new_appointment.save()
                employee_email = user.objects.filter(id=employee_id).first()
                
                if employee_email != '':
                    try:
                        appointment_id = new_appointment.id
                        encrypted_appointment_id = signing.dumps(appointment_id)
                        base_url = request.build_absolute_uri('/')[:-1]
                        subject_employee = 'New Visitor Appointment'
                        context_employee = {
                            'employee_data':employee_email,
                            'visitor_data':visitor_user,
                            'new_appointment':new_appointment,
                            'accept_url': f"{base_url}/accept/{encrypted_appointment_id}",
                            'reject_url': f"{base_url}/reject/{encrypted_appointment_id}",
                        }
                        
                        template_name_employee = 'dashboard/admin_dashboard/admin_notifitation/employee_notification_email.html'
                        
                        message_employee = render_to_string(template_name_employee, context_employee)
                        plain_message_employee = strip_tags(message_employee)
                        recipient_list_employee = [employee_email]
    
                        mail_employee = EmailMultiAlternatives(subject_employee, plain_message_employee, from_email, recipient_list_employee)
                        mail_employee.attach_alternative(message_employee, "text/html")
                        mail_employee.send()
                    except Exception as e:
                        print('eamil_send_error', e)
                        messages.error(request, f"Error: {e}", extra_tags="danger")
                try:
                    if employee_email.mobile != '':
                        # visitor_name = new_user.first_name
                        visitor_name = all_users.first_name
                        if visitor_name == '':
                            visitor_name = '(visitor name)'
                        else:
                            visitor_name = visitor_name
                        employee_mobile = employee_email.mobile
                        employee_name= employee_email.first_name
                        visitor_name= visitor_name if visitor_name else 'Default Visitor Name'
                        accept_url = f"{base_url}/accept/{encrypted_appointment_id}"
                        reject_url= f"{base_url}/reject/{encrypted_appointment_id}"
                        
                        website_settings = website_setting.objects.first()
                        if website_settings.whatsapp_notification == 1:
                            whatsapps_send_notifications(request,employee_mobile,employee_name,visitor_name,accept_url,reject_url)
                except requests.exceptions.RequestException as e:
                     messages.error(request, f"Error: {e}", extra_tags="danger")
                if email != '' and email != None:
                    try:
                        appointment_id = new_appointment.id
                        encrypted_appointment_id = signing.dumps(appointment_id)
                        confirmation_link = f"{base_url}/register/{encrypted_appointment_id}"
                        subject_visitor = 'Appointment Confirmation'
                        context_visitor = {
                            'visitor_data':visitor_user,
                            'employee_data':employee_email,
                            'new_appointment':new_appointment,
                            'confirmation_link':confirmation_link,
                            'is_link':False
                            
                        }
                        
                        template_name_visitor = 'dashboard/admin_dashboard/admin_notifitation/visitor_confirmation_email.html'
                        message_visitor = render_to_string(template_name_visitor, context_visitor)
                        plain_message_visitor = strip_tags(message_visitor)
                        recipient_list_visitor = [email]
    
                        mail_visitor = EmailMultiAlternatives(subject_visitor, plain_message_visitor, from_email, recipient_list_visitor)
                        mail_visitor.attach_alternative(message_visitor, "text/html")
                        mail_visitor.send()
    
                        messages.success(request, f"Appointment successfully created.", extra_tags="success")
                        return redirect('gate_keeper_visitor_verification')
                    except requests.RequestException as e:
                        print(f"API request error: {e}")
                        messages.error(request, f"API request error: {e}", extra_tags="danger")
                        return redirect('gate_keeper_visitor_verification')
                else:
                    messages.success(request, f"Appointment successfully created.", extra_tags="success")
                    return redirect('gate_keeper_visitor_verification')
        except requests.RequestException as e:
            print(f"API request error: {e}")
            messages.error(request, f"API request error: {e}", extra_tags="danger")
        
    return render(request, 'dashboard/gate_keeper_dashboard/gate_keeper_visitor_add.html', {
        'username': username, 'all_employee': all_employee, 'locationes': locationes, 
        'companyes': companyes, 'departmentes': departmentes, 'roles': role
    })


def gate_keeper_ajax_load_employee(request):

    employee_id = request.GET.get('employee_id')  # Correct parameter name

    
    all_user = user.objects.filter(id=employee_id).first()  # Correct filter by `id`

    if all_user is not None:
        all_employee = company.objects.filter(id=all_user.company_id).values('id', 'company_name')
        all_department = department.objects.filter(id=all_user.department_id).values('id', 'department_name')
        all_location = location.objects.filter(id=all_user.location_id).values('id', 'location_name')
        response_data = {
            'company': list(all_employee),
            'departments': list(all_department),
            'location':list(all_location)
        }
        return JsonResponse(response_data, safe=False)
    else:
        
        return JsonResponse([], safe=False)
    # all_employee = company.objects.filter(id=employee_id).first()

    # return JsonResponse(list(all_employee.values('id', 'company_name')), safe=False)
def gate_keeper_visitor_edit(request,id):
    constants = my_constants(request)
    user_data = constants.get('gate_keeper_data', {})
    username = request.session.get('gate_keeper')
    if not username:
        return redirect('gate_keeper')
    
    # Fetch the appointment based on id
    all_appointment = get_object_or_404(appointment, id=id)
    email = username['user_email']
    # Get visitors_id from the appointment object
    visitors_id = all_appointment.visitors_id
    
    # Fetch the user based on visitors_id
    all_user = user.objects.filter(id=visitors_id).first()
    all_mobile= all_user.mobile
    
    all_email = all_user.email
    gate_keeper_user = user.objects.get(email=email)
    mobile = gate_keeper_user.mobile
    # Fetch related data
    all_employee = user.objects.filter(type='employee', is_active=1)
    locationes = location.objects.filter(status=1)
    companyes = company.objects.filter(status=1)
    departmentes = department.objects.all()
    role = roles.objects.all()
    # WDMS_API_ENDPOINT = constants['WDMS_API_ENDPOINT']
    # api_url_areas = f'{WDMS_API_ENDPOINT}personnel/api/areas/'
    # api_url_employees_get = f'{WDMS_API_ENDPOINT}personnel/api/employees/{all_appointment.access_card_id}'
    # api_username = 'admin'
    # api_password = 'admin'
    
    # try:
    #     # Fetch areas data
    #     response_areas = requests.get(api_url_areas, auth=HTTPBasicAuth(api_username, api_password))
    #     response_areas.raise_for_status()
    #     api_data_areas = response_areas.json()
        
    
        
        
    #     response_employees_get = requests.get(api_url_employees_get, auth=HTTPBasicAuth(api_username, api_password))
    #     response_employees_get.raise_for_status()
    #     api_data_employees_get = response_employees_get.json()
        
        
    #     employees_assigned_areas = [
    #         employee for employee in api_data_employees_get['area'] 
    #     ]
    # except requests.RequestException as e:       
    #     messages.error(request, "Failed to fetch data from API.", extra_tags='danger')
    #     api_data_areas = {'data': []}
    #     api_data_employees_get = {'data': []}
    #     employees_assigned_areas = []
    if request.method == "POST":
        all_user.first_name = request.POST['Firstname']
        all_user.last_name = request.POST['Lastname']
        emailes = request.POST['Email']
        if emailes != all_email and emailes != '':
            existing_user  = user.objects.filter(email=emailes).exists()
            if existing_user:
                messages.error(request, "This Email is already in use.", extra_tags='danger')
                return redirect('gate_keeper_visitor_edit',id=id)
            else:
                all_user.email = emailes
        elif emailes == '':  # If email is empty, set email back to original or handle accordingly
            all_user.email = all_email
            
        all_user.company_id =request.POST['company_id']
        all_user.department_id =request.POST['department_id']
        # all_user.area_id =request.POST['area_id']
        all_user.location_id =request.POST['location_id']
        all_user.gender =request.POST['gender']
        all_user.address =request.POST['Address']
        all_user.is_active =request.POST['status']
        all_user.mobile = request.POST['mobile']
        image  = request.POST['user_image']
        # password = request.POST['Password']
        # employees_API = request.POST['employe_API']
        # area = request.POST.getlist('Area[]')
        # area = [item.replace(" ", "").replace("'", "") for item in area]
        
        
        # if all_user.mobile != mobile:            
        #     user_mobile_is_exist  = user.objects.filter(mobile=all_user.mobile).exists()            
        #     if user_mobile_is_exist == True:               
        #         messages.error(request, 'Mobile already exists.', extra_tags='danger')
        #         return redirect('gate_keeper_visitor_verification')
            

        # if  all_user.email != gate_keeper_user :
        #     user_email_is_exist  = user.objects.filter(email=all_user.email).exists()            
        #     if user_email_is_exist == True:               
        #         messages.error(request, 'Email already exists.', extra_tags='danger')
        #         return redirect('gate_keeper_visitor_verification')
        
        
        # Convert each cleaned string to an integer
        # area = list(map(int, area))
        all_user.employee_code = all_user.employee_code
        
        
        # if password == '':
        #     all_user.password = all_user.password

        
        if image != '':
            base64_data = image.split(",")[1]  # Extract base64 part
            binary_data = base64.b64decode(base64_data)  # Decode base64 data
            image = Image.open(io.BytesIO(binary_data))  # Convert binary data to image


            # Save the image to a directory
            save_directory = 'user/'  # Ensure this directory exists or use a path within Django's MEDIA_ROOT
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
            user_img = generate_vms_string()

            user_img = user_img.split('VMS')[1]
            
            filename = f"user_{user_img}"  
               
            filename = f"{filename}.jpg"
            face_image_path = os.path.join(save_directory, filename)
            image.save(face_image_path)
            all_user.image = f"user/{filename}"
        else:
                  
            all_user.image = all_user.image
        
        
        all_user.updated_at = date_time()    
        all_user.save()
        all_user.save()
        all_appointment.visitors_id = all_user.id
        all_appointment.employee_id = request.POST['employee']
        all_appointment.purpose = request.POST['Purpose']
        all_appointment.date = request.POST['date']
        all_appointment.time = request.POST['time'] 
        all_appointment.detail = request.POST['detail'] 
        all_appointment.visitors_type = request.POST['visitors_type']
        all_appointment.visitors_timing = request.POST['visitors_timing']
        all_appointment.updated_at = date_time()      
        
        all_appointment.save()
        messages.success(request, "Employee data updated successfully.", extra_tags="success")
        return redirect('gate_keeper_visitor_verification')
        # api_url = f'{WDMS_API_ENDPOINT}personnel/api/employees/{employees_API}/'
        # data = {
        #     'area': area,  # Directly pass the list
        # }
        # try:
        #     # Send the PATCH request to update the employee data
        #     response = requests.patch(api_url, json=data, auth=HTTPBasicAuth(api_username, api_password))
        #     response.raise_for_status()  # Raises an HTTPError for bad responses

        #     # Handle success
        #     if response.status_code == 200:
        #         print("Employee data updated successfully.")
        #         messages.success(request, "Employee data updated successfully.", extra_tags="success")
        #         return redirect('gate_keeper_visitor_verification')
        #     else:
        #         print(f"Failed to update employee data. Status code: {response.status_code}")
        #         messages.error(request, f"Failed to update employee data. Status code: {response.status_code}", extra_tags="danger")
        #         return redirect('gate_keeper_visitor_add')
        # except requests.RequestException as e:
        #     print(f"API request error: {e}")
        #     messages.error(request, f"API request error: {e}", extra_tags="danger")
        # return redirect('gate_keeper_visitor_verification')
        
    return render(request, 'dashboard/gate_keeper_dashboard/gate_keeper_visitor_edit.html', {
        'username': username,
        'all_employee': all_employee,
        'locationes': locationes,
        'companyes': companyes,
        'departmentes': departmentes,
        'roles': role,
        'appointment': all_appointment,  # Add appointment to context if needed in the template
        'user': all_user,  # Add user to context if needed in the template
        'user_data':user_data,
        # 'api_data': api_data_areas,'api_data_employees_get':api_data_employees_get,'employees_assigned_areas':employees_assigned_areas
    })
    
    
    
    
    
    
    
def handle_appointment(request, encrypted_appointment_id, status):
    """
    Common function to handle both accepting and rejecting appointments.
    `status` should be 'accepted' or 'rejected'.
    """
    constants = my_constants(request)
    user_data = constants.get('employee_data', {})
    username = request.session.get('employee')

    if not username:
        request.session['pending_appointment'] = encrypted_appointment_id
        request.session['pending_action'] = status  # Save the pending action in the session (accepted or rejected)
        return redirect('employee')

    try:
        decrypted_appointment_id = signing.loads(encrypted_appointment_id)
        appointment_instance = get_object_or_404(appointment, id=decrypted_appointment_id)

        if appointment_instance.employee_id != user_data.get('id'):
            messages.error(request, f"You are not authorized to {status} this appointment.", extra_tags="danger")
            return redirect('employee_dashboard')

        # Check if the current status matches the desired action
        if appointment_instance.status == status:
            messages.error(request, f"Appointment is already {status}.", extra_tags="danger")
            return redirect('employee_dashboard')

        # Handle conflicting status changes
        if (status == 'rejected' and appointment_instance.status == 'accepted') or \
           (status == 'accepted' and appointment_instance.status == 'rejected'):
            messages.error(request, f"You cannot change the appointment from {appointment_instance.status} to {status}.", extra_tags="danger")
            return redirect('employee_dashboard')

        # Proceed to update the appointment status
        appointment_instance.status = status
        appointment_instance.employee_approval = status
        if status == 'rejected':
            # Create a new record in the AppointmentReject table
            appointment_reject.objects.create(
                appointment_id=decrypted_appointment_id,
                reason='',
                date='',
                time='',
                created_at = date_time()
            )

        appointment_instance.save()
        messages.success(request, f"Appointment {status} successfully.", extra_tags="success")

        return redirect('employee_dashboard')

    except BadSignature:
        messages.error(request, "Invalid appointment link.")
        return redirect('employee')
    
def accept_appointment(request, encrypted_appointment_id):
    return handle_appointment(request, encrypted_appointment_id, 'accepted')

def reject_appointment(request, encrypted_appointment_id):
    return handle_appointment(request, encrypted_appointment_id, 'rejected')