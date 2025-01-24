from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
# Create your views here.
# Create your views here.
from django.contrib import messages
from visitors_app.models import user,roles,appointment
from django.db.models import Count
from django.contrib.auth.hashers import check_password,make_password
from visitors_app.context_processors import my_constants
from django.shortcuts import get_object_or_404
from django.db import connection
from visitors_app.views import date_time
from django.http import JsonResponse
from django.db.models import Q
def admin(request):
    context = {'function_name': 'Admin', 'ADMIN_STATIC_PATH': settings.ADMIN_STATIC_PATH}
    if request.method == 'POST':
        employee_code =request.POST.get('employee_code', '')
        password = request.POST.get('password', '')
        user_type = request.POST.get('user_type', '')
        if employee_code == '' or password == '':
            messages.error(request, 'All fields are required.')
            return render(request, 'registration/login.html', context)
        if employee_code == '001' and password == 'hex@123':
            admin = {
                 'user_email': 'admin_by@example.com',
                 'user_password': 'hex@123',
                 'user_name': 'Admin'
             }
            request.session['admin'] = admin
            return redirect('admin_dashboard')
        else:
            user_check = user.objects.filter(employee_code=employee_code, is_active=True).first()
            if user_check is not None:
                user_types = user_check.type
                if 'admin' in user_types:            
                    if user_check is not None:
                        if check_password(password, user_check.password):
                            user_name = user_check.first_name
                            print('yes......')
                            admin = {'user_email': user_check.email, 'user_password': password,'user_name':user_name}
                            request.session['admin'] = admin
                          
                            return redirect(f'admin_dashboard')
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

# def admin(request):
#     context = {'function_name': 'Admin', 'ADMIN_STATIC_PATH': settings.ADMIN_STATIC_PATH}
#     if request.method == 'POST':
#         # email = request.POST.get('email', '')
#         employee_code =request.POST.get('employee_code', '')
#         password = request.POST.get('password', '')
#         user_type = request.POST.get('user_type', '')
#         if employee_code == '' or password == '':
#             messages.error(request, 'All fields are required.')
#             return render(request, 'registration/login.html', context)
#         # abc = user.objects.filter(email=email, is_active=True, type='admin').first()
#         # abc = user.objects.filter(email=email, is_active=True, type__in=['admin', 'gate_keeper']).first()
#         # abc = user.objects.filter(email=email, is_active=True, type__in=('admin')).first()
#         # with connection.cursor() as cursor:
#         #     cursor.execute("SELECT * FROM users WHERE email = %s AND type IN (%s)", [email, 'admin'])
#         #     abc = cursor.fetchone()
#         #     print('abc:-',abc)
 
#         user_check = user.objects.filter(employee_code=employee_code, is_active=True).first()
#         if user_check is not None:
#             user_types = user_check.type
#             if 'admin' in user_types:
#                 if user_check is not None:
#                     if check_password(password, user_check.password):
#                         user_name = user_check.first_name
#                         print('yes......')
#                         admin = {'user_email': user_check.email, 'user_password': password,'user_name':user_name}
#                         request.session['admin'] = admin
#                         # request.session['username_gate_keeper'] = user_name
#                         # request.session['user_type'] = user_type
#                         # return render(request, 'dashboard\gate_keeper_dashboard\dashboard.html', {'username': user_name})
#                         return redirect(f'admin_dashboard')
#                     else:
#                         messages.error(request, 'Invalid Employee Code or Password.')
#                 else:
#                     messages.error(request, 'Invalid Login.')
#             else:
#                 messages.error(request, 'Invalid Login.')
#         else:
#             messages.error(request, 'Invalid Login.')
#         else:
#             if employee_code == '001' and password == '1':
#                 # Allow login with employee_code and password both set to '1' (admin creation setup)
#                 # Create an admin session without checking the database
#                 admin_session_data = {
#                     'user_email': 'admin@example.com',
#                     'user_password': password,  # Store in session temporarily (not recommended in production)
#                     'user_name': 'Admin'
#                 }
#                 request.session['admin'] = admin_session_data
#                 return redirect('admin_dashboard')
#             else:
#                 messages.error(request, 'No users in the system, please contact support or use the setup credentials.')



#         return render(request, 'registration/login.html', context)

#     return render(request, 'registration/login.html', context)











# def admin(request):
#     context = {'function_name': 'Admin', 'ADMIN_STATIC_PATH': settings.ADMIN_STATIC_PATH}
#     if request.method == 'POST':
#         # email = request.POST.get('email', '')
#         employee_code =request.POST.get('employee_code', '')
#         password = request.POST.get('password', '')
#         user_type = request.POST.get('user_type', '')
#         if employee_code == '' or password == '':
#             messages.error(request, 'All fields are required.')
#             return render(request, 'registration/login.html', context)

