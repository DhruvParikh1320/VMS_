from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
# Create your views here.
# Create your views here.
from django.contrib import messages
from visitors_app.models import user,roles,countries,states,cities,location,company,department
from django.contrib.auth.hashers import check_password
from visitors_app.context_processors import my_constants
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from visitors_app.views import date_time
from django.db import connection


def admin_department_add(request):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    locationes = location.objects.filter(status=1)
    companyes = company.objects.filter(status=1)
    if request.method == 'POST':
        department_name = request.POST['department_name']
        department_code = request.POST['department_code']
        department_color_code = request.POST['department_color_code']
        company_id = request.POST['company_id']
        location_id = request.POST['location_id']
        created_at = date_time()
        departmente = department(department_name=department_name, department_code=department_code, company_id=company_id,location_id=location_id,created_at=created_at,department_color_code=department_color_code)
        departmente.save()
        messages.success(request, "Departmente successfully created.", extra_tags="success")
        return redirect('admin_department')
        
    return render(request, 'dashboard/admin_dashboard/admin_department/admin_department_add.html',{'locationes':locationes,'companyes':companyes})

def admin_department(request):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    
    return render(request, 'dashboard/admin_dashboard/admin_department/admin_department.html')



def admin_department_ajax_page_ajax(request):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    database_name = constants['database_name']
    start = request.POST.get('start', 0)
    length = request.POST.get('length', 10)
    search_value = request.POST.get('search[value]', '')
    search = ''
    if search_value != '':
        # search = f'WHERE visitors.first_name LIKE "%{search_value}%" or employees.first_name LIKE "%{search_value}%" or appointment.id LIKE "%{search_value}%" or appointment.date LIKE "%{search_value}%" or appointment.time LIKE "%{search_value}%" or appointment.purpose LIKE "%{search_value}%"'
        search = f'AND ( department_name LIKE "%{search_value}%" OR department_code LIKE "%{search_value}%" OR location_name LIKE "%{search_value}%"  OR company_name LIKE "%{search_value}%")'
    # First SQL query to get the count of appointments

    sql_query = f"""
            SELECT COUNT(*) AS department_count
            FROM {database_name}.department
            INNER JOIN {database_name}.location ON {database_name}.department.location_id = {database_name}.location.id
            INNER JOIN {database_name}.company ON {database_name}.department.company_id = {database_name}.company.id
                where 1=1 {search};
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        database_all_data = cursor.fetchall()

    # Check if database_all_data is not empty before accessing its elements
    if database_all_data:
        recordsTotal = database_all_data[0][0]
    else:
        recordsTotal = 0

    # Second SQL query to get detailed appointment data
    sql_query = f"""
        select {database_name}.department.*,{database_name}.location.location_name,{database_name}.company.company_name
        from  {database_name}.department
        inner join {database_name}.location on {database_name}.department.location_id = {database_name}.location.id
        inner join {database_name}.company on {database_name}.department.company_id = {database_name}.company.id
        where 1=1 {search}
    	ORDER BY
    		department.id DESC 
        LIMIT {length} OFFSET {start};
    """
    # Execute the second SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]
    return JsonResponse({"recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, 'data': all_coupon_dtl})



def admin_department_delete(request,id):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    all_department = get_object_or_404(department,id=id)
    all_department.delete()
    data = {
        'status': 1,
        'message': f'Department Deleted Successfully.',
    }
    messages.success(request, f"successfully Department Deleted!", extra_tags="success")
    return JsonResponse(data)



def admin_department_edit(request, id):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')

    user_data = constants.get('admin_data', {})
    user_id = user_data.get('id')
    all_department= get_object_or_404(department, id=id)
    all_location = location.objects.filter(status=1)
    all_company= company.objects.filter(status=1)
    # state = states.objects.filter(id=all_location.state_id).first()
    # citie = cities.objects.filter(id=all_location.city_id).first()
    if request.method == "POST":
        all_department.department_name = request.POST['department_name']
        all_department.department_code = request.POST['department_code']
        all_department.department_color_code =request.POST['department_color_code']
        all_department.company_id = request.POST['company_id']
        all_department.location_id = request.POST['location_id']
        all_department.created_at = date_time()        
        all_department.save()
        messages.success(request, "Department successfully updated.", extra_tags="success")
        return redirect('admin_department')
    return render(request, 'dashboard/admin_dashboard/admin_department/all_department_edit.html', {
        'all_department': all_department,
        'locationes': all_location,
        'companyes':all_company
    })