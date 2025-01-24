from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
# Create your views here.
# Create your views here.
from django.contrib import messages
from visitors_app.models import user,roles,countries,states,cities,location,areas
from django.contrib.auth.hashers import check_password
from visitors_app.context_processors import my_constants
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from visitors_app.views import date_time
from django.db import connection



def admin_area_add(request):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    all_location = location.objects.filter(status=1)
    if request.method == 'POST':
        area_code = request.POST['area_code']
        area_name = request.POST['area_name']
        location_id = request.POST['location_id']
        created_at = date_time()
        existing_area_code = areas.objects.filter(area_code=area_code).first()
        existing_area_name = areas.objects.filter(area_code=area_name).first()
        if existing_area_code or existing_area_name:
            messages.error(request, "Areas with this already exists..", extra_tags="danger")
            return redirect('admin_area_add')
        
        area = areas(area_code=area_code, area_name=area_name, location_id=location_id,created_at=created_at)
        area.save()
        messages.success(request, "Areas successfully updated.", extra_tags="success")
        return redirect('admin_area')
    return render(request, 'dashboard/admin_dashboard/admin_areas/admin_areas_add.html',{'location':all_location})

def admin_area(request):
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    return render(request, 'dashboard/admin_dashboard/admin_areas/admin_areas_list.html')

def admin_area_ajax_page_ajax(request):
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
        search = f'AND (area_code LIKE "%{search_value}%" OR area_name LIKE "%{search_value}%" OR location_name LIKE "%{search_value}%")'
    # First SQL query to get the count of appointments

    sql_query = f"""
            SELECT COUNT(*) AS area_count
            FROM {database_name}.areas
            INNER JOIN {database_name}.location ON {database_name}.areas.location_id = {database_name}.location.id
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
        select {database_name}.areas.*,{database_name}.location.location_name
        from  {database_name}.areas
        inner join {database_name}.location on {database_name}.areas.location_id = {database_name}.location.id
        where 1=1 {search}
    	ORDER BY
    		areas.id DESC 
        LIMIT {length} OFFSET {start};
    """

    # Execute the second SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]
    return JsonResponse({"recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, 'data': all_coupon_dtl})


def admin_area_delete(request,id):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    all_areas = get_object_or_404(areas,id=id)
    all_areas.delete()
    data = {
        'status': 1,
        'message': f'Areas Deleted Successfully.',
    }
    messages.success(request, f"successfully Areas Deleted!", extra_tags="success")
    return JsonResponse(data)


def admin_area_edit(request, id):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')

    user_data = constants.get('admin_data', {})
    user_id = user_data.get('id')
    all_areas= get_object_or_404(areas, id=id)
    all_location = location.objects.all()

    # state = states.objects.filter(id=all_location.state_id).first()
    # citie = cities.objects.filter(id=all_location.city_id).first()
    if request.method == "POST":
        all_areas.area_code = request.POST['area_code']
        all_areas.area_name = request.POST['area_name']
        all_areas.location_id = request.POST['location_id']
        all_areas.created_at = date_time()
        all_areas.save()
        messages.success(request, "Areas successfully updated.", extra_tags="success")
        return redirect('admin_area')
    return render(request, 'dashboard/admin_dashboard/admin_areas/admin_areas_edit.html', {
        'all_areas': all_areas,
        'location': all_location,
    })