#         if employee_code == '001' and password == 'hex@123':
#             admin = {
#                 'user_email': 'admin_by@example.com',
#                 'user_password': 'hex@123',
#                 'user_name': 'Admin'
#             }
#             request.session['admin'] = admin
#             return redirect('admin_dashboard')
#         else:
#             messages.error(request, 'No users in the system, please contact support or use the setup credentials.')
#         return render(request, 'registration/login.html', context)

#     return render(request, 'registration/login.html', context)

def admin_dashboard(request):
    constants = my_constants(request)

    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    user_data = constants.get('admin_data', {})
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
        'admin_data': constants['admin_data'],
        'check_in_count': check_in_count,  
        'check_out_count': check_out_count,  
        'total_visitors_count': total_visitors_count,
        'pending_count': pending_count,
        'all_check_out_dtl': all_check_out_dtl,
        'all_check_in_dtl': all_check_in_dtl,
        'all_pending_list':all_pending_list
    }

    return render(request, 'dashboard/admin_dashboard/dashboard.html', context)
    
    
    
    
    
    
    
    
    
#     today_time = date_time()  # Get today's date
#    # Format the date
#     today_time = today_time.split(' ')[0]
#     print('today_time:-',today_time)
    
#     with connection.cursor() as cursor:
#         cursor.execute(f"""
#             SELECT COUNT(*) 
#             FROM vms.appointment 
#             WHERE 
#             check_in_time >= %s
#         """, [today_time])
        
#         row = cursor.fetchone()
#         check_in_count = row[0]

#         cursor.execute(f"""
#             SELECT COUNT(*) 
#             FROM vms.appointment 
#             WHERE 
#             check_out_time >= %s
#         """, [today_time])
#         row = cursor.fetchone()
#         check_out_count = row[0]

#     context = {

#         'username': username,
#         'DOMAIN_NAME': constants['DOMAIN_NAME'],
#         'DOMAIN_ICON': constants['DOMAIN_ICON'],
#         'admin_data': constants['admin_data'],
#         'check_in_count': check_in_count,
#         'check_out_count':check_out_count
#     }
#     return render(request, 'dashboard/admin_dashboard/dashboard.html', context)



def admin_logout(request):
    if request.session.get('admin'):
        del request.session['admin']
    return redirect('admin')



def admin_edit(request):
    constants = my_constants(request)
    
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    user_data = constants.get('admin_data', {})
    
        # return redirect('gate_keeper')
    email = username['user_email']
    user_name = username['user_name']

    admin_user = user.objects.get(email=email)
    mobile = admin_user.mobile
    if request.method == "POST":
        admin_user.first_name = request.POST['Firstname']
        
        admin_user.last_name = request.POST['Lastname']
        
        admin_user.email = request.POST['Email']
        
        # visitors_user.password = request.POST['Password']
        #
        # visitors_user.password = request.POST['Confirm_Password']
        
        admin_user.address = request.POST['Address']
        
        admin_user.mobile = request.POST['mobile']
        
        admin_user.gender = request.POST['gender']
        password = request.POST['Password']
        confirm_password = request.POST['Confirm_Password']
        
        if mobile != admin_user.mobile:
            user_mobile_is_exist  = user.objects.filter(mobile=admin_user.mobile).exists()            
            if user_mobile_is_exist == True:
                messages.error(request, 'User mobile already exists.', extra_tags='danger')
                return redirect('admin_edit')

        if email != admin_user.email:
            user_email_is_exist  = user.objects.filter(email=admin_user.email).exists()            
            if user_email_is_exist == True:
                messages.error(request, 'Email already exists.', extra_tags='danger')
                return redirect('admin_edit')
        
        if 'gender' not in request.POST or request.POST['gender'] == '':
            messages.error(request, 'Please choose a gender.', extra_tags='danger')
            return redirect('admin_edit')

        
        
        if password == '' and confirm_password == '':
            admin_user.password = admin_user.password
        
        elif password == confirm_password:
            admin_user.password = make_password(confirm_password)
        else:
            messages.error(request, 'Passwords do not match.', extra_tags='danger')
            return redirect('admin_edit')

        if 'image' in request.FILES:
            file = request.FILES['image']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension in ['png', 'jpg', 'jpeg']:
                admin_user.image = file
            else:
                messages.error(request, 'Error: Invalid image format.', extra_tags='danger')
                return redirect('admin_edit')
        if 'document' in request.FILES:
            document = request.FILES['document']
            document_extension = document.name.split('.')[-1].lower()
            if document_extension in ['png', 'jpg', 'jpeg', 'pdf']:
                admin_user.document = document
            else:
                messages.error(request, 'Error: Invalid document format.', extra_tags='danger')
                return redirect('admin_edit')
        admin_user.save()
        admin_user.save()
        messages.success(request, f"Successfully Update:", extra_tags="success")
    return render(request,'dashboard/admin_dashboard/admin_profile/profile_edit.html',{'admin_user':admin_user,'username': username,'user_data': constants['admin_data']})