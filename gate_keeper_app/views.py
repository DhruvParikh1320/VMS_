from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
# Create your views here.
# Create your views here.
from django.contrib import messages
from visitors_app.models import user
from django.contrib.auth.hashers import check_password,make_password
from visitors_app.context_processors import my_constants
from django.contrib.auth import authenticate, login
from visitors_app.views import date_time
import base64
import os
import datetime
from django.http import JsonResponse
from django.shortcuts import render
from PIL import Image
import io
from django.http import JsonResponse
from django.db import connection


from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.
def gate_keeper(request):
    context = {'function_name': 'Gate Keeper', 'ADMIN_STATIC_PATH': settings.ADMIN_STATIC_PATH}
    if request.method == 'POST':
        # email = request.POST.get('email', '')
        employee_code =request.POST.get('employee_code', '')
        password = request.POST.get('password', '')
        user_type = request.POST.get('user_type', '')
        if employee_code == '' or password == '':
            messages.error(request, 'All fields are required.')
            return render(request, 'registration/login.html', context)
        # abc = user.objects.filter(employee_code=employee_code, is_active=True, type='gate_keeper').first()
        user_check = user.objects.filter(employee_code=employee_code, is_active=True).first()
        if user_check is not None:
            user_types = user_check.type
            if 'gate_keeper' in user_types:
                if user_check is not None:
                    if check_password(password, user_check.password):
                        user_name = user_check.first_name
                        gate_keeper = {'user_email': user_check.email, 'user_password': password,'user_name':user_name}
                        request.session['gate_keeper'] = gate_keeper
                        # request.session['username_gate_keeper'] = user_name
                        # request.session['user_type'] = user_type
                        # return render(request, 'dashboard\gate_keeper_dashboard\dashboard.html', {'username': user_name})
                        return redirect(f'gate_keeper_dashboard')
                    else:
                        messages.error(request, 'Invalid Employee Code or Password.')
                else:
                    messages.error(request, 'Invalid Login.')
            else:
                messages.error(request, 'Invalid Login.') 
        else:
            messages.error(request, 'Invalid Login.')

        return render(request, 'registration/login.html', context)

    return render(request, 'registration/login.html', context)



# gate_keeper_dashboard
# def dashboard_view(request, user_type):
#     username = request.session.get(f'username_{user_type}')
#     if not username or request.session.get('user_type') != user_type:
#         return redirect('gate_keeper')
#
#     context = {'username': username}
#     return render(request, f'dashboard/{user_type}_dashboard/dashboard.html', context)
# def gate_keeper_dashboard(request):
    # return dashboard_view(request, 'gate_keeper')

def gate_keeper_dashboard(request):
    constants = my_constants(request)
    database_name = constants['database_name']
    username = request.session.get('gate_keeper')
    if not username:
        return redirect('gate_keeper')
    
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
            date = %s AND check_out_time IS NOT NULL AND check_out_time != ''
        ORDER BY 
            visitors.id DESC;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query_check_out, [total_visitors_date])
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
            date = %s AND check_in_time IS NOT NULL AND check_in_time != '' AND check_out_time = ''
        ORDER BY 
            visitors.id DESC;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query_check_in, [total_visitors_date])
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
        date = %s AND check_in_time = '' AND check_out_time = ''
    ORDER BY 
        visitors.id DESC;
