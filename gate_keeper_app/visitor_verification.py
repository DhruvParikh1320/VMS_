import datetime

from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
# Create your views here.
from django.contrib import messages
from visitors_app.models import user,appointment,visitors_log,gate_pass_no
from django.contrib.auth.hashers import check_password ,make_password
from django.contrib.auth import authenticate, login
from django.core.files.images import get_image_dimensions
from django.http import JsonResponse
from django.db import connection
from visitors_app.views import date_time
from django.shortcuts import get_object_or_404
from visitors_app.context_processors import my_constants
from django.shortcuts import render
from django.template.loader import render_to_string
from datetime import  datetime,timedelta
import requests
from requests.auth import HTTPBasicAuth
import qrcode

from io import BytesIO
import base64

def gate_keeper_visitor_verification(request):
    constants = my_constants(request)
    
    username = request.session.get('gate_keeper')
    if not username:
        return redirect('gate_keeper')

    return render(request,'dashboard/gate_keeper_dashboard/gate_keeper_visitor_verification.html',{'username': username})

def gate_keeper_visitor_verification_page_ajax(request):
    constants = my_constants(request)
    username = request.session.get('gate_keeper')
    if not username:
        return redirect('gate_keeper')
    database_name = constants['database_name']
    user_data = constants.get('user_data', {})
    user_id = user_data.get('id')
    start = int(request.POST.get('start', 0))
    length = int(request.POST.get('length', 10))
    search_value = request.POST.get('search[value]', '')
    
    search = ''
    if search_value:
        search = (
            "AND (visitors.first_name LIKE %s OR "
            "visitors.last_name LIKE %s OR "
            "employees.first_name LIKE %s OR "
            "employees.last_name LIKE %s OR "
            "appointment.id LIKE %s OR "
            "appointment.date LIKE %s OR "
            "appointment.time LIKE %s OR "
            "appointment.purpose LIKE %s OR "
            "appointment.status LIKE %s OR "
            "visitors.uni_id LIKE %s OR "
            "appointment.visitors_type LIKE %s OR "
            "visitors.mobile LIKE %s)"
        )
        search_params = ['%' + search_value + '%'] * 12
    else:
        search_params = []

    # First SQL query to get the count of appointments
    sql_query = f"""
        SELECT
            COUNT(*) AS appointment_count
        FROM
            {database_name}.appointment
        INNER JOIN
            {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
        INNER JOIN
            {database_name}.users AS employees ON employees.id = appointment.employee_id
        INNER JOIN 
            {database_name}.users AS created_by ON created_by.id = appointment.created_by
        WHERE
            1=1
            {search}
    """

    with connection.cursor() as cursor:
        cursor.execute(sql_query, search_params)
        database_all_data = cursor.fetchall()

    recordsTotal = database_all_data[0][0] if database_all_data else 0

    # Second SQL query to get detailed appointment data
    sql_query = f"""
        SELECT 
            appointment.*, 
            visitors.first_name AS visitors_name, 
            visitors.last_name AS visitors_last_name, 
            visitors.uni_id AS visitors_uni_id,
            visitors.image AS visitors_image,
            visitors.mobile AS visitors_mobile,
            employees.first_name AS employee_name,
            employees.last_name AS employee_last_name,
            employees.uni_id AS employee_uni_id,
            appointment.check_in_time AS start_time,
            appointment.check_out_time AS stop_time,
            created_by.first_name AS created_by_first_name,
            created_by.last_name AS created_by_last_name,
            employees.designation_id AS employees_designation_id,
            designation.allow_check_in AS employees_allow_check_in

        FROM 
            {database_name}.appointment
        INNER JOIN 
            {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
        INNER JOIN 
            {database_name}.users AS employees ON employees.id = appointment.employee_id
        INNER JOIN 
            {database_name}.users AS created_by ON created_by.id = appointment.created_by
            
        LEFT JOIN 
            {database_name}.designation AS designation ON designation.id = employees.designation_id
        
    
        WHERE
            1=1
            
            {search}
        ORDER BY 
            appointment.id DESC
        LIMIT %s OFFSET %s;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query, search_params + [length, start])
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]

    return JsonResponse({"recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, 'data': all_coupon_dtl})



def gate_keeper_start_time(request, id):
    username = request.session.get('gate_keeper')
    # if not username:
    #     return redirect('gate_keeper')
    if request.method == 'POST':
        try:
            Appointment = appointment.objects.get(id=id)
            if Appointment.check_in_time is not None:

                Appointment.status = 'check in'
                Appointment.check_in_time = date_time()
                # visitors_loges = visitors_log.objects.create(appointment_id=id,start_time=date_time(),created_at=date_time())
                Appointment.save()

                return JsonResponse({'status': 'success','message': 'Check-in time set successfully'})
            print('yes...no......')
            return JsonResponse({'status': 'error', 'message': 'Start time already set'})
        except Appointment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Appointment not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})





def gate_keeper_stop_time(request, id):
    constants = my_constants(request)
    username = request.session.get('gate_keeper')
    # if not username:
    #     return redirect('gate_keeper')
    if request.method == 'POST':
        try:
            appointmentes = appointment.objects.get(id=id)
            if appointment.check_in_time and appointment.check_out_time is not None:
                appointmentes.status = 'check out'
                appointmentes.check_out_time = date_time()
                appointmentes.save()
                return JsonResponse({'status': 'success','message': 'Check-out time set successfully'})
            return JsonResponse({'status': 'error', 'message': 'Cannot stop time'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {(e)}'})        
    
    return JsonResponse({'status': 'success'})




def gate_keeper_print_gate_pass(request, id):
    constants = my_constants(request)
    username = request.session.get('gate_keeper')
    if not username:
        return redirect('gate_keeper')
    pass_type = request.GET.get('pass_type')
    get_pass_images = constants['GET_PASS_IMAGE']
    database_name = constants['database_name']
    appointmentes = get_object_or_404(appointment, id=id)
    
        
    latest_gate_pass = gate_pass_no.objects.filter(appointment_id=id).first()
    if latest_gate_pass:
        latest_gate_pass.updated_at = date_time()
        latest_gate_pass.save()
    else:
        latest_gate_pass = gate_pass_no.objects.order_by('-gate_pass_number').first()

        gate_pass_nos = latest_gate_pass.gate_pass_number + 1 if latest_gate_pass else 1
        # gate_pass_nos = str(gate_pass_nos).zfill(4)
        new_gate_pass = gate_pass_no(
            appointment_id=id,
            gate_pass_number=gate_pass_nos,
            created_at=date_time()

        )
        new_gate_pass.save()
    # formatted_gate_pass_number = str(new_gate_pass.gate_pass_number).zfill(4)
    if latest_gate_pass:
        # Format the existing gate pass number
        formatted_gate_pass_number = str(latest_gate_pass.gate_pass_number).zfill(4)
    else:
        # If there was no previous gate pass, and we created a new one
        formatted_gate_pass_number = str(gate_pass_nos).zfill(4)
    check_in_time = datetime.now().replace(microsecond=0)

# # Format the date to YY-MM-DD HH:MM:SS
    formatted_check_in_time = check_in_time.strftime('%y-%m-%d %H:%M:%S')
    
    if appointment.check_in_time:
        pass
    else:
#     # Set the check-in time
        appointmentes.check_in_time = formatted_check_in_time

    #     # Set the check-out time as one hour after the check-in time, formatted to YY-MM-DD HH:MM:SS
    #     check_out_time = check_in_time + timedelta(hours=1)
    #     formatted_check_out_time = check_out_time.strftime('%y-%m-%d %H:%M:%S')
    #     appointmentes.check_out_time = formatted_check_out_time
        appointmentes.save()
        
    sql_query = f"""
       SELECT 
            appointment.*, 
            visitors.first_name AS visitors_name,
            visitors.last_name AS visitors_last_name, 
            visitors.uni_id AS visitors_uni_id,
            employees.first_name AS employee_name,
            employees.last_name AS employee_last_name,
            visitors.mobile AS visitors_mobile,
            visitors.email AS visitors_email,
            visitors.address AS visitors_address,
            visitors.image AS visitors_image,
            company.company_name AS company_name, 
            company.address_1 AS address_1,
            department.department_name AS department_name,
            department.department_color_code AS department_color_code,
            location.location_name AS location_name,
            gate_pass.gate_pass_number AS gate_pass_number
            
        FROM 
            {database_name}.appointment
        INNER JOIN 
            {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
        INNER JOIN 
            {database_name}.users AS employees ON employees.id = appointment.employee_id
        INNER JOIN
            {database_name}.company AS company ON company.id = employees.company_id  -- Join with company table
        
        INNER JOIN
            {database_name}.department AS department ON department.id = employees.department_id  -- Join with company table
            
        INNER JOIN
            {database_name}.location AS location ON location.id = employees.location_id  -- Join with company table
        INNER JOIN 
            {database_name}.gate_pass_no AS gate_pass ON gate_pass.appointment_id = appointment.id
        WHERE
            appointment.id = %s;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query,[id])
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]
    # Generate QR code for the visitor details URL
    visitor_url = request.build_absolute_uri(f'/visitor_details/{id}/')
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(visitor_url)
    qr.make(fit=True)
    # Create QR code image
    img_buffer = BytesIO()
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(img_buffer, format='PNG')
    qr_code_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    context = {
        'appointment': all_coupon_dtl,
        'get_pass_images':get_pass_images,
        'formatted_gate_pass_number':formatted_gate_pass_number,
        'pass_type':pass_type,
        'qr_code_base64':qr_code_base64,
    }
    # Render the HTML content for the modal
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        # If the request is AJAX, render just the part of the template needed
        html = render_to_string('dashboard/gate_keeper_dashboard/gate_keeper_print_gate_pass.html', context, request=request)
        return JsonResponse({'html': html})
    # For non-AJAX requests (e.g., direct URL access)
    return render(request, 'dashboard/gate_keeper_dashboard/gate_keeper_print_gate_pass.html', context)