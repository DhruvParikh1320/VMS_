import datetime

from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
# Create your views here.
from django.contrib import messages
from .models import user,appointment,safety_training
from django.contrib.auth.hashers import check_password ,make_password
from django.contrib.auth import authenticate, login
from django.core.files.images import get_image_dimensions
from django.http import JsonResponse
from django.db import connection
from .views import date_time
from django.shortcuts import get_object_or_404
from .context_processors import my_constants

database_name = 'vms'
def visitors_appointment(request):
    # username = request.session.get('visitors')
    # user_type = request.session.get('user_type')
    # print('user_type:-', user_type)
    # if not username :
    #     return redirect('visitors')
    
    constants = my_constants(request)
    username = request.session.get('visitors')
    if not username:
        return redirect('visitors')
    user_data = constants.get('user_data', {})
    user_id = user_data.get('id')
    useres = user.objects.filter(id=user_id).first()  
    if not useres.is_safety_training:  
        return redirect('visitors_dashboard')
        # return redirect('gate_keeper')
    # all_appointmentses = appointment.objects.all().order_by('-created_at')
    # all_appointments = []
    # for appointmentes in all_appointmentses:
    #     visitor_name = user.objects.get(id=appointmentes.visitors_id).first_name
    #     employee_name = user.objects.get(id=appointmentes.employee_id).first_name
    #     all_appointments.append({
    #         'id':appointmentes.id,
    #         'visitors_id': visitor_name,
    #         'employee_id': employee_name,
    #         'date': appointmentes.date,
    #         'time': appointmentes.time,
    #         'status': appointmentes.status,
    #         'created_at':appointmentes.created_at,
    #         'updated_at':appointmentes.updated_at
    #     })
    # employees = []
    # visitors = []
    
    # for appointmentes in all_appointments:
    #     # Assuming `appointment.employee_first_name` and `appointment.visitor_first_name` are fields
    #     employee = user.objects.filter(type='employee', first_name=appointmentes.employee_first_name).first()
    #     if employee:
    #         employees.append(employee)
        
    #     visitor = user.objects.filter(type='visitors', first_name=appointmentes.visitor_first_name).first()
    #     if visitor:
    #         visitors.append(visitor)
    return render(request,'dashboard/visitors_dashboard/appointment.html',{'username': username})