"""
    with connection.cursor() as cursor:
        cursor.execute(sql_query_pending_list, [total_visitors_date])
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
        
        WHERE date = %s AND check_in_time IS NOT NULL AND check_in_time != '' AND check_out_time = '';
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
        WHERE date = %s AND check_out_time IS NOT NULL AND check_out_time != '';
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
        WHERE date = %s;
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
            date = %s AND check_in_time = '' AND check_out_time = '';
    
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql_query_check_in_count, [total_visitors_date])
        check_in_data = cursor.fetchone()
        check_in_count = check_in_data[0] if check_in_data else 0
        
        cursor.execute(sql_query_check_out_count, [total_visitors_date])
        check_out_data = cursor.fetchone()
        check_out_count = check_out_data[0] if check_out_data else 0

        cursor.execute(sql_query_total_visitors, [total_visitors_date])
        total_visitors_data = cursor.fetchone()
        total_visitors_count = total_visitors_data[0] if total_visitors_data else 0

        cursor.execute(sql_query_pending, [total_visitors_date])
        pending_data = cursor.fetchone()
        pending_count = pending_data[0] if pending_data else 0
    
    context = {
        'username': username,
        'DOMAIN_NAME': constants['DOMAIN_NAME'],
        'DOMAIN_ICON': constants['DOMAIN_ICON'],
        'gate_keeper_data': constants['gate_keeper_data'],
        'check_in_count': check_in_count,  
        'check_out_count': check_out_count,  
        'total_visitors_count': total_visitors_count,
        'pending_count': pending_count,
        'all_check_out_dtl': all_check_out_dtl,
        'all_check_in_dtl': all_check_in_dtl,
        'all_pending_list':all_pending_list
    }

    return render(request, 'dashboard/gate_keeper_dashboard/dashboard.html', context)


def gate_keepe_logout(request):
    if 'gate_keeper' in request.session:
        del request.session['gate_keeper']
    return redirect('gate_keeper')


def gate_keeper_edit(request):
    constants = my_constants(request)
    
    username = request.session.get('gate_keeper')
    if not username:
        return redirect('gate_keeper')
    user_data = constants.get('user_data', {})
    
        # return redirect('gate_keeper')
    email = username['user_email']
    user_name = username['user_name']
    gate_keeper_user = user.objects.get(email=email)
    mobile = gate_keeper_user.mobile
    
    if request.method == "POST":
        gate_keeper_user.first_name = request.POST['Firstname']
        
        gate_keeper_user.last_name = request.POST['Lastname']
        
        gate_keeper_user.email = request.POST['Email']
        
        # visitors_user.password = request.POST['Password']
        #
        # visitors_user.password = request.POST['Confirm_Password']
        
        gate_keeper_user.address = request.POST['Address']
        
        gate_keeper_user.mobile = request.POST['mobile']
        
        if mobile != gate_keeper_user.mobile:
            user_mobile_is_exist  = user.objects.filter(mobile=gate_keeper_user.mobile).exists()            
            if user_mobile_is_exist == True:
                messages.error(request, 'User mobile already exists.', extra_tags='danger')
                return redirect('gate_keeper_edit')

        if email != gate_keeper_user.email:
            user_email_is_exist  = user.objects.filter(email=gate_keeper_user.email).exists()            
            if user_email_is_exist == True:
                messages.error(request, 'Email already exists.', extra_tags='danger')
                return redirect('gate_keeper_edit')
        
        gate_keeper_user.gender = request.POST['gender']
        password = request.POST['Password']
        confirm_password = request.POST['Confirm_Password']

        if 'gender' not in request.POST or request.POST['gender'] == ''  or request.POST['gender'] == 'Choose Gender':
            messages.error(request, 'Please choose a gender.', extra_tags='danger')
            return redirect('gate_keeper_edit')
                
        if password == '' and confirm_password == '':
            gate_keeper_user.password = gate_keeper_user.password
        
        elif password == confirm_password:
            gate_keeper_user.password = make_password(confirm_password)
        else:
            messages.error(request, 'Passwords do not match.', extra_tags='danger')
            return redirect('gate_keeper_edit')

        if 'image' in request.FILES:
            file = request.FILES['image']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension in ['png', 'jpg', 'jpeg']:
                gate_keeper_user.image = file
            else:
                messages.error(request, 'Error: Invalid image format.', extra_tags='danger')
                return redirect('gate_keeper_edit')
        if 'document' in request.FILES:
            document = request.FILES['document']
            document_extension = document.name.split('.')[-1].lower()
            if document_extension in ['png', 'jpg', 'jpeg', 'pdf']:
                gate_keeper_user.document = document
            else:
                messages.error(request, 'Error: Invalid document format.', extra_tags='danger')
                return redirect('gate_keeper_edit')
        gate_keeper_user.save()
        gate_keeper_user.save()
        
        messages.success(request, f"Successfully Update:", extra_tags="success")
    return render(request,'dashboard/gate_keeper_dashboard/gate_keeper_profile/profile_edit.html',{'gate_keeper_user':gate_keeper_user,'username': username,'user_data': constants['gate_keeper_data']})
    


@csrf_exempt
def capture_photo(request):
    print('request')
    if request.method == 'POST':
        # Parse JSON body
        image_data = request.POST.get('image')

        name = request.POST.get('name')


        if image_data:
            # Decode base64 image data
            base64_data = image_data.split(",")[1]  # Extract base64 part
            binary_data = base64.b64decode(base64_data)  # Decode base64 data

            image = Image.open(io.BytesIO(binary_data))  # Convert binary data to image


            # Save the image to a directory
            save_directory = 'user/'  # Ensure this directory exists or use a path within Django's MEDIA_ROOT
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
                print('save_directory:-',save_directory)
            print('save_directory:-',save_directory)
            filename = name.replace(' ','_')      
            filename = f"{filename}.jpg"
            face_image_path = os.path.join(save_directory, filename)
            print('face_image_path:-',face_image_path)
            image.save(face_image_path)  # Save image file

            return JsonResponse({'status': 'success', 'filename': filename})
        else:
            return JsonResponse({'status': 'error', 'message': 'No image data provided'}, status=400)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
        
        


@csrf_exempt  # Only use this if you're sure about CSRF handling
def get_mobile_numbers(request):
    if request.method == 'GET':
        # Fetch all mobile numbers from the User model
        mobile_numbers = user.objects.values_list('mobile', flat=True)
        return JsonResponse(list(mobile_numbers), safe=False)

@csrf_exempt
def autocomplete_mobile_numbers(request):
    if request.method == 'GET':
        # query = request.GET.get('term', '')  # Get the search term from the query parameters
        # # Filter mobile numbers that contain the search term
        # mobile_numbers = user.objects.filter(mobile__icontains=query).values_list('mobile', flat=True)
        # return JsonResponse(list(mobile_numbers), safe=False)
        query = request.GET.get('term', '')  # Get the search term from the query parameters
        # Use raw SQL query to fetch mobile numbers that start with the search term
        # sql = "SELECT mobile FROM users WHERE mobile LIKE %s"
        visitor_types = ['visitors']
        # sql = "SELECT mobile, first_name,id FROM users WHERE mobile LIKE %s AND type IN %s"
        search_term = query + '%'  # Match only mobile numbers starting with the search term
        # mobile_numbers = user.objects.raw(sql, [search_term])
        placeholders = ', '.join(['%s'] * len(visitor_types))  # Create placeholders for visitor types
        sql = f"SELECT mobile, first_name,last_name, id FROM users WHERE mobile LIKE %s AND type IN ({placeholders})"

        with connection.cursor() as cursor:
            # Execute the query with the search term and visitor types
            cursor.execute(sql, [search_term] + visitor_types)
            results = cursor.fetchall()
        # Convert the result to a list of mobile numbers
        # mobile_list = [obj.mobile for obj in mobile_numbers]
        # return JsonResponse(mobile_list, safe=False)
        # with connection.cursor() as cursor:
        #     cursor.execute(sql, (search_term,visitor_types))
        #     results = cursor.fetchall()

        # mobile_numbers = [row[0] for row in results]
        mobile_numbers =  [f"{row[0]} - {row[1]} - {row[2]} - {row[3]}" for row in results]

        return JsonResponse(list(mobile_numbers), safe=False, status=200)

@csrf_exempt
def get_user_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mobile_number = data.get('mobile')
        # Use filter() to get all matching users
        user_id = data.get('id')
        users = user.objects.filter(mobile=mobile_number,id=user_id)

        if users.exists():
            # If you just want the first user
            useres = users.first()
            base_url = request.build_absolute_uri('/')[:-1]
            response_data = {
                'success': True,
                'user': {
                    'user_id':useres.id,
                    'first_name': useres.first_name,
                    'last_name': useres.last_name,
                    'email': useres.email,
                    'genderSelect':useres.gender,
                    'address':useres.address,
                    'image': f"{base_url}/user/{useres.image}" if useres.image else None,
                    'mobile_number':mobile_number
                }
            }
        else:
            response_data = {'success': False, 'message': 'User not found.'}

        return JsonResponse(response_data)

@csrf_exempt
def autocomplete_emails(request):
    if request.method == 'GET':
       
        query = request.GET.get('term', '') 
      
        visitor_types = ['visitors']

        search_term = query + '%' 

        placeholders = ', '.join(['%s'] * len(visitor_types)) 
        sql = f"SELECT email, first_name,last_name, id FROM users WHERE email LIKE %s AND type IN ({placeholders})"

        with connection.cursor() as cursor:
  
            cursor.execute(sql, [search_term] + visitor_types)
            results = cursor.fetchall()

        email =  [f"{row[0]} - {row[1]} - {row[2]} - {row[3]}" for row in results]

        return JsonResponse(list(email), safe=False, status=200)


@csrf_exempt
def get_user_data_by_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email_id = data.get('email')
        # Use filter() to get all matching users
        user_id = data.get('id')
        users = user.objects.filter(email=email_id,id=user_id)

        if users.exists():
            # If you just want the first user
            useres = users.first()
            base_url = request.build_absolute_uri('/')[:-1]
            response_data = {
                'success': True,
                'user': {
                    'user_id':useres.id,
                    'first_name': useres.first_name,
                    'last_name': useres.last_name,
                    'email': email_id,
                    'genderSelect':useres.gender,
                    'address':useres.address,
                    'image': f"{base_url}/user/{useres.image}" if useres.image else None,
                    'mobile_number':useres.mobile
                }
            }
        else:
            response_data = {'success': False, 'message': 'User not found.'}

        return JsonResponse(response_data)


def visitor_details(request, id):
    constants = my_constants(request)
    database_name = constants['database_name']
    
    sql_query = f"""
        SELECT 
            appointment.*, 
            visitors.first_name AS visitors_name,
            visitors.last_name AS visitors_last_name, 
            visitors.uni_id AS visitors_uni_id,
            visitors.gender AS visitors_gender,
            visitors.address AS visitors_address,
            visitors.image AS visitors_image,
            visitors.mobile AS visitors_mobile,  
            visitors.email AS visitors_email, 
            employees.first_name AS employee_name,
            employees.last_name AS employee_last_name,
            employees.gender AS employee_gender,
            employees.address AS employee_address,
            employees.image AS employee_image,
            employees.mobile AS employee_mobile,  
            employees.email AS employee_email,  
            appointment.date AS appointment_date,
            appointment.time AS appointment_time,
            appointment.status AS status,
            appointment.purpose AS purpose,
            appointment.detail AS details,
            appointment.visitors_type AS visitors_type,
            appointment.visitors_timing AS visitors_timing,
            appointment.employee_approval AS employee_approval,
            appointment.created_by AS created_by,
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
            {database_name}.company AS company ON company.id = employees.company_id  
        INNER JOIN
            {database_name}.department AS department ON department.id = employees.department_id
        INNER JOIN
            {database_name}.location AS location ON location.id = employees.location_id
        INNER JOIN 
            {database_name}.gate_pass_no AS gate_pass ON gate_pass.appointment_id = appointment.id
        WHERE
            appointment.id = %s;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql_query, [id])
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        appointment_data = [dict(zip(columns, row)) for row in database_all_data]
    
    context = {
        'appointment': appointment_data,
        'user_data': constants['admin_data']
    }
    
    return render(request, 'dashboard/gate_keeper_dashboard/visitor_details.html', context)