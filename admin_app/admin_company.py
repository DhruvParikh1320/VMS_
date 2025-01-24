from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
# Create your views here.
# Create your views here.
from django.contrib import messages
from visitors_app.models import user,roles,countries,states,cities,location,company
from django.contrib.auth.hashers import check_password
from visitors_app.context_processors import my_constants
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from visitors_app.views import date_time
from django.db import connection



def admin_company_add(request):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    locationes = location.objects.filter(status=1)
    if request.method == 'POST':
        company_code = request.POST['company_code']
        company_name = request.POST['company_name']
        location_id = request.POST['location_id']
        address_1 = request.POST['address_1']
        address_2 = request.POST['address_2']
        pincode = request.POST['pincode']
        status =request.POST['status']
        created_at = date_time()
        companyes = company(company_code=company_code, company_name=company_name, location_id=location_id,address_1=address_1,address_2=address_2,status=status,pincode=pincode,created_at=created_at)
        companyes.save()
        messages.success(request, "Company successfully created.", extra_tags="success")
        return redirect('admin_company')
    return render(request, 'dashboard/admin_dashboard/admin_company/admin_company_add.html',{'locationes':locationes})

def admin_company(request):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    return render(request, 'dashboard/admin_dashboard/admin_company/admin_company.html')


def admin_company_ajax_page_ajax(request):
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
        search = f'AND ( company_code LIKE "%{search_value}%" OR company_name LIKE "%{search_value}%" OR location_name LIKE "%{search_value}%"  OR address_1 LIKE "%{search_value}%" OR address_2 LIKE "%{search_value}%" OR pincode LIKE "%{search_value}%")'
    # First SQL query to get the count of appointments

    sql_query = f"""
            SELECT COUNT(*) AS company_count
            FROM {database_name}.company
            INNER JOIN {database_name}.location ON {database_name}.company.location_id = {database_name}.location.id
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
        select {database_name}.company.*,{database_name}.location.location_name
        from  {database_name}.company
        inner join {database_name}.location on {database_name}.company.location_id = {database_name}.location.id
        where 1=1 {search}
    	ORDER BY
    		company.id DESC 
        LIMIT {length} OFFSET {start};
    """

    # Execute the second SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]
    return JsonResponse({"recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, 'data': all_coupon_dtl})


def admin_company_delete(request,id):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    all_company = get_object_or_404(company,id=id)
    all_company.delete()
    data = {
        'status': 1,
        'message': f'Company Deleted Successfully.',
    }
    messages.success(request, f"successfully Company Deleted!", extra_tags="success")
    return JsonResponse(data)

def admin_company_edit(request, id):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')

    user_data = constants.get('user_data', {})
    user_id = user_data.get('id')
    all_company= get_object_or_404(company, id=id)
    all_location = location.objects.filter(status=1)

    # state = states.objects.filter(id=all_location.state_id).first()
    # citie = cities.objects.filter(id=all_location.city_id).first()
    if request.method == "POST":
        all_company.company_code = request.POST['company_code']
        all_company.company_name = request.POST['company_name']
        all_company.location_id = request.POST['location_id']
        all_company.address_1 = request.POST['address_1']
        all_company.address_2 = request.POST['address_2']
        all_company.pincode = request.POST['pincode']
        all_company.status = request.POST['status']
        all_company.created_at = date_time()
        all_company.save()
        messages.success(request, "Company successfully updated.", extra_tags="success")
        return redirect('admin_company')
    return render(request, 'dashboard/admin_dashboard/admin_company/all_company_edit.html', {
        'all_company': all_company,
        'location': all_location,
    })