def appointment_page_ajax(request):
    constants = my_constants(request)
    username = request.session.get('visitors')
    if not username:
        return redirect('visitors')
    
    user_data = constants.get('user_data', {})
    user_id = user_data.get('id')
    if not user_id:
        return JsonResponse({"error": "User ID is missing"}, status=400)

    # Validate POST data
    try:
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
    except ValueError:
        return JsonResponse({"error": "Invalid pagination parameters"}, status=400)

    search_value = request.POST.get('search[value]', '').strip()

    # Secure database name usage

    database_name = constants['database_name']
    if not database_name.isidentifier():
        return JsonResponse({"error": "Invalid database name"}, status=400)

    search = ""
    if search_value:
        search = """
            AND (
                visitors.first_name LIKE %s OR 
                employees.first_name LIKE %s OR 
                appointment.id LIKE %s OR 
                appointment.date LIKE %s OR 
                appointment.time LIKE %s OR 
                appointment.purpose LIKE %s
            )
        """

    # First SQL query to get the count of appointments
    count_query = f"""
        SELECT COUNT(*) AS appointment_count
        FROM {database_name}.appointment
        INNER JOIN {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
        INNER JOIN {database_name}.users AS employees ON employees.id = appointment.employee_id
        WHERE appointment.visitors_id = %s {search};
    """
    params = [user_id] + ([f"%{search_value}%"] * 6 if search_value else [])
    with connection.cursor() as cursor:
        cursor.execute(count_query, params)
        recordsTotal = cursor.fetchone()[0] if cursor.rowcount > 0 else 0

    # Second SQL query to get detailed appointment data
    data_query = f"""
        SELECT 
            appointment.*, 
            visitors.first_name AS visitors_name, 
            employees.first_name AS employee_name
        FROM {database_name}.appointment
        INNER JOIN {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
        INNER JOIN {database_name}.users AS employees ON employees.id = appointment.employee_id
        WHERE appointment.visitors_id = %s {search}
        ORDER BY appointment.id DESC
        LIMIT %s OFFSET %s;
    """
    params = [user_id] + ([f"%{search_value}%"] * 6 if search_value else []) + [length, start]
    with connection.cursor() as cursor:
        cursor.execute(data_query, params)
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return JsonResponse({"recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, 'data': all_coupon_dtl})


def visitors_appointment_add(request):
    constants = my_constants(request)
    username = request.session.get('visitors')
    # user_type = request.session.get('user_type')
    # print('user_type:-', user_type)
    if not username :
        return redirect('visitors')
        # return redirect('gate_keeper')
    all_employee = user.objects.filter(type='employee',is_active=1)
    user_data = constants.get('user_data', {})
    user_id = user_data.get('id')
    if request.method == "POST":
        visitors_id = user_id
        employee_id = request.POST['employee']
        date = request.POST['date']
        time = request.POST['time']
        purpose = request.POST['Purpose']
        visitors_type = request.POST['visitors_type']
        detail = request.POST['detail']
        if employee_id == '' or employee_id == 'Choose employee' or date == '' or time == '' or purpose == '' or visitors_type == 'Choose visitors type' or visitors_type == '':
            messages.error(request, "All fields are required.", extra_tags="danger")
            return render(request, 'dashboard/visitors_dashboard/appointment_add.html', {
                'username': username, 'all_employee': all_employee
            })
        try:
            appointment_obj = appointment(
                visitors_id=visitors_id,
                employee_id=employee_id,
                date=date,
                time=time,
                status='pending',  # Assuming 'scheduled' is the default status
                created_at =date_time(),
                purpose = purpose,
                visitors_type = visitors_type,
                detail = detail
            )
            appointment_obj.save()
            visitor = user.objects.get(id=visitors_id)
            employee = user.objects.get(id=employee_id)
            
            messages.success(request, "Appointment successfully created.", extra_tags="success")
            return redirect('visitors_appointment')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}", extra_tags="danger")
    return render(request,'dashboard/visitors_dashboard/appointment_add.html',{'username': username,'all_employee':all_employee})


def visitors_appointment_edit(request,id):
    constants = my_constants(request)
    username = request.session.get('visitors')

    if not username :
        return redirect('visitors')
    user_data = constants.get('user_data', {})
    user_id = user_data.get('id')
    all_appointment = get_object_or_404(appointment,id=id)
    all_employee = user.objects.filter(type='employee',is_active=1)
    if request.method == "POST":
        all_appointment.visitors_id = user_id
        all_appointment.employee_id = request.POST['employee']
        all_appointment.purpose = request.POST['Purpose']
        all_appointment.date = request.POST['date']
        all_appointment.time = request.POST['time']
        all_appointment.detail = request.POST['detail']
        all_appointment.visitors_type = request.POST['visitors_type']
        all_appointment.updated_at = date_time()
        if  request.POST['employee'] ==  'Choose employee' or request.POST['employee'] ==  '' or request.POST['visitors_type'] == '' or request.POST['visitors_type'] == 'Choose visitors type' :
            messages.error(request, "All fields are required.", extra_tags="danger")
            # return render(request, 'dashboard/visitors_dashboard/appointment_edit.html', {
            #     'username': username, 'all_appointment': all_appointment, 'all_employee': all_employee
            # })
            return redirect('visitors_appointment_edit',id=id)
        all_appointment.save()
        messages.success(request, "Appointment successfully updated.", extra_tags="success")
        return redirect('visitors_appointment')
    return render(request,'dashboard/visitors_dashboard/appointment_edit.html',{'username': username,'all_appointment':all_appointment,'all_employee':all_employee})


def visitors_appointment_delete(request,id):
    username = request.session.get('visitors')
    if not username :
        return redirect('visitors')
    all_appointment = get_object_or_404(appointment,id=id)
    all_appointment.delete()
    data = {
        'status': 1,
        'message': f'Appointment Deleted Successfully.',
    }
    messages.success(request, f"successfully Appointment Deleted!", extra_tags="success")
    return JsonResponse(data)
    

def visitors_appointment_upcoming_appointment(request):
    username = request.session.get('visitors')
    if not username :
        return redirect('visitors')
    # today = datetime.datetime.today().date()
    #
    # all_appointments_today = appointment.objects.filter(date__gte=today).order_by('date')
    # all_appointments = []
    # for appointmentes in all_appointments_today:
    #     visitor_name = user.objects.get(id=appointmentes.visitors_id).first_name
    #     employee_name = user.objects.get(id=appointmentes.employee_id).first_name
    #     all_appointments.append({
    #         'id':appointmentes.id,
    #         'visitors_id': visitor_name,
    #         'employee_id': employee_name,
    #         'date': appointmentes.date,
    #         'time': appointmentes.time,
    #         'status': appointmentes.status,
    #         'created_at':appointmentes.created_at,
    #         'updated_at':appointmentes.updated_at
    #     })
    return render(request,'dashboard/visitors_dashboard/upcoming_appointment.html')

def upcoming_appointment_page_ajax(request):
    constants = my_constants(request)
    username = request.session.get('visitors')
    if not username:
        return redirect('visitors')
    user_data = constants.get('user_data', {})
    user_id = user_data.get('id')
    start = request.POST.get('start', 0)
    # length = request.POST['length']
    length = request.POST.get('length', 10)
    # search_value = request.POST['search[value]']
    search_value = request.POST.get('search[value]', '')
    # offset_value =
    search = ''
    if search_value:
        search = f'AND (visitors.first_name LIKE "%{search_value}%" OR employees.first_name LIKE "%{search_value}%" OR appointment.id LIKE "%{search_value}%" OR appointment.date LIKE "%{search_value}%" OR appointment.time LIKE "%{search_value}%" OR appointment.purpose LIKE "%{search_value}%")'

    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%I:%M %p").lstrip('0') # 12-hour format

    # SQL date and time filter
    date_filter = f"""          
            AND(appointment.date > '{date}' OR (appointment.date = '{date}' AND appointment.time > '{time}'))            
        """
    user_id_filter = f"AND appointment.visitors_id = {user_id}"
    # First SQL query to get the count of appointments
    sql_query_count = f"""
            SELECT 
                COUNT(*) AS appointment_count
            FROM 
                vms.appointment
            INNER JOIN 
                vms.users AS visitors ON visitors.id = appointment.visitors_id
            INNER JOIN 
                vms.users AS employees ON employees.id = appointment.employee_id
            WHERE 1=1
            {search} 
            {date_filter} {user_id_filter};
        """
    # Execute the first SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query_count)
        database_all_data = cursor.fetchall()

    # Check if database_all_data is not empty before accessing its elements
    recordsTotal = database_all_data[0][0] if database_all_data else 0

    # Second SQL query to get detailed appointment data
    sql_query_detail = f"""
            SELECT 
                appointment.*, 
                visitors.first_name AS visitors_name, 
                employees.first_name AS employee_name
            FROM 
                vms.appointment
            INNER JOIN 
                vms.users AS visitors ON visitors.id = appointment.visitors_id
            INNER JOIN 
                vms.users AS employees ON employees.id = appointment.employee_id
            WHERE 1=1
            {search}
            {date_filter} 
            {user_id_filter}
            ORDER BY 
                appointment.time ASC
            LIMIT {length} OFFSET {start};
        """
    # Execute the second SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query_detail)
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]

    return JsonResponse({"recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, 'data': all_coupon_dtl})