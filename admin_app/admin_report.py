from django.shortcuts import render,HttpResponse,redirect
import json
from django.conf import settings
# Create your views here.
# Create your views here.
from django.contrib import messages
from visitors_app.models import user,roles,countries,states,cities,location,company,department,areas
from django.contrib.auth.hashers import check_password,make_password
from visitors_app.context_processors import my_constants
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from visitors_app.views import date_time
from django.core.files.images import get_image_dimensions
from django.db import connection
from visitors_app.views import generate_vms_string
from datetime import datetime

def admin_report(request):
    constants = my_constants(request)
    database_name = constants['database_name']
    user_id = constants['admin_data']['id']
    username = request.session.get('admin')
    
    if not username:
        return redirect('admin')
    
    if request.method == 'POST':
        # date_1 = request.POST.get('date')
        date_1 = request.POST.get('date')

        department_id = request.POST.get('department')
        visitor_type = request.POST.get('visitor_type')

        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')

        search = ''
        search_args = []
        if search_value:
            search = '''
                AND (
                    v.first_name LIKE %s OR 
                    v.last_name LIKE %s OR 
                    v.email LIKE %s OR
                    v.uni_id LIKE %s OR
                    v.mobile LIKE %s OR
                    a.visitors_type LIKE %s OR
                    e.first_name LIKE %s
                )
            '''
            search_args.extend([f'%{search_value}%'] * 7)

        # Adding filters for date, department, and visitor type
        date_filter = ''
        department_filter = ''
        visitor_type_filter = ''
        filter_args = []
        
        if date_1:
            start_date_str, end_date_str = date_1.split(" - ")

            date_format = "%m/%d/%Y"

            # Parse the start and end dates
            start_date = datetime.strptime(start_date_str, date_format)
            end_date = datetime.strptime(end_date_str, date_format)

            # Define the desired output format
            output_format = "%y-%m-%d"

            # Convert the dates to the desired format
            start_date_formatted = start_date.strftime(output_format)
            end_date_formatted = end_date.strftime(output_format)

            # Print the results
 
            # date_2 = date_1.split('-')[0]
            # date_year = date_2.split('20')[1]

            # date_parts = date_1.split('-')
            # date = f"{date_year}-{date_parts[1]}-{date_parts[2]}"

            # date_filter = 'AND a.created_at LIKE %s'
            # filter_args.append(f"%{date}%")
            start_date_formatt = f"{start_date_formatted} 00:00:00"

            end_date_formatt= f"{end_date_formatted} 23:59:59"

            
            date_filter = 'AND a.created_at >= %s AND a.created_at <= %s'
            filter_args.extend([start_date_formatt, end_date_formatt])
            
            
            
        
        if department_id:
            department_filter = 'AND v.department_id = %s'
            filter_args.append(department_id)

        if visitor_type:
            visitor_type_filter = 'AND a.visitors_type = %s'
            filter_args.append(visitor_type)

        if date_1 != '' or department_id != ''  or visitor_type != '':

        # First SQL query to get the count of appointments
            sql_query_count = f"""
                SELECT
                    COUNT(*)
                FROM
                    {database_name}.appointment AS a
                INNER JOIN
                    {database_name}.users AS v
                ON
                    v.id = a.visitors_id
                INNER JOIN
                    {database_name}.users AS e
                ON
                    e.id = a.employee_id
                INNER JOIN
                    {database_name}.department AS d  
                ON
                    d.id = v.department_id  
                    
                INNER JOIN
                    {database_name}.location AS l 
                ON
                    l.id = v.location_id 
                
                INNER JOIN
                    {database_name}.company AS c 
                ON
                    c.id = v.company_id 
                WHERE
                    1=1
                    {date_filter}
                    {department_filter}
                    {visitor_type_filter}
                    {search}
            """
            count_params = filter_args + search_args
            with connection.cursor() as cursor:
                cursor.execute(sql_query_count, count_params)
                recordsTotal = cursor.fetchone()[0]
            # Second SQL query to get detailed user data
            
            sql_query_data = f"""
                SELECT 
                    a.*, 
                    v.first_name AS visitors_first_name,
                    v.last_name AS visitors_last_name,
                    v.uni_id AS visitors_uni_id,
                    e.first_name AS employee_first_name,
                    v.email AS visitors_email,
                    v.mobile AS visitors_mobile,
                    v.image AS visitors_image,
                    d.department_name AS department_name,  
                    l.location_name AS location_name,
                    c.company_name AS company_name
                FROM 
                    {database_name}.appointment AS a
                INNER JOIN 
                    {database_name}.users AS v
                ON 
                    v.id = a.visitors_id
                INNER JOIN
                    {database_name}.users AS e
                ON
                    e.id = a.employee_id
                INNER JOIN
                    {database_name}.department AS d  
                ON
                    d.id = v.department_id  
                    
                INNER JOIN
                    {database_name}.location AS l 
                ON
                    l.id = v.location_id 
                
                INNER JOIN
                    {database_name}.company AS c 
                ON
                    c.id = v.company_id  
                WHERE 
                    1=1
                    {date_filter}
                    {department_filter}
                    {visitor_type_filter}
                    {search}
                ORDER BY
                    a.id DESC
                LIMIT %s OFFSET %s
            """
            data_params = filter_args + search_args + [length, start]
            with connection.cursor() as cursor:
                cursor.execute(sql_query_data, data_params)
                database_all_data = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                all_user_dtl = [dict(zip(columns, row)) for row in database_all_data]

            return JsonResponse({
                "recordsTotal": recordsTotal,
                "recordsFiltered": recordsTotal,
                'data': all_user_dtl
            })
        else:
            return JsonResponse({
                "recordsTotal": 0,
                "recordsFiltered": 0,
                'data': []
            })
    departments = department.objects.all()
    return render(request, 'dashboard/admin_dashboard/admin_report/admin_report.html', {'departments': departments})
        
    
    
    # constants = my_constants(request)
    # database_name = constants['database_name']
    # user_id = constants['admin_data']['id']
    # username = request.session.get('admin')
    
    # if not username:
    #     return redirect('admin')
    
    # if request.method == 'POST':
    #     date_1 = request.POST.get('date')
    #     print('date_1:-',date_1)
    #     department_id = request.POST.get('department')
    #     visitor_type = request.POST.get('visitor_type')
    #     start = int(request.POST.get('start', 0))
    #     length = int(request.POST.get('length', 10))
    #     search_value = request.POST.get('search[value]', '')

    #     search = ''
    #     search_args = []
    #     if search_value:
    #         search = '''
    #             AND (
    #                 v.first_name LIKE %s OR 
    #                 v.email LIKE %s OR 
    #                 a.id LIKE %s OR 
    #                 a.created_at LIKE %s OR 
    #                 a.purpose LIKE %s
    #             )
    #         '''
    #         search_args.extend([f'%{search_value}%'] * 5)

    #     # Adding filters for date, department, and visitor type
    #     date_filter = ''
    #     department_filter = ''
    #     visitor_type_filter = ''
    #     filter_args = []
        
    #     if date_1:
    #         try:
    #             start_date_str, end_date_str = date_1.split(' - ')
    #             print('start_date_str, end_date_str :-',start_date_str, end_date_str )
    #             # start_date = datetime.strptime(start_date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
    #             # end_date = datetime.strptime(end_date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
                
    #             date_filter = 'AND a.created_at BETWEEN %s AND %s'
    #             filter_args.extend([start_date, end_date])
    #         except ValueError:
    #             print('Error parsing date range')

    #     if department_id:
    #         department_filter = 'AND v.department_id = %s'
    #         filter_args.append(department_id)

    #     if visitor_type:
    #         visitor_type_filter = 'AND a.visitors_type = %s'
    #         filter_args.append(visitor_type)

    #     if date_1 or department_id or visitor_type:
    #         sql_query_count = f"""
    #             SELECT
    #                 COUNT(*)
    #             FROM
    #                 {database_name}.appointment AS a
    #             INNER JOIN
    #                 {database_name}.users AS v
    #             ON
    #                 v.id = a.visitors_id
    #             INNER JOIN
    #                 {database_name}.users AS e
    #             ON
    #                 e.id = a.employee_id
    #             INNER JOIN
    #                 {database_name}.department AS d  
    #             ON
    #                 d.id = v.department_id  
    #             INNER JOIN
    #                 {database_name}.location AS l 
    #             ON
    #                 l.id = v.location_id 
    #             INNER JOIN
    #                 {database_name}.company AS c 
    #             ON
    #                 c.id = v.company_id 
    #             WHERE
    #                 1=1 
    #                 {date_filter} 
    #                 {department_filter} 
    #                 {visitor_type_filter}
    #         """
    #         sql_query_data = f"""
    #             SELECT
    #                 a.id,
    #                 v.first_name AS visitors_first_name,
    #                 v.last_name AS visitors_last_name,
    #                 v.uni_id AS visitors_uni_id,
    #                 v.image AS visitors_image,
    #                 e.first_name AS employee_first_name,
    #                 v.email AS visitors_email,
    #                 c.company_name,
    #                 d.department_name,
    #                 l.location_name,
    #                 a.check_in_time
    #             FROM
    #                 {database_name}.appointment AS a
    #             INNER JOIN
    #                 {database_name}.users AS v
    #             ON
    #                 v.id = a.visitors_id
    #             INNER JOIN
    #                 {database_name}.users AS e
    #             ON
    #                 e.id = a.employee_id
    #             INNER JOIN
    #                 {database_name}.department AS d  
    #             ON
    #                 d.id = v.department_id  
    #             INNER JOIN
    #                 {database_name}.location AS l 
    #             ON
    #                 l.id = v.location_id 
    #             INNER JOIN
    #                 {database_name}.company AS c 
    #             ON
    #                 c.id = v.company_id 
    #             WHERE
    #                 1=1 
    #                 {date_filter} 
    #                 {department_filter} 
    #                 {visitor_type_filter}
    #             ORDER BY
    #                 a.id DESC
    #             LIMIT %s OFFSET %s
    #         """
    #         filter_args.extend([length, start])
        
    #     else:
    #         sql_query_count = f"""
    #             SELECT
    #                 COUNT(*)
    #             FROM
    #                 {database_name}.appointment AS a
    #             INNER JOIN
    #                 {database_name}.users AS v
    #             ON
    #                 v.id = a.visitors_id
    #             INNER JOIN
    #                 {database_name}.users AS e
    #             ON
    #                 e.id = a.employee_id
    #             INNER JOIN
    #                 {database_name}.department AS d  
    #             ON
    #                 d.id = v.department_id  
    #             INNER JOIN
    #                 {database_name}.location AS l 
    #             ON
    #                 l.id = v.location_id 
    #             INNER JOIN
    #                 {database_name}.company AS c 
    #             ON
    #                 c.id = v.company_id 
    #             WHERE
    #                 1=1
    #         """
    #         sql_query_data = f"""
    #             SELECT
    #                 a.id,
    #                 v.first_name AS visitors_first_name,
    #                 v.last_name AS visitors_last_name,
    #                 v.uni_id AS visitors_uni_id,
    #                 v.image AS visitors_image,
    #                 e.first_name AS employee_first_name,
    #                 v.email AS visitors_email,
    #                 c.company_name,
    #                 d.department_name,
    #                 l.location_name,
    #                 a.check_in_time
    #             FROM
    #                 {database_name}.appointment AS a
    #             INNER JOIN
    #                 {database_name}.users AS v
    #             ON
    #                 v.id = a.visitors_id
    #             INNER JOIN
    #                 {database_name}.users AS e
    #             ON
    #                 e.id = a.employee_id
    #             INNER JOIN
    #                 {database_name}.department AS d  
    #             ON
    #                 d.id = v.department_id  
    #             INNER JOIN
    #                 {database_name}.location AS l 
    #             ON
    #                 l.id = v.location_id 
    #             INNER JOIN
    #                 {database_name}.company AS c 
    #             ON
    #                 c.id = v.company_id 
    #             WHERE
    #                 1=1
    #             ORDER BY
    #                 a.id DESC
    #             LIMIT %s OFFSET %s
    #         """
    #         filter_args.extend([length, start])

    #     # Debugging SQL Queries
    #     print('SQL Query Count:', sql_query_count % tuple(filter_args))
    #     print('SQL Query Data:', sql_query_data % tuple(filter_args))
        
    #     with connection.cursor() as cursor:
    #         cursor.execute(sql_query_count, filter_args)
    #         records_total = cursor.fetchone()[0]

    #         cursor.execute(sql_query_data, filter_args)
    #         records = cursor.fetchall()

    #     data = []
    #     for record in records:
    #         data.append({
    #             'id': record[0],
    #             'visitors_first_name': record[1],
    #             'visitors_last_name': record[2],
    #             'visitors_uni_id': record[3],
    #             'visitors_image': record[4],
    #             'employee_first_name': record[5],
    #             'visitors_email': record[6],
    #             'company_name': record[7],
    #             'department_name': record[8],
    #             'location_name': record[9],
    #             'check_in_time': record[10]
    #         })

    #     response = {
    #         # 'draw': int(request.POST.get('draw', 1)),
    #         'recordsTotal': records_total,
    #         'recordsFiltered': records_total,
    #         'data': data
    #     }

    #     return JsonResponse(response)
    # departments = department.objects.all()
    # return render(request, 'dashboard/admin_dashboard/admin_report/admin_report.html', {'departments': departments})
    # return render(request,'admin_report.html')