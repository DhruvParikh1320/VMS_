
from django.contrib import messages
import requests
import datetime
from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
# Create your views here.
from visitors_app.models import user,appointment,visitors_log,roles,countries,states,cities,location,company,department,areas,appointment_reject,website_setting
from django.contrib.auth.hashers import check_password ,make_password
from django.contrib.auth import authenticate, login
from django.core.files.images import get_image_dimensions
from django.http import JsonResponse
from django.db import connection
from visitors_app.views import date_time,generate_vms_string
from gate_keeper_app.whatsapps_send_notification import whatsapps_send_notifications
from django.shortcuts import get_object_or_404
from visitors_app.context_processors import my_constants
from django.shortcuts import render
from django.template.loader import render_to_string
from visitor_management import settings
from requests.auth import HTTPBasicAuth
from django.utils.html import strip_tags
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core import signing
import base64
import os
from PIL import Image
import io
from django.core.signing import BadSignature
import json

database_name = settings.DATABASE_NAME




# def employee(request):
#     context = {'function_name': 'Employee', 'ADMIN_STATIC_PATH': settings.ADMIN_STATIC_PATH}
#     if request.method == 'POST':
#         # email = request.POST.get('email', '')
        
#         employee_code =request.POST.get('employee_code', '')
#         password = request.POST.get('password', '')
#         user_type = request.POST.get('user_type', '')
#         if employee_code == '' or password == '':
#             messages.error(request, 'All fields are required.')
#             return render(request, 'registration/login.html', context)
#         user_check = user.objects.filter(employee_code=employee_code, is_active=True).first()
#         if user_check is not None:
#             user_types = user_check.type
#             print('user_types:-',user_types)
#             if 'employee' in user_types:            
#                 if user_check is not None:
#                     if check_password(password, user_check.password):
#                         user_name = user_check.first_name
#                         employee = {'user_email': user_check.email, 'user_password': password,'user_name':user_name}
#                         request.session['employee'] = employee
#                         # request.session['username_gate_keeper'] = user_name
#                         # request.session['user_type'] = user_type
#                         # return render(request, 'dashboard\gate_keeper_dashboard\dashboard.html', {'username': user_name})
#                         return redirect(f'employee_dashboard')
#                     else:
#                         messages.error(request, 'Invalid Email or Password.') 
#                 else:
#                     messages.error(request, 'Invalid Login.')
#             else:
#                 messages.error(request, 'Invalid Login.')
#         else:
#             messages.error(request, 'Invalid Login.')

#         return render(request, 'registration/login.html', context)

#     return render(request, 'registration/login.html', context)

def update_appointment_status(decrypted_appointment_id, status, user_check, request):
    """
    Update the appointment status to either 'accepted' or 'rejected'.
    
    Parameters:
    - decrypted_appointment_id: The ID of the appointment to be updated.
    - status: The new status to set (either 'accepted' or 'rejected').
    - user_check: The currently logged-in user object.
    - request: The HTTP request object.
    """
    appointment_instance = get_object_or_404(appointment, id=decrypted_appointment_id)

    # Check if the appointment belongs to the logged-in employee
    if appointment_instance.employee_id != user_check.id:
        messages.error(request, "You are not authorized to modify this appointment.")
        return
    
    # Check if the appointment is already in the desired state
    if appointment_instance.status == status:
        messages.error(request, f"Appointment is already {status}.")
        return

    # If the appointment is being rejected, save the reason
    if status == 'rejected':
        
        # Create a new record in the AppointmentReject table
        appointment_reject.objects.create(
            appointment_id=decrypted_appointment_id,
            reason='',
            date='',
            time='',
            created_at = date_time()
        )

    # Update the appointment status
    appointment_instance.status = status
    appointment_instance.employee_approval = status
    appointment_instance.save()
    # messages.success(request, f"Appointment {status} successfully.")
    # messages.success(request, f"Appointment {status} successfully.")
def employee(request):
    context = {'function_name': 'Employee', 'ADMIN_STATIC_PATH': settings.ADMIN_STATIC_PATH}
    
    if request.method == 'POST':
        employee_code = request.POST.get('employee_code', '')
        password = request.POST.get('password', '')
        
        if not employee_code or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'registration/login.html', context)
        
        user_check = user.objects.filter(employee_code=employee_code, is_active=True).first()
        
        if user_check:
            if 'employee' in user_check.type:
                if check_password(password, user_check.password):
                    user_name = user_check.first_name
                    employee_data = {
                        'user_email': user_check.email,
                        'user_password': password,
                        'user_name': user_name
                    }
                    request.session['employee'] = employee_data
                  
                    encrypted_appointment_id = request.session.get('pending_appointment')
                    pending_action = request.session.get('pending_action')  # Get pending action (accepted or rejected)
                    
                    if encrypted_appointment_id and pending_action:
                        try:
                            decrypted_appointment_id = signing.loads(encrypted_appointment_id)
                            update_appointment_status(decrypted_appointment_id, pending_action, user_check, request)
                            
                            del request.session['pending_appointment']
                            del request.session['pending_action']  # Clear pending action after processing
                            
                            messages.success(request, f"Appointment {pending_action} successfully after login.")
                            return redirect('employee_dashboard')
                        
                        except signing.BadSignature:
                            messages.error(request, "Invalid appointment link, cannot save after login.")
                            return redirect('employee_dashboard')
                    
                    # If there's no pending appointment, just log in successfully
                    return redirect('employee_dashboard')
                else:
                    messages.error(request, 'Invalid Email or Password.')
            else:
                messages.error(request, 'Invalid Login. You are not authorized as an employee.')
        else:
            messages.error(request, 'Invalid Login. No matching account found.')
        
        return render(request, 'registration/login.html', context)
    
    return render(request, 'registration/login.html', context)


