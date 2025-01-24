from django.shortcuts import render,HttpResponse,redirect
import json
from django.conf import settings
# Create your views here.
# Create your views here.
from django.contrib import messages
from visitors_app.models import user,roles,countries,states,cities,location,company,department,areas,designation
from django.contrib.auth.hashers import check_password,make_password
from visitors_app.context_processors import my_constants
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from visitors_app.views import date_time
from django.core.files.images import get_image_dimensions
from django.db import connection
from visitors_app.views import generate_vms_string




def admin_user_add(request):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    user_data = constants.get('admin_data', {})
    user_id = user_data.get('id')
    locationes = location.objects.filter(status=1)
    companyes = company.objects.filter(status=1)
    departmentes = department.objects.all()
    role = roles.objects.all()
    designationes = designation.objects.all()
    # area =  areas.objects.all()
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        employee_code = request.POST['employee_code']
        image =request.FILES.get('image')
        if employee_code == '':
            messages.error(request, "Error: Employee Code is Required.", extra_tags='danger')
            return redirect('admin_user_add')
        if user.objects.filter(email=email).exists():
            messages.error(request, 'All ready user exists......')
        else:
            pass
        if user.objects.filter(employee_code=employee_code).exists():
            messages.error(request, 'All ready Employee Code exists......')
        else:
            pass
        
        
        if image:
            if 'image' in request.FILES and request.FILES['image'] and len(request.FILES['image']) != 0:
                image = request.FILES['image']

                try:
                    width, height = get_image_dimensions(image)
                except AttributeError:
                    messages.error(request, "Error: Uploaded file is not an image.",extra_tags='danger')
                    return redirect('admin_user_add')

                # Check if the image format is valid
                valid_formats = ['image/jpeg', 'image/png','image/jpg']
                if image.content_type not in valid_formats:
                    messages.error(request, "Error: Invalid image format.",extra_tags='danger')
                    return redirect('admin_user_add')
            else:
                messages.error(request, "Error: Invalid image format.", extra_tags='danger')
                return redirect('admin_user_add')
        else:
            image = image
        password = request.POST['password']
        mobile = request.POST['mobile']
        
        if mobile != '':
            if user.objects.filter(mobile=mobile).exists():
                messages.error(request, 'Already Mobile exists......')
            else:
                pass
        gender = request.POST['gender']
        address = request.POST['address']
        # type = request.POST['roles_id']
        # print('type_1:-',type)
        # type = type.lower().replace(' ', '_')
        # print('type_2:-',type)
        type = request.POST.getlist('roles_id[]')

        type = ','.join([role.lower().replace(' ', '_') for role in type])
        company_id = request.POST['company_id']
        department_id = request.POST['department_id']
        # area_ides = request.POST.getlist('area_id')
        # area_id = json.dumps(area_ides)
        location_id = request.POST['location_id']
        designation_id = request.POST['designation_id']
        status = request.POST['status']
        password = make_password(password)
        created_at = date_time()
        useres = user(first_name=first_name, last_name=last_name, email=email,password=password,mobile=mobile,gender=gender,address=address,type=type,company_id=company_id,department_id=department_id,location_id=location_id,is_active=status,created_at=created_at,uni_id=generate_vms_string(),image=image,employee_code=employee_code,created_by=user_id,designation_id=designation_id)
        useres.save()
        useres.save()
        messages.success(request, "user successfully created.", extra_tags="success")
        return redirect('admin_user')
    return render(request, 'dashboard/admin_dashboard/admin_user/admin_user_add.html',{'locationes':locationes,'companyes':companyes,'departmentes':departmentes,'roles':role,'designationes':designationes})



def admin_user(request):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')

    return render(request, 'dashboard/admin_dashboard/admin_user/admin_user.html')



