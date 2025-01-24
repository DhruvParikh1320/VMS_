import datetime

from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
# Create your views here.
from django.contrib import messages
from visitors_app.models import user,appointment,visitors_log
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
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail


def admin_visitor(request):
    constants = my_constants(request)
    
    username = request.session.get('admin')
    if not username:
        return redirect('admin')

    return render(request,'dashboard/admin_dashboard/admin_visitor/admin_visitor.html',{'username': username})


def admin_visitor_verification_page_ajax(request):
    constants = my_constants(request)
    
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    database_name = constants['database_name']
    start = int(request.POST.get('start', 0))
    length = int(request.POST.get('length', 10))
    search_value = request.POST.get('search[value]', '')
    
    search = ''
    if search_value:
        search = (
            "AND (visitors.first_name LIKE %s OR "
            "employees.first_name LIKE %s OR "
            "appointment.id LIKE %s OR "
            "appointment.date LIKE %s OR "
            "appointment.time LIKE %s OR "
            "appointment.purpose LIKE %s OR "
            "visitors.mobile LIKE %s OR "
            "visitors.uni_id LIKE %s)"
        )
        search_params = ['%' + search_value + '%'] * 8
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
        WHERE
            {database_name}.appointment.status IN ('pending', 'check in', 'check out')
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
            visitors.uni_id AS visitors_uni_id,
            visitors.image AS visitors_image,
            visitors.mobile AS visitors_mobile,
            employees.first_name AS employee_name,
            employees.uni_id AS employee_uni_id,
            appointment.check_in_time AS start_time,
            appointment.check_out_time AS stop_time

        FROM 
            {database_name}.appointment
        INNER JOIN 
            {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
        INNER JOIN 
            {database_name}.users AS employees ON employees.id = appointment.employee_id
        
        WHERE
            appointment.status IN ('pending', 'check in', 'check out')
            
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








def  admin_start_time(request, id):
    username = request.session.get('gate_keeper')
    if not username:
        return redirect('gate_keeper')
    if request.method == 'POST':
        try:
            Appointment = appointment.objects.get(id=id)
            if Appointment.check_in_time is not None:
                Appointment.status = 'check in'
                Appointment.check_in_time = date_time()
                # visitors_loges = visitors_log.objects.create(appointment_id=id,start_time=date_time(),created_at=date_time())
                Appointment.save()
                print('Appointment:-',Appointment)
                return JsonResponse({'status': 'success'})
            print('yes...no......')
            return JsonResponse({'status': 'error', 'message': 'Start time already set'})
        except Appointment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Appointment not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})





def admin_stop_time(request, id):
    constants = my_constants(request)
    
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    database_name = constants['database_name']
    
    if request.method == 'POST':
        try:
            appointmentes = appointment.objects.get(id=id)
            print('appointmentes:-',appointmentes)
            if appointment.check_in_time and appointment.check_out_time is not None:
                appointmentes.status = 'check out'
                appointmentes.check_out_time = date_time()
                appointmentes.save()
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Cannot stop time'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {(e)}'})        
    
    return JsonResponse({'status': 'success'})



def admin_print_gate_pass(request, id):
    constants = my_constants(request)
    
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    database_name = constants['database_name']
    appointmentes = get_object_or_404(appointment, id=id)
    
    sql_query = f"""
        SELECT 
            appointment.*, 
            visitors.first_name AS visitors_name, 
            employees.first_name AS employee_name,
            visitors.mobile AS visitors_mobile,
            visitors.email AS visitors_email,
            visitors.address AS visitors_address,
            visitors.image AS visitors_image
    
            
        FROM 
            {database_name}.appointment
        INNER JOIN 
            {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
        INNER JOIN 
            {database_name}.users AS employees ON employees.id = appointment.employee_id
        WHERE
            appointment.id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query,[id])
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]
        
    context = {
        'appointment': all_coupon_dtl
    }
    # Render the HTML content for the modal
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        # If the request is AJAX, render just the part of the template needed
        html = render_to_string('dashboard/gate_keeper_dashboard/gate_keeper_print_gate_pass.html', context, request=request)
        return JsonResponse({'html': html})
    # For non-AJAX requests (e.g., direct URL access)
    return render(request, 'dashboard/gate_keeper_dashboard/gate_keeper_print_gate_pass.html', context)







def admin_visitor_user(request):
    constants = my_constants(request)
    
    username = request.session.get('admin')
    if not username:
        return redirect('admin')

    return render(request,'dashboard/admin_dashboard/admin_visitor/admin_visitor_user.html',{'username': username})


def admin_visitor_user_page_ajax(request):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    user_data = constants.get('user_data', {})
    user_id = user_data.get('id')
    database_name = constants['database_name']
    start = int(request.POST.get('start', 0))
    length = int(request.POST.get('length', 10))
    search_value = request.POST.get('search[value]', '')
    
    search = ''
    if search_value:
        search = (
            "AND (users.first_name LIKE %s OR "
            "users.last_name LIKE %s OR "
            "users.email LIKE %s OR "
            "users.gender LIKE %s OR "
            "users.is_active LIKE %s OR "
            "users.created_at LIKE %s OR "
            "users.mobile LIKE %s OR "
            "users.uni_id LIKE %s)"
        )
        search_params = ['%' + search_value + '%'] * 8
    else:
        search_params = []

    sql_query = f"""
        SELECT
            COUNT(*) AS user_count
        FROM
            {database_name}.users
        WHERE
            {database_name}.users.type IN ('visitors')
            {search}
    """

    with connection.cursor() as cursor:
        cursor.execute(sql_query, search_params)
        database_all_data = cursor.fetchall()

    recordsTotal = database_all_data[0][0] if database_all_data else 0

    # Second SQL query to get detailed appointment data
    sql_query = f"""
        SELECT 
            users.*
        FROM 
            {database_name}.users        
        WHERE
            {database_name}.users.type IN ('visitors')            
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


@csrf_exempt
def admin_update_user_status(request):
    constants = my_constants(request)
    email_ides = constants['From_Email']
    if request.method == 'POST':
        user_id = request.POST.get('id')
        is_active = request.POST.get('is_active')

        try:
            useres = user.objects.get(id=user_id)
            useres.is_active = bool(int(is_active))
            useres.save()
            
            if useres.email:
                subject = 'User Status Updated'
                message = (
                    f"Hello {useres.first_name},\n\n"
                    f"Your account status has been updated to {'Active' if useres.is_active else 'Inactive'}.\n"
                    "If you have any questions, please contact support.\n\n"
                    "Best regards,\n"
                    "Visitor Management System"
                )
                from_email = email_ides  # Replace with your email
                recipient_list = [useres.email]  # The user's email
                send_mail(subject, message, from_email, recipient_list)
            return JsonResponse({'success': True})
        except user.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})