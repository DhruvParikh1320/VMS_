from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
# Create your views here.
# Create your views here.
from django.contrib import messages
from visitors_app.models import user, roles, countries, states, cities, location, company, department,designation
from django.contrib.auth.hashers import check_password
from visitors_app.context_processors import my_constants
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from visitors_app.views import date_time
from django.db import connection


def admin_designation_add(request):
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    locationes = location.objects.filter(status=1)
    companyes = company.objects.filter(status=1)
    if request.method == 'POST':
        designation_name = request.POST['designation_name']
        designation_allow_check_in = request.POST['allow_check_in']

        created_at = date_time()
        designationes = designation(name=designation_name, allow_check_in=designation_allow_check_in,
                                created_at=created_at)
        designationes.save()
        messages.success(request, "Designation successfully created.", extra_tags="success")
        return redirect('admin_designation')
    return render(request, 'dashboard/admin_dashboard/admin_designation/admin_designation_add.html',
                  {'locationes': locationes, 'companyes': companyes})


def admin_designation(request):
    username = request.session.get('admin')
    if not username:
        return redirect('admin')

    return render(request, 'dashboard/admin_dashboard/admin_designation/admin_designation.html')


def admin_designation_ajax_page_ajax(request):
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
        search = f'AND ( name LIKE "%{search_value}%" )'
    # First SQL query to get the count of appointments

    sql_query = f"""
            SELECT COUNT(*) AS designation_count
            FROM {database_name}.designation
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
        select {database_name}.designation.*
        from  {database_name}.designation
        where 1=1 {search}
    	ORDER BY
    		designation.id DESC 
        LIMIT {length} OFFSET {start};
    """
    # Execute the second SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]
    return JsonResponse({"recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, 'data': all_coupon_dtl})


def admin_designation_delete(request, id):
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    all_designation = get_object_or_404(designation, id=id)
    all_designation.delete()
    data = {
        'status': 1,
        'message': f'Designation Deleted Successfully.',
    }
    messages.success(request, f"successfully Designation Deleted!", extra_tags="success")
    return JsonResponse(data)


def admin_designation_edit(request, id):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')

    user_data = constants.get('admin_data', {})
    user_id = user_data.get('id')
    all_designation = get_object_or_404(designation, id=id)
    if request.method == "POST":
        all_designation.name = request.POST['designation_name']
        all_designation.allow_check_in = request.POST['allow_check_in']
        all_designation.updated_at = date_time()
        all_designation.save()
        messages.success(request, "Designation successfully updated.", extra_tags="success")
        return redirect('admin_designation')
    return render(request, 'dashboard/admin_dashboard/admin_designation/all_designation_edit.html', {'all_designation': all_designation})