def admin_user_ajax_page_ajax(request):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
   
    database_name = constants['database_name']
    start = int(request.POST.get('start', 0))
    length = int(request.POST.get('length', 10))
    search_value = request.POST.get('search[value]', '')
    search = ''
    if search_value != '':
        search = f"""AND (
            {database_name}.users.first_name LIKE "%{search_value}%" OR 
            {database_name}.users.last_name LIKE "%{search_value}%" OR 
            {database_name}.users.email LIKE "%{search_value}%" OR 
            {database_name}.users.mobile LIKE "%{search_value}%" OR 
            {database_name}.company.company_name LIKE "%{search_value}%" OR 
            {database_name}.location.location_name LIKE "%{search_value}%" OR 
            {database_name}.department.department_name LIKE "%{search_value}%" OR
            {database_name}.users.employee_code LIKE "%{search_value}%" OR
            {database_name}.users.type LIKE "%{search_value}%"
        )"""

    # First SQL query to get the count of users
    sql_query = f"""
        SELECT COUNT(*) AS user_count
        FROM {database_name}.users
        LEFT JOIN {database_name}.company ON {database_name}.users.company_id = {database_name}.company.id
        LEFT JOIN {database_name}.location ON {database_name}.users.location_id = {database_name}.location.id
        LEFT JOIN {database_name}.department ON {database_name}.users.department_id = {database_name}.department.id
        LEFT JOIN {database_name}.designation ON {database_name}.users.designation_id = {database_name}.designation.id
        WHERE {database_name}.users.type != 'visitors' {search};
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        database_all_data = cursor.fetchall()

    recordsTotal = database_all_data[0][0] if database_all_data else 0

    # Second SQL query to get detailed user data
    sql_query = f"""
        SELECT 
            {database_name}.users.*,
            {database_name}.company.company_name,
            {database_name}.location.location_name,
            {database_name}.department.department_name,
            {database_name}.designation.allow_check_in
        FROM {database_name}.users
        LEFT JOIN {database_name}.company ON {database_name}.users.company_id = {database_name}.company.id
        LEFT JOIN {database_name}.location ON {database_name}.users.location_id = {database_name}.location.id
        LEFT JOIN {database_name}.department ON {database_name}.users.department_id = {database_name}.department.id
        LEFT JOIN {database_name}.designation ON {database_name}.users.designation_id = {database_name}.designation.id
        WHERE {database_name}.users.type != 'visitors' {search}
        ORDER BY {database_name}.users.id DESC 
        LIMIT {length} OFFSET {start};
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_user_dtl = [dict(zip(columns, row)) for row in database_all_data]

    return JsonResponse({
        "recordsTotal": recordsTotal, 
        "recordsFiltered": recordsTotal, 
        'data': all_user_dtl
    })

# def admin_user_edit(request, id):
#     constants = my_constants(request)
#     username = request.session.get('admin')
#     if not username:
#         return redirect('admin')

#     user_data = constants.get('admin_data', {})
#     user_id = user_data.get('id')
#     all_user= get_object_or_404(user, id=id)

#     all_location = location.objects.filter(status=1)
#     all_company= company.objects.filter(status=1)
#     all_department = department.objects.all()
#     all_roles = roles.objects.all()
#     formatted_role_names = [i.name.lower().replace(' ', '_') for i in all_roles]

#     role_mapping = {role.name.lower().replace(' ', '_'): role.name for role in all_roles}
#     print('role_mapping:-',role_mapping)
#     # all_area = areas.objects.all()
#     # state = states.objects.filter(id=all_location.state_id).first()
#     # citie = cities.objects.filter(id=all_location.city_id).first()
#     if request.method == "POST":
#         all_user.first_name = request.POST['first_name']
#         all_user.employee_code= request.POST['employee_code']
#         all_user.last_name = request.POST['last_name']
#         all_user.email = request.POST['email']
#         all_user.company_id =request.POST['company_id']
#         all_user.department_id =request.POST['department_id']
#         # all_user.area_id =request.POST['area_id']
#         all_user.location_id =request.POST['location_id']
#         all_user.roles_id =request.POST['roles_id']
#         all_user.gender =request.POST['gender']
#         all_user.address =request.POST['address']
#         all_user.is_active =request.POST['status']
#         all_user.mobile = request.POST['mobile']

#         password = request.POST['Password']

