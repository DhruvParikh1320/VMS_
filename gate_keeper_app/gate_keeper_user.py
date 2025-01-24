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
import requests
from requests.auth import HTTPBasicAuth
from PIL import Image
import io
from django.core.signing import BadSignature
from django.core import signing
import requests
import json
from gate_keeper_app.whatsapps_send_notification import whatsapps_send_notifications

def gate_keeper_user(request):
    constants = my_constants(request)
    
    username = request.session.get('gate_keeper')
    if not username:
        return redirect('gate_keeper')
    
    return render(request, 'dashboard/gate_keeper_dashboard/gate_keeper_user/gate_keeper_user.html', {
        'username': username    })

def gate_keeper_user_page_ajax(request):
    constants = my_constants(request)
    database_name = constants['database_name']
    username = request.session.get('gate_keeper')
    if not username:
        return redirect('gate_keeper')
    
    user_data = constants.get('gate_keeper_data', {})
    user_id = user_data.get('id')
    start = int(request.POST.get('start', 0))
    length = int(request.POST.get('length', 10))
    search_value = request.POST.get('search[value]', '')
    
    search = ''
    if search_value:
        search = (
            "AND (users.first_name LIKE %s OR "
            "users.last_name LIKE %s OR "
            "users.email LIKE %s OR "
            "users.mobile LIKE %s OR "
            "users.created_at LIKE %s OR "
            "users.updated_at LIKE %s OR "
            "users.uni_id LIKE %s)"
        )
        search_params = ['%' + search_value + '%'] * 7
    else:
        search_params = []

    # First SQL query to get the count of appointments
    sql_query = f"""
       SELECT
            COUNT(*) AS users
        FROM
            {database_name}.users AS users
        LEFT  JOIN  
            {database_name}.users AS created_by ON created_by.id = users.created_by
        WHERE
            users.type = 'visitors'
            {search}
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query, search_params)
        database_all_data = cursor.fetchall()

    recordsTotal = database_all_data[0][0] if database_all_data else 0

    # Second SQL query to get detailed appointment data
    sql_query = f"""
       SELECT 
            users.*, 
            created_by.first_name AS created_by_first_name,
            created_by.last_name AS created_by_last_name 
        FROM 
            {database_name}.users
        LEFT JOIN  
            {database_name}.users AS created_by ON created_by.id = users.created_by
        WHERE
            users.type = 'visitors'
            {search} 
        ORDER BY 
            users.id DESC
        LIMIT %s OFFSET %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql_query, search_params + [length, start])
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]

    return JsonResponse({"recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, 'data': all_coupon_dtl})


def gate_keeper_user_new_appointment(request,id):
    constants = my_constants(request)
    
    username = request.session.get('gate_keeper')

    if not username:
        return redirect('gate_keeper')
    
    # Fetch the appointment based on id
    all_user = get_object_or_404(user, id=id)
    # user_name = user.objects.filter(id=all_user,is_active=1).first().first_name
    # print('user_name:-',user_name)
    # user_name = user_name.first_name
    # print('user_name:-1',user_name)
    # all_visitor = user.objects.filter(id=id,is_active=1)
    # visitor_first_name = all_visitor.first().first_name
    all_appointmentes = appointment.objects.filter(visitors_id=id)
    all_employee = user.objects.filter(type='employee',is_active=1)
    user_data = constants.get('gate_keeper_data', {})
    user_id = user_data.get('id')
    from_email = constants['From_Email']
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
        visitors_id = user_id
        employee_id = request.POST['employee']
        date = request.POST['date']
        time = request.POST['time']
        purpose = request.POST['Purpose']
        visitors_type = request.POST['visitors_type']
        detail = request.POST['detail']
        visitors_timing = request.POST['visitors_timing']
        # employees_API = request.POST['employe_API']
        # area = request.POST.getlist('Area[]')
        # area = [item.replace(" ", "").replace("'", "") for item in area]
        
        # Convert each cleaned string to an integer
        # area = list(map(int, area))
        if employee_id == '' or employee_id == 'Choose employee' or date == '' or time == '' or purpose == '' or visitors_type == 'Choose visitors type' or visitors_type == '':
            messages.error(request, "All fields are required.", extra_tags="danger")
            return render(request, 'dashboard/gate_keeper_dashboard/gate_keeper_user/gate_keeper_user_appointment_add.html', {
                'username': username, 'all_employee': all_employee
            })
        try:
            appointment_obj = appointment(
                visitors_id=id,
                employee_id=employee_id,
                date=date,
                time=time,
                status='pending',  # Assuming 'scheduled' is the default status
                created_at =date_time(),
                purpose = purpose,
                visitors_type = visitors_type,
                detail = detail,
                created_by=user_id,
                visitors_timing =visitors_timing,
                employee_approval = None
                # access_card_id = employees_API
                
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
            
            appointment_obj.save()
            
            visitor = user.objects.filter(id=id).first()
            
            # visitor_email = all_user.email

            employee = user.objects.filter(id=employee_id).first()

            if employee != '':
                try:
                    appointment_id = appointment_obj.id
                    encrypted_appointment_id = signing.dumps(appointment_id)
                    base_url = request.build_absolute_uri('/')[:-1]
                    subject_employee = 'New Visitor Appointment'
                    context_employee = {
                        'employee_data':employee,
                        'visitor_data':visitor,
                        'new_appointment':appointment_obj,
                        'accept_url': f"{base_url}/accept/{encrypted_appointment_id}",
                        'reject_url': f"{base_url}/reject/{encrypted_appointment_id}",
                    }
                    
                    template_name_employee = 'notification_email/employee_notification_email.html'
                    
                    message_employee = render_to_string(template_name_employee, context_employee)
                    plain_message_employee = strip_tags(message_employee)
                    recipient_list_employee = [employee.email]

                    mail_employee = EmailMultiAlternatives(subject_employee, plain_message_employee, from_email, recipient_list_employee)
                    mail_employee.attach_alternative(message_employee, "text/html")
                    mail_employee.send()
                except Exception as e:
                    print('eamil_send_error', e)
                    messages.error(request, f"Error: {e}", extra_tags="danger")
            try:
                if employee.mobile != '':
                    # visitor_name = new_user.first_name
                    visitor_name = visitor.first_name
                    if visitor_name == '':
                        visitor_name = '(visitor name)'
                    else:
                        visitor_name = visitor_name
                    employee_mobile = employee.mobile
                    employee_name= employee.first_name
                    visitor_name= visitor_name if visitor_name else 'Default Visitor Name'
                    accept_url = f"{base_url}/accept/{encrypted_appointment_id}"
                    reject_url= f"{base_url}/reject/{encrypted_appointment_id}"
                    website_settings = website_setting.objects.first()
                    if website_settings.whatsapp_notification == 1:
                        whatsapps_send_notifications(request,employee_mobile,employee_name,visitor_name,accept_url,reject_url)
            except requests.exceptions.RequestException as e:
                 messages.error(request, f"Error: {e}", extra_tags="danger")
            if visitor and visitor.email:
                try:
                    appointment_id = appointment_obj.id
                    encrypted_appointment_id = signing.dumps(appointment_id)
                    confirmation_link = f"{base_url}/register/{encrypted_appointment_id}"
                    subject_visitor = 'Appointment Confirmation'
                    context_visitor = {
                        'visitor_data': visitor,
                        'employee_data': employee,
                        'new_appointment': appointment_obj,
                        'confirmation_link':confirmation_link,
                        'is_link': False
                    }
                    
                    template_name_visitor = 'dashboard/admin_dashboard/admin_notifitation/visitor_confirmation_email.html'
                    message_visitor = render_to_string(template_name_visitor, context_visitor)
                    plain_message_visitor = strip_tags(message_visitor)
                    recipient_list_visitor = [visitor.email]
                    mail_visitor = EmailMultiAlternatives(subject_visitor, plain_message_visitor, from_email, recipient_list_visitor)
                    mail_visitor.attach_alternative(message_visitor, "text/html")
                    mail_visitor.send()
                    # messages.success(request, "Appointment successfully created.", extra_tags="success")
                    # return Response({"status": "true", "message": "Appointment successfully created."})
                except Exception as e:
                    print(f"Email to visitor error: {e}")
                    # messages.success(request, "Appointment successfully created.", extra_tags="success")
                    # return Response({"status": "true", "message": "Appointment successfully created."})
            messages.success(request, "Appointment successfully created.", extra_tags="success")
            return redirect('gate_keeper_visitor_verification')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}", extra_tags="danger")
        
    return render(request,'dashboard/gate_keeper_dashboard/gate_keeper_user/gate_keeper_user_appointment_add.html',{'username': username,'all_employee':all_employee,'user_id':user_id,'all_user':all_user,'all_appointment':all_appointmentes})