def employee_dashboard(request):
    
    constants = my_constants(request)
    
    username = request.session.get('employee')

    if not username:
        return redirect('employee')
    user_data = constants.get('employee_data', {})
    user_id = user_data.get('id')    
    database_name = constants['database_name']
    
    today_date = date_time().split(' ')[0]
    total_visitors_date = f'20{today_date}'
    # Query for check-out details
    sql_query_check_out = f"""
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
        WHERE
            date = %s AND check_out_time IS NOT NULL AND check_out_time != '' AND employee_id = %s
        ORDER BY 
            visitors.id DESC;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query_check_out, [total_visitors_date,user_id])
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_check_out_dtl = [dict(zip(columns, row)) for row in database_all_data]

    # Query for check-in details (corrected)
    sql_query_check_in = f"""
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
        WHERE
            date = %s AND check_in_time IS NOT NULL AND check_in_time != '' AND check_out_time = '' AND employee_id = %s
        ORDER BY 
            visitors.id DESC;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query_check_in, [total_visitors_date,user_id])
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_check_in_dtl = [dict(zip(columns, row)) for row in database_all_data]
    
    sql_query_pending_list = f"""
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
    WHERE
        date = %s AND check_in_time = '' AND check_out_time = '' AND employee_id = %s
    ORDER BY 
        visitors.id DESC;
"""
    with connection.cursor() as cursor:
        cursor.execute(sql_query_pending_list, [total_visitors_date,user_id])
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_pending_list = [dict(zip(columns, row)) for row in database_all_data]

    # Count queries
    sql_query_check_in_count = f"""
        SELECT 
            COUNT(*) AS total_count
        FROM 
            {database_name}.appointment
        INNER JOIN 
            {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
        INNER JOIN 
            {database_name}.users AS employees ON employees.id = appointment.employee_id
        INNER JOIN 
            {database_name}.users AS created_by ON created_by.id = appointment.created_by
        
        WHERE date = %s AND check_in_time IS NOT NULL AND check_in_time != '' AND check_out_time = '' AND employee_id = %s; 
    """
    
    sql_query_check_out_count = f"""
       SELECT 
            COUNT(*) AS total_count
        FROM 
            {database_name}.appointment
        INNER JOIN 
            {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
        INNER JOIN 
            {database_name}.users AS employees ON employees.id = appointment.employee_id
        INNER JOIN 
            {database_name}.users AS created_by ON created_by.id = appointment.created_by
        WHERE date = %s AND check_out_time IS NOT NULL AND check_out_time != '' AND employee_id = %s;
    """
    
    sql_query_total_visitors = f"""
        SELECT 
            COUNT(*) AS total_count
        FROM 
            {database_name}.appointment
        INNER JOIN 
            {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
        INNER JOIN 
            {database_name}.users AS employees ON employees.id = appointment.employee_id
        INNER JOIN 
            {database_name}.users AS created_by ON created_by.id = appointment.created_by
        WHERE date = %s AND employee_id = %s;
    """
    
    # sql_query_pending = f"""
    #     SELECT COUNT(*) FROM {database_name}.appointment
    #     WHERE date = %s AND check_in_time = '' AND check_out_time = '';
    # """

    sql_query_pending = f"""
        SELECT 
            COUNT(*) AS total_count
        FROM 
            {database_name}.appointment
        INNER JOIN 
            {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
        INNER JOIN 
            {database_name}.users AS employees ON employees.id = appointment.employee_id
        INNER JOIN 
            {database_name}.users AS created_by ON created_by.id = appointment.created_by
        WHERE
            date = %s AND check_in_time = '' AND check_out_time = '' AND employee_id = %s;
    
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql_query_check_in_count, [total_visitors_date,user_id])
        check_in_data = cursor.fetchone()
        check_in_count = check_in_data[0] if check_in_data else 0
        
        cursor.execute(sql_query_check_out_count, [total_visitors_date,user_id])
        check_out_data = cursor.fetchone()
        check_out_count = check_out_data[0] if check_out_data else 0

        cursor.execute(sql_query_total_visitors, [total_visitors_date,user_id])
        total_visitors_data = cursor.fetchone()
        total_visitors_count = total_visitors_data[0] if total_visitors_data else 0

        cursor.execute(sql_query_pending, [total_visitors_date,user_id])
        pending_data = cursor.fetchone()
        pending_count = pending_data[0] if pending_data else 0
    
    context = {
        'username': username,
        'DOMAIN_NAME': constants['DOMAIN_NAME'],
        'DOMAIN_ICON': constants['DOMAIN_ICON'],
        'employee_data': constants['employee_data'],
        'check_in_count': check_in_count,  
        'check_out_count': check_out_count,  
        'total_visitors_count': total_visitors_count,
        'pending_count': pending_count,
        'all_check_out_dtl': all_check_out_dtl,
        'all_check_in_dtl': all_check_in_dtl,
        'all_pending_list':all_pending_list
    }

    return render(request, 'dashboard/employee_dashboard/dashboard.html', context)
    
    
    
    
    
    
    
    # context = {

    #     'username': username,
    #     'DOMAIN_NAME': constants['DOMAIN_NAME'],
    #     'DOMAIN_ICON': constants['DOMAIN_ICON'], 
    #     'employee_data': constants['employee_data'],

    # }
    # if user_id:
    #     # Prepare API request to fetch pending count
    #     api_url = f"{constants['ADMIN_PATH']}/api/visitore_listing"  # Adjust URL if necessary
    #     payload = {
    #         'employee_id': user_id,
    #         'type': 'pending',
    #         'page': 1
    #     }
        
    #     try:
    #         response = requests.post(api_url, json=payload,verify=False)
    #         if response.status_code == 200:
    #             data = response.json()
    #             if data['status'] == 'true':
    #                 context['total'] = data['pagination']['total'] # or however you want to calculate the count
    #             else:
    #                 print("API Error:", data.get('message'))
    #         else:
    #             print("HTTP Error:", response.status_code)
    #     except Exception as e:
    #         print(f"Error fetching pending count from API: {e}")
    # return render(request, 'dashboard/employee_dashboard/dashboard.html', context)



def employee_logout(request):
    if request.session.get('employee'):
        del request.session['employee']
    return redirect('employee')





# def employee_edit(request):
#     constants = my_constants(request)
    
#     username = request.session.get('employee')
#     if not username:
#         return redirect('employee')
#     user_data = constants.get('employee_data', {})
    
#         # return redirect('gate_keeper')
#     email = username['user_email']
#     user_name = username['user_name']

#     employee_user = user.objects.get(email=email)
#     if request.method == "POST":
#         employee_user.frist_name = request.POST['Firstname']
        
#         employee_user.last_name = request.POST['Lastname']
        
#         employee_user.email = request.POST['Email']
        
#         # visitors_user.password = request.POST['Password']
#         #
#         # visitors_user.password = request.POST['Confirm_Password']
        
#         employee_user.address = request.POST['Address']
        
#         employee_user.mobile = request.POST['mobile']
        
#         employee_user.gender = request.POST['gender']
#         password = request.POST['Password']
#         confirm_password = request.POST['Confirm_Password']

#         if 'gender' not in request.POST or request.POST['gender'] == '':
#             messages.error(request, 'Please choose a gender.', extra_tags='danger')
#             return redirect('admin_edit')

        
        
#         if password == '' and confirm_password == '':
#             employee_user.password = employee_user.password
        
#         elif password == confirm_password:
#             employee_user.password = make_password(confirm_password)
#         else:
#             messages.error(request, 'Passwords do not match.', extra_tags='danger')
#             return redirect('employee_edit')

#         if 'image' in request.FILES:
#             file = request.FILES['image']
#             file_extension = file.name.split('.')[-1].lower()
#             if file_extension in ['png', 'jpg', 'jpeg']:
#                 employee_user.image = file
#             else:
#                 messages.error(request, 'Error: Invalid image format.', extra_tags='danger')
#                 return redirect('employee_edit')
#         if 'document' in request.FILES:
#             document = request.FILES['document']
#             document_extension = document.name.split('.')[-1].lower()
#             if document_extension in ['png', 'jpg', 'jpeg', 'pdf']:
#                 employee_user.document = document
#             else:
#                 messages.error(request, 'Error: Invalid document format.', extra_tags='danger')
#                 return redirect('employee_edit')
#         employee_user.save()
#         employee_user.save()
#         messages.success(request, f"Successfully Update:", extra_tags="success")
#     return render(request,'dashboard/employee_dashboard/employee_profile/profile_edit.html',{'employee_user':employee_user,'username': username,'user_data': constants['employee_data']})

def employee_edit(request):
    constants = my_constants(request)
        
    username = request.session.get('employee')
    if not username:
        return redirect('employee')
    
    user_data = constants.get('employee_data', {})
    email = username['user_email']
    user_name = username['user_name']
    
    try:
        employee_user = user.objects.get(email=email)
    except user.DoesNotExist:
        messages.error(request, "User not found.", extra_tags="danger")
        return redirect('employee')
    mobile = employee_user.mobile
    # user_mobile = user.objects.filter(mobile=mobile).first()
    if request.method == "POST":
        employee_user.first_name = request.POST['Firstname']
        employee_user.last_name = request.POST['Lastname']
        
        
        new_email = request.POST['Email']
        if employee_user.email != new_email:
            employee_user.email = new_email
            username['user_email'] = new_email
            request.session['employee'] = username
        
        employee_user.address = request.POST['Address']
        employee_user.mobile = request.POST['mobile']
        employee_user.gender = request.POST['gender']
        
        password = request.POST['Password']
        confirm_password = request.POST['Confirm_Password']
        
        if employee_user.mobile != mobile:            
            user_mobile_is_exist  = user.objects.filter(mobile=employee_user.mobile).exists()            
            if user_mobile_is_exist == True:               
                messages.error(request, 'Mobile already exists.', extra_tags='danger')
                return redirect('employee_edit')
            

        if  employee_user.email != email :
            user_email_is_exist  = user.objects.filter(email=employee_user.email).exists()            
            if user_email_is_exist == True:               
                messages.error(request, 'Email already exists.', extra_tags='danger')
                return redirect('employee_edit')
            
            
        if 'gender' not in request.POST or request.POST['gender'] == '':
            messages.error(request, 'Please choose a gender.', extra_tags='danger')
            return redirect('employee_edit')
        
        if password == '' and confirm_password == '':
            pass  # No change in password
        elif password == confirm_password:
            employee_user.password = make_password(confirm_password)
        else:
            messages.error(request, 'Passwords do not match.', extra_tags='danger')
            return redirect('employee_edit')

        if 'image' in request.FILES:
            file = request.FILES['image']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension in ['png', 'jpg', 'jpeg']:
                employee_user.image = file
            else:
                messages.error(request, 'Error: Invalid image format.', extra_tags='danger')
                return redirect('employee_edit')

        if 'document' in request.FILES:
            document = request.FILES['document']
            document_extension = document.name.split('.')[-1].lower()
            if document_extension in ['png', 'jpg', 'jpeg', 'pdf']:
                employee_user.document = document
            else:
                messages.error(request, 'Error: Invalid document format.', extra_tags='danger')
                return redirect('employee_edit')

        employee_user.save()        
        messages.success(request, "Successfully Updated.", extra_tags="success")
        return redirect('employee_edit')

 
        
    return render(request, 'dashboard/employee_dashboard/employee_profile/profile_edit.html', {
        'employee_user': employee_user,
        'username': username,
        'user_data': constants['employee_data']
    })


    
def employee_visitore_approve_reject(request):
    constants = my_constants(request)
    username = request.session.get('employee')
    if not username:
        return redirect('employee')

    employee_data = constants.get('employee_data', {})
    employee_id = employee_data.get('id')

    if not employee_id:
        return JsonResponse({"status": "false", "message": "Employee ID is required."})
    
    DOMIN_PATH = constants['ADMIN_PATH']
    types='all'
    try:
        page = int(request.GET.get('page', 1))
        if page < 1:
            page = 1  # Default to the first page if a negative or zero page is requested
    except ValueError:
        page = 1
    api_url = f"{DOMIN_PATH}api/visitore_listing"
    payload = {
        "employee_id": employee_id,
        "page": page,
        "type": types
    }
    response = requests.post(api_url, json=payload,verify=False)

    if response.status_code == 200:
        api_response = response.json()
        if api_response.get('status') == "true":
            results = api_response.get('data', [])
            pagination = api_response.get('pagination', {})
        else:
            results = []
            pagination = {}
            message = api_response.get('message', 'No data found.')
            return render(request, 'dashboard/employee_dashboard/employee_visitor/employee_visitore_approve_reject.html', {
                'username': username,
                'user_data': constants['employee_data'],
                'message': message
            })
    else:
        results = []
        pagination = {}
        message = 'An error occurred while fetching data.'
        return render(request, 'dashboard/employee_dashboard/employee_visitor/employee_visitore_approve_reject.html', {
            'username': username,
            'user_data': constants['employee_data'],
            'message': message
        })

    last_page = pagination.get('last_page', 1)
    total_entries = pagination.get('total', 0)
    page_range = range(1, last_page + 1)

    # Calculate start and end indices for the current page
    per_page_count = pagination.get('per_page_count', 10)
    
    start_index = (page - 1) * per_page_count + 1
    end_index = min(page * per_page_count, total_entries)

    return render(request, 'dashboard/employee_dashboard/employee_visitor/employee_visitore_approve_reject.html', {
        'username': username,
        'user_data': constants['employee_data'],
        'results': results,
        'pagination': pagination,
        'page_range': page_range,
        'start_index': start_index,
        'end_index': end_index,
        'total_entries': total_entries,
        'DOMIN_PATH': DOMIN_PATH
    })









def employee_visitore_send_invitations(request):
    constants = my_constants(request)
    
    username = request.session.get('employee')
    if not username:
        return redirect('employee')
    user_data = constants.get('employee_data', {})
    user_id = user_data.get('id')
    from_email = constants['From_Email']
    all_employee = user.objects.filter(id=user_id, is_active=1)
    locationes = location.objects.filter(status=1)
    companyes = company.objects.filter(status=1)
    departmentes = department.objects.all()
    role = roles.objects.filter(name='Visitors')
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
              
        
    #     employees_without_areas = api_data_employees
        

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
      
        
        employee_id = request.POST['employee_id']
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
        image  = request.POST['user_image']
        location_id = request.POST['location_id']
        visitors_timing = request.POST['visitors_timing']
        # employees_API = request.POST['employe_API']
        # area = request.POST.getlist('Area[]')
        # area = [item.replace(" ", "").replace("'", "") for item in area]
        
        if user_ides in  '':
            if email != '':
                if user.objects.filter(email=email).exists():
                    messages.error(request, 'User Email already exists.', extra_tags='danger')
                    return redirect('employee_visitore_send_invitations')
            else:
                email = None
        else:
            email = email
            pass
        
        # Convert each cleaned string to an integer
        # area = list(map(int, area))
        
        # if email != '':
        #     if user.objects.filter(email=email).exists():
        #         messages.error(request, 'User Email already exists.', extra_tags='danger')
        #         return redirect('employee_visitore_send_invitations')
        # else:
        #     email = None
        
        # if 'image' in request.FILES and request.FILES['image'] != '':
        #     if 'image' in request.FILES and request.FILES['image'] and len(request.FILES['image']) != 0:
        #         image = request.FILES['image']
        #         try:
        #             width, height = get_image_dimensions(image)
        #         except AttributeError:
        #             messages.error(request, "Error: Uploaded file is not an image.", extra_tags='danger')
        #             return redirect('employee_visitore_send_invitations')

        #         valid_formats = ['image/jpeg', 'image/png', 'image/jpg']
        #         if image.content_type not in valid_formats:
        #             messages.error(request, "Error: Invalid image format.", extra_tags='danger')
        #             return redirect('employee_visitore_send_invitations')
        #     else:
                
        #         messages.error(request, "Error: Invalid image format.", extra_tags='danger')
        #         return redirect('employee_visitore_send_invitations')
        # else:
        #     image = ''
        
        
        if 'user' in image:
            filename = image
        else:
            if image != '':
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
            else:
                filename = ''

        # if user.objects.filter(email=email).exists():
        #     messages.error(request, 'User already exists.', extra_tags='danger')
        # else:
        #     pass

        # if password != confirm_password:
        #     messages.error(request, 'Passwords do not match.', extra_tags='danger')
        #     return redirect('employee_visitore_send_invitations')

        # if password == '' or confirm_password == '':
        #     messages.error(request, 'Password fields cannot be empty.', extra_tags='danger')
        #     return redirect('employee_visitore_send_invitations')

        #password = make_password(password)
        created_at = date_time()
        updated_at = date_time()

        # if employee_id == '' or employee_id == 'Choose employee' or date == '' or time == '' or purpose == '' or visitors_type == 'Choose visitors type' or visitors_type == '' or firstname == '' or password == '' or confirm_password == '' or lastname == '' or address == '' or gender == '' or company_id == '' or company_id == '-- Select Company  --' or department_id == '' or department_id == '-- Select Department --' or location_id == '' or location_id == '-- Select Location --' or status == '':
        #     messages.error(request, "All fields are required.", extra_tags="danger")
        #     return render(request, 'dashboard/employee_dashboard/employee_visitor/employee__visitor_add.html', {
        #         'username': username, 'all_employee': all_employee, 'locationes': locationes, 'companyes': companyes, 'departmentes': departmentes, 'roles': role,'api_data': api_data_areas, 'api_data_employees': api_data_employees,'employees_without_areas':employees_without_areas
        #     })
        
        if employee_id == '' or employee_id == 'Choose employee' or date == '' or time == '' or purpose == '' or company_id == '' or company_id == '-- Select Company  --' or department_id == '' or department_id == '-- Select Department --' or location_id == '' or location_id == '-- Select Location --' or status == '':
            messages.error(request, "All fields are required.", extra_tags="danger")
            return render(request, 'dashboard/employee_dashboard/employee_visitor/employee__visitor_add.html', {
                'username': username, 'all_employee': all_employee, 'locationes': locationes, 'companyes': companyes, 'departmentes': departmentes, 'roles': role
            })
        try:
            if user_ides == '':
                new_user = user.objects.create(
                    first_name=firstname,
                    last_name=lastname,
                    email=email,
                    password='',
                    address=address,
                    mobile=mobile,
                    gender=gender,
                    image=filename,
                    type='visitors',
                    company_id=company_id,
                    department_id=department_id,
                    location_id=location_id,
                    is_active=status,
                    created_at=created_at,
                    uni_id=generate_vms_string(),
                    created_by=user_id,
                    employee_code = 0,
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
                if visitors_type == '':
                    visitors_type = 'other'
                
                new_appointment = appointment(
                    employee_id=employee_id,
                    date=date,
                    time=time,
                    status='pending',
                    purpose=purpose,
                    visitors_type=visitors_type,
                    detail=detail,
                    visitors_id=new_user.id,  
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
                        #https://indianinfotechvms.hexagoninfosoft.in/register
                        confirmation_link = f"{request.build_absolute_uri('/register')}/{encrypted_appointment_id}"
                        subject_visitor = 'Appointment Confirmation'
                        context_visitor = {
                            'visitor_data':new_user,
                            'employee_data':employee_email,
                            'new_appointment':new_appointment,
                            'confirmation_link':confirmation_link,
                        }
                        
                        template_name_visitor = 'dashboard/admin_dashboard/admin_notifitation/visitor_confirmation_email.html'
                        message_visitor = render_to_string(template_name_visitor, context_visitor)
                        plain_message_visitor = strip_tags(message_visitor)
                        recipient_list_visitor = [email]
    
                        mail_visitor = EmailMultiAlternatives(subject_visitor, plain_message_visitor, from_email, recipient_list_visitor)
                        mail_visitor.attach_alternative(message_visitor, "text/html")
                        mail_visitor.send()
    
                        messages.success(request, "Appointment successfully created.", extra_tags="success")
                        return redirect('employee_visitore_send_invitations')
                    except requests.RequestException as e:
                        print(f"API request error: {e}")
                        messages.error(request, f"API request error: {e}", extra_tags="danger")
                        return redirect('employee_visitore_send_invitations')
                else:
                    messages.success(request, "Appointment successfully created.", extra_tags="success")
                    return redirect('employee_visitore_send_invitations')
            else:
                all_users.first_name = firstname
                all_users.last_name = lastname
                all_users.email = email
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
                
                new_appointment = appointment(
                    employee_id=employee_id,
                    date=date,
                    time=time,
                    status='pending',
                    purpose=purpose,
                    visitors_type=visitors_type,
                    detail=detail,
                    visitors_id=user_ides,  
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
                            visitor_name = all_users.first_name
                            if visitor_name == '':
                                visitor_name = '(visitor name)'
                            else:
                                visitor_name = visitor_name
                            employee_mobile = employee_email.mobile
                            employee_name= employee_email.first_name
                            visitor_name=visitor_name
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
                        #https://indianinfotechvms.hexagoninfosoft.in/register
                        confirmation_link = f"{request.build_absolute_uri('/register')}/{encrypted_appointment_id}"
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
    
                        messages.success(request, "Appointment successfully created.", extra_tags="success")
                        return redirect('employee_visitore_send_invitations')
                    except requests.RequestException as e:
                        print(f"API request error: {e}")
                        messages.error(request, f"API request error: {e}", extra_tags="danger")
                        return redirect('employee_visitore_send_invitations')
                else:
                    messages.success(request, "Appointment successfully created.", extra_tags="success")
                    return redirect('employee_visitore_send_invitations')
        except Exception as e:
            messages.error(request, f"Error: {e}", extra_tags="danger")
            return redirect('employee_visitore_send_invitations')
      
    return render(request, 'dashboard/employee_dashboard/employee_visitor/employee__visitor_add.html', {
        'username': username, 'all_employee': all_employee, 'locationes': locationes, 'companyes': companyes, 'departmentes': departmentes
    })


def employee_visitore_all_page(request):
    constants = my_constants(request)
    username = request.session.get('employee')
    if not username:
        return redirect('employee')

    return render(request, 'dashboard/employee_dashboard/employee_visitor/employee_visitore_all_page.html', {
        'username': username,
        'user_data': constants['employee_data']})



def employee_visitore_ajax_page_ajax(request):

    constants = my_constants(request)
    username = request.session.get('employee')
    if not username:
        return redirect('employee')
    
    user_data = constants.get('employee_data', {})
    user_id = user_data.get('id')
    start = int(request.POST.get('start', 0))
    length = int(request.POST.get('length', 10))
    search_value = request.POST.get('search[value]', '')
    
    search = ''
    search_args = []
    if search_value:
        search = '''
            AND (
                u.first_name LIKE %s OR 
                u.email LIKE %s OR 
                a.id LIKE %s OR 
                a.date LIKE %s OR 
                a.time LIKE %s OR 
                a.purpose LIKE %s
            )
        '''
        search_args = [f'%{search_value}%'] * 6

    # First SQL query to get the count of appointments
    sql_query_count = f"""
        SELECT
            COUNT(*)
        FROM
            {database_name}.appointment AS a
        INNER JOIN
            {database_name}.users AS u
        ON
            u.id = a.visitors_id
        WHERE
            a.employee_id = %s
            AND a.status = 'pending'
            {search}
    """
    print('sql_query_count:', sql_query_count)
    with connection.cursor() as cursor:
        cursor.execute(sql_query_count, [user_id] + search_args)
        database_all_data = cursor.fetchall()
        print('database_all_data:', database_all_data)
    recordsTotal = database_all_data[0][0] if database_all_data else 0
    
    # Second SQL query to get detailed appointment data
    sql_query_data = f"""
        SELECT 
            a.*, 
            u.first_name AS visitors_first_name,
            u.email AS visitors_email,
            u.mobile AS visitors_mobile,
            u.image AS visitors_image
        FROM 
            {database_name}.appointment AS a
        INNER JOIN 
            {database_name}.users AS u
        ON 
            u.id = a.visitors_id
        WHERE 
            a.employee_id = %s
            AND a.status = 'pending'
            {search}
        ORDER BY
            a.id DESC
        LIMIT %s OFFSET %s
    """
    
    args_data = [user_id] + search_args + [length, start]
    print('SQL Data Query:', sql_query_data)
    print('Arguments Data Query:', args_data)
    
    with connection.cursor() as cursor:
        cursor.execute(sql_query_data, args_data)
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]
    
    return JsonResponse({"recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, 'data': all_coupon_dtl})






def employee_user(request):
    constants = my_constants(request)
    username = request.session.get('employee')
    if not username:
        return redirect('employee')

    employee_data = constants.get('employee_data', {})
    employee_id = employee_data.get('id')

    return render(request, 'dashboard/employee_dashboard/employee_user/employee_user.html', {'username': username    })

def employee_page_ajax(request):
    constants = my_constants(request)
    database_name = constants['database_name']
    username = request.session.get('employee')
    if not username:
        return redirect('employee')
    
    user_data = constants.get('employee_data', {})
    user_id = user_data.get('id')
    start = int(request.POST.get('start', 0))
    length = int(request.POST.get('length', 10))
    search_value = request.POST.get('search[value]', '')
    
    search = ''
    if search_value:
        search = (
            "AND (users.email LIKE %s OR "
            "users.mobile LIKE %s OR "
            "users.created_at LIKE %s OR "
            "users.updated_at LIKE %s OR "
            "users.first_name LIKE %s OR "
            "users.last_name LIKE %s OR "
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



def employee_new_appointment(request,id):
    constants = my_constants(request)
    
    username = request.session.get('employee')
    if not username:
        return redirect('employee')
    
    # Fetch the appointment based on id
    all_user = get_object_or_404(user, id=id)
    all_employee = user.objects.filter(type='employee',is_active=1)
    user_data = constants.get('employee_data', {})
    user_id = user_data.get('id')
    user_first_name = user_data.get('first_name')
    employee_code = user_data.get('employee_code')
    user_last_name = user_data.get('last_name')
    from_email = constants['From_Email']
    # WDMS_API_ENDPOINT = constants['WDMS_API_ENDPOINT']
    # api_url_areas = f'{WDMS_API_ENDPOINT}personnel/api/areas/'
    # api_url_employees = f'{WDMS_API_ENDPOINT}personnel/api/employees/?areas=1'
    # api_username = 'admin'
    # api_password = 'admin'
    
    # employees_without_areas = {'data': []}  # Initialize with a default value
    
    # try:
    #     # Fetch areas data
    #     response_areas = requests.get(api_url_areas, auth=HTTPBasicAuth(api_username, api_password))
    #     response_areas.raise_for_status()
    #     api_data_areas = response_areas.json()
        
    #     # Fetch employees data
    #     response_employees = requests.get(api_url_employees, auth=HTTPBasicAuth(api_username, api_password))
    #     response_employees.raise_for_status()
    #     api_data_employees = response_employees.json()
    #     employees_without_areas = api_data_employees
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
        # employees_API = request.POST.get('employe_API')
        # area = request.POST.getlist('Area[]')
        # area = [item.replace(" ", "").replace("'", "") for item in area]
    
        # area = list(map(int, area))
        if employee_id == '' or employee_id == 'Choose employee' or date == '' or time == '' or purpose == '' or visitors_type == 'Choose visitors type' or visitors_type == '':
            messages.error(request, "All fields are required.", extra_tags="danger")
            return render(request,'dashboard/employee_dashboard/employee_user/employee_user_appointment_add.html',{'username': username,'all_employee':all_employee,'user_first_name':user_first_name,'user_last_name':user_last_name,'user_id':user_id,'all_user':all_user,'employee_code':employee_code  })
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
                # access_card_id=employees_API
            )
            
            
            
            
            
            
            
        #     api_url = f'{WDMS_API_ENDPOINT}personnel/api/employees/{employees_API}/'
        #     data = {'area': area}
            
        #     try:
        #         response = requests.patch(api_url, json=data, auth=HTTPBasicAuth(api_username, api_password))
        #         response.raise_for_status()

        #         # Handle success
        #         if response.status_code == 200:
        #             appointment_obj.save()
        #             visitor = user.objects.filter(id=visitors_id).first()
                    
        #             visitor_email = all_user.email
        #             employee = user.objects.filter(id=employee_id).first()
        #             if employee:
        #                 try:
        #                     subject_employee = 'New Visitor Appointment'
        #                     context_employee = {
        #                         'employee_data': employee,
        #                         'visitor_data': all_user,
        #                         'new_appointment': appointment_obj,
        #                     }
        #                     template_name_employee = 'notification_email/employee_notification_email.html'
        #                     message_employee = render_to_string(template_name_employee, context_employee)
        #                     plain_message_employee = strip_tags(message_employee)
        #                     recipient_list_employee = [employee.email]  # Use email for sending

        #                     mail_employee = EmailMultiAlternatives(subject_employee, plain_message_employee, from_email, recipient_list_employee)
        #                     mail_employee.attach_alternative(message_employee, "text/html")
        #                     mail_employee.send()
        #                 except Exception as e:
        #                     print('Email send error:', e)
        #                     messages.error(request, f"Error: {e}", extra_tags="danger")
        #             messages.success(request, "Appointment successfully created.", extra_tags="success")
        #             return redirect('employee_user')
        #     except Exception as e:
        #         messages.error(request, f"An error occurred: {e}", extra_tags="danger")
        #     return redirect('employee_user')
        # except Exception as e:
        #     messages.error(request, f"An error occurred: {e}", extra_tags="danger")
            appointment_obj.save()
            # visitor = user.objects.get(id=visitors_id)
            visitor =user.objects.filter(id=id).first()
            employee = user.objects.filter(id=employee_id).first()
    
            encrypted_appointment_id = signing.dumps(appointment_obj.id)
            base_url = request.build_absolute_uri('/')[:-1]

            if employee != '':
                try:                            
                    subject_employee = 'Visitor Appointment'
                    context_employee = {
                        'employee_data':employee,
                        'visitor_data':visitor,
                        'new_appointment':appointment_obj,
                        
                    }
                    
                    template_name_employee = 'notification_email/employee_notification_email.html'
                    
                    message_employee = render_to_string(template_name_employee, context_employee)
                    plain_message_employee = strip_tags(message_employee)
                    recipient_list_employee = [employee]

                    mail_employee = EmailMultiAlternatives(subject_employee, plain_message_employee, from_email, recipient_list_employee)
                    mail_employee.attach_alternative(message_employee, "text/html")
                    
                    mail_employee.send()
                except Exception as e:
                    print('eamil_send_error', e)
                    messages.error(request, f"Error: {e}", extra_tags="danger")
            try:
                if employee.mobile != '':
                    visitor_name = visitor.first_name
                    if visitor_name == '':
                        visitor_name = '(visitor name)'
                    else:
                        visitor_name = visitor_name
                    employee_mobile = employee.mobile
                    employee_name= employee.first_name
                    visitor_name=visitor_name
                    accept_url = f"{base_url}/accept/{encrypted_appointment_id}"
                    reject_url= f"{base_url}/reject/{encrypted_appointment_id}"
                    website_settings = website_setting.objects.first()
                    if website_settings.whatsapp_notification == 1:
                        whatsapps_send_notifications(request,employee_mobile,employee_name,visitor_name,accept_url,reject_url)
            except requests.exceptions.RequestException as e:
                 messages.error(request, f"Error: {e}", extra_tags="danger")
                 pass
            if visitor.email != '' and visitor.email != None:
                try:
                    base_url = request.build_absolute_uri('/')[:-1]
                    appointment_id = appointment_obj.id
                    encrypted_appointment_id = signing.dumps(appointment_id)
                    confirmation_link = f"{base_url}/register/{encrypted_appointment_id}"
                    subject_visitor = 'Appointment Confirmation'
                    context_visitor = {
                        'visitor_data':visitor,
                        'employee_data':employee,
                        'new_appointment':appointment_obj,
                        'confirmation_link':confirmation_link,
                        'is_link':False,
                        'accept_url': f"{base_url}accept/{encrypted_appointment_id}",
                        'reject_url': f"{base_url}reject/{encrypted_appointment_id}",
                    }
                    
                    template_name_visitor = 'dashboard/admin_dashboard/admin_notifitation/visitor_confirmation_email.html'
                    message_visitor = render_to_string(template_name_visitor, context_visitor)
                    plain_message_visitor = strip_tags(message_visitor)
                    recipient_list_visitor = [visitor.email]
                    
                    mail_visitor = EmailMultiAlternatives(subject_visitor, plain_message_visitor, from_email, recipient_list_visitor)
                    mail_visitor.attach_alternative(message_visitor, "text/html")
                    mail_visitor.send()

                    messages.success(request, "Appointment successfully created.", extra_tags="success")
                    return redirect('employee_user')
                except requests.RequestException as e:
                    print(f"API request error: {e}")
                    messages.error(request, f"API request error: {e}", extra_tags="danger")
                    return redirect('employee_user')
            else:
                messages.success(request, "Appointment successfully created.", extra_tags="success")
                return redirect('employee_user')
            
            messages.success(request, "Appointment successfully created.", extra_tags="success")
            return redirect('employee_user')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}", extra_tags="danger")

    return render(request,'dashboard/employee_dashboard/employee_user/employee_user_appointment_add.html',{'username': username,'all_employee':all_employee,'user_first_name':user_first_name,'user_last_name':user_last_name,'user_id':user_id,'all_user':all_user,'employee_code':employee_code  })