#         if password == '':
#             all_user.password = all_user.password
#         if 'image' in request.FILES:
#             file = request.FILES['image']
#             file_extension = file.name.split('.')[-1].lower()
#             if file_extension in ['png', 'jpg', 'jpeg']:
#                 all_user.image = file
#             else:
#                 messages.error(request, 'Error: Invalid image format.', extra_tags='danger')
#                 return redirect('admin_user_edit',id=id) 
#         all_user.created_at = date_time()        
#         all_user.save()
#         messages.success(request, "User successfully updated.", extra_tags="success")
#         return redirect('admin_user')
#     return render(request, 'dashboard/admin_dashboard/admin_user/admin_user_edit.html', {
#         'all_user': all_user,
#         'locationes': all_location,
#         'companyes':all_company, 
#         'departmentes':all_department,
#         'roles':role_mapping,
#         # 'area':all_area,
#         'user_data':user_data,
#         'user_role_key': all_user.type.lower().replace(' ', '_')
#     })
    
    
def admin_user_edit(request, id):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    print('yes')
    user_data = constants.get('admin_data', {})
    all_user = get_object_or_404(user, id=id)
    email = username['user_email']
    mobile = all_user.mobile
    all_email = all_user.email
    all_location = location.objects.filter(status=1)
    all_company = company.objects.filter(status=1)
    all_department = department.objects.all()
    all_roles = roles.objects.all()
    designationes = designation.objects.all()
    #employee_codes = all_user.employee_code
    role_mapping = {role.name.lower().replace(' ', '_'): role.name for role in all_roles}
    
    if request.method == "POST":
        all_user.first_name = request.POST['first_name']
        employee_codes = request.POST['employee_code']
        employee_codes = int(employee_codes)
        all_user.last_name = request.POST['last_name']
        all_user.email = request.POST['email']
        all_user.company_id = request.POST['company_id']
        all_user.department_id = request.POST['department_id'] 
        all_user.location_id = request.POST['location_id']
        all_user.gender = request.POST['gender']
        all_user.address = request.POST['address']
        all_user.is_active = request.POST['status']
        all_user.mobile = request.POST['mobile']
        all_user.designation_id = request.POST['designation_id']
        
        if request.POST['mobile'] != '':
            if mobile != all_user.mobile:
                user_mobile_is_exist  = user.objects.filter(mobile=all_user.mobile).exists()            
                if user_mobile_is_exist == True:
                    messages.error(request, 'User mobile already exists.', extra_tags='danger')
                    return redirect('admin_user_edit', id=id)
        

        if all_email != all_user.email:
            user_email_is_exist  = user.objects.filter(email=all_user.email).exists()            
            if user_email_is_exist == True:
                messages.error(request, 'Email already exists.', extra_tags='danger')
                return redirect('admin_user_edit', id=id)
        
        if employee_codes != all_user.employee_code:
            user_employee_codes_is_exist  = user.objects.filter(employee_code=employee_codes).exists()            
            if user_employee_codes_is_exist == True:
                messages.error(request, 'User Employee Codes already exists.', extra_tags='danger')
                return redirect('admin_user_edit', id=id)
        all_user.employee_code = employee_codes 
        
        # Handle multiple role selections
        selected_roles = request.POST.getlist('roles_id[]')
        all_user.type = ','.join(selected_roles)  # Save roles as a comma-separated string

        password = request.POST['Password']
        if password:
            all_user.password = make_password(password)  # Consider hashing the password

        if 'image' in request.FILES:
            file = request.FILES['image']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension in ['png', 'jpg', 'jpeg']:
                all_user.image = file
            else:
                messages.error(request, 'Error: Invalid image format.', extra_tags='danger')
                return redirect('admin_user_edit', id=id)
        all_user.created_at = date_time()
        all_user.save()
        all_user.save()
        messages.success(request, "User successfully updated.", extra_tags="success")
        return redirect('admin_user')

    # For editing, fetch the user's existing roles
    user_role_keys = all_user.type.split(',')  # Split roles back into a list

    return render(request, 'dashboard/admin_dashboard/admin_user/admin_user_edit.html', {
        'all_user': all_user,
        'locationes': all_location,
        'companyes': all_company,
        'departmentes': all_department,
        'roles': role_mapping,
        'user_role_keys': user_role_keys,  # Pass the user's existing role keys
        'user_data':user_data,
        'designationes':designationes
    })
    
def admin_user_delete(request,id):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    all_user = get_object_or_404(user,id=id)
    all_user.delete()
    data = {
        'status': 1,
        'message': f'User Deleted Successfully.',
    }
    messages.success(request, f"successfully User Deleted!", extra_tags="success")
    return JsonResponse(data)