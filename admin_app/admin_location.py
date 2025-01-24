from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
# Create your views here.
# Create your views here.
from django.contrib import messages
from visitors_app.models import user,roles,countries,states,cities,location
from django.contrib.auth.hashers import check_password
from visitors_app.context_processors import my_constants
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from visitors_app.views import date_time
from django.db import connection


def admin_location_add(request):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    countrie = countries.objects.all()
    if request.method == 'POST':
        country_id = request.POST['country_id']
        state_id = request.POST['state_id']
        city_id = request.POST['city_id']
        location_name = request.POST['location_name']
        status =request.POST['status']
        created_at = date_time()
        locationes = location(country_id=country_id, state_id=state_id, city_id=city_id,location_name=location_name,status=status,created_at=created_at)
        locationes.save()
        messages.success(request, "location successfully updated.", extra_tags="success")
        return redirect('admin_location')
    return render(request, 'dashboard/admin_dashboard/admin_location/admin_location_add.html', {'countrie':countrie})


def admin_location_ajax_load_states(request):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    country_id = request.GET.get('country_id')

    state = states.objects.filter(country_id=country_id).all()

    return JsonResponse(list(state.values('id', 'name')), safe=False)


def admin_location_ajax_load_cities(request):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    state_id = request.GET.get('state_id')
    city = cities.objects.filter(state_id=state_id).all()
    return JsonResponse(list(city.values('id', 'name')), safe=False)


def admin_location(request):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    
    return render(request, 'dashboard/admin_dashboard/admin_location/admin_location_list.html')

def admin_location_ajax_page_ajax(request):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    
    database_name = constants['database_name']
    user_data = constants.get('user_data', {})
    user_id = user_data.get('id')
    start = int(request.POST.get('start', 0))
    length = int(request.POST.get('length', 10))
    search_value = request.POST.get('search[value]', '')

    search = ''
    search_params = []

    if search_value:
        search = f"AND (countries.name LIKE %s OR states.name LIKE %s OR cities.name LIKE %s OR location.location_name LIKE %s)"
        search_params = [f"%{search_value}%"] * 4

    # First SQL query to get the count of records
    count_query = f"""
        SELECT
            COUNT(*) AS appointment_count
        FROM
            {database_name}.location
        INNER JOIN
            {database_name}.countries AS countries ON countries.id = location.country_id
        INNER JOIN
            {database_name}.states AS states ON states.id = location.state_id
        INNER JOIN
            {database_name}.cities AS cities ON cities.id = location.city_id
        WHERE
            1 = 1 {search};
    """
    
    with connection.cursor() as cursor:
        cursor.execute(count_query, search_params)
        database_all_data = cursor.fetchone()
    
    recordsTotal = database_all_data[0] if database_all_data else 0

    # Second SQL query to get detailed records
    data_query = f"""
        SELECT
            location.*,
            countries.name AS countries_name,
            states.name AS states_name,
            cities.name AS cities_name
        FROM
            {database_name}.location
        INNER JOIN
            {database_name}.countries AS countries ON countries.id = location.country_id
        INNER JOIN
            {database_name}.states AS states ON states.id = location.state_id
        INNER JOIN
            {database_name}.cities AS cities ON cities.id = location.city_id
        WHERE
            1 = 1 {search}
        ORDER BY
            location.id DESC
        LIMIT %s OFFSET %s;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(data_query, search_params + [length, start])
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]
    
    return JsonResponse({"recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, 'data': all_coupon_dtl})
    
    
    
def admin_location_delete(request,id):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    all_location = get_object_or_404(location,id=id)
    all_location.delete()
    data = {
        'status': 1,
        'message': f'Location Deleted Successfully.',
    }
    messages.success(request, f"successfully Location Deleted!", extra_tags="success")
    return JsonResponse(data)


def admin_location_edit(request,id):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username :
        return redirect('admin')

    user_data = constants.get('admin_data', {})
    user_id = user_data.get('id')
    all_location = get_object_or_404(location,id=id)
    all_country = countries.objects.all()
    state = states.objects.filter(id=all_location.state_id).first()
    citie = cities.objects.filter(id=all_location.city_id).first()
    if request.method == "POST":
        all_location.country_id = request.POST['country_id']
        all_location.state_id = request.POST['state_id']
        all_location.city_id = request.POST['city_id']
        all_location.location_name = request.POST['location_name']
        all_location.status = request.POST['status']
        all_location.created_at = date_time()
        all_location.save()
        messages.success(request, "Location successfully updated.", extra_tags="success")
        return redirect('admin_location')
    return render(request, 'dashboard/admin_dashboard/admin_location/admin_location_edit.html', {
        'all_location': all_location,
        'all_country': all_country,
        'state': state,
        'cities': citie,
        
    })