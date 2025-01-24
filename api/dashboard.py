from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password,make_password
from visitors_app.models import user,roles,countries,states,cities,location,areas,appointment
from visitors_app.context_processors import my_constants
import os
from django.conf import settings
from django.core.files.storage import default_storage
from visitors_app.views import date_time
from django.db import connection 
from django.core.mail import send_mail
from django.db import connection, IntegrityError, DatabaseError

from visitors_app.context_processors import my_constants
import random
import string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import datetime
# class dashboard(APIView):
#     def post(self, request):        
#         constants = my_constants(request)        
#         database_name = constants['database_name']
#         employee_id = request.data.get('employee_id', '')
#         year = datetime.datetime.now().strftime("%Y")[:2]
#         today_date = date_time().split(' ')[0]
#         total_visitors_date = f'{year}{today_date}'
#         sql_query_check_in_count = """
#         SELECT COUNT(*) AS total_count
#         FROM {database_name}.appointment
#         WHERE date = %s AND check_in_time IS NOT NULL AND check_in_time != '' AND check_out_time = '';
#         """.format(database_name=f'{database_name}')

#         sql_query_check_out_count = """
#             SELECT COUNT(*) AS total_count
#             FROM {database_name}.appointment
#             WHERE date = %s AND check_out_time IS NOT NULL AND check_out_time != '';
#         """.format(database_name=f'{database_name}')

#         sql_query_total_visitors = """
#             SELECT COUNT(*) AS total_count
#             FROM {database_name}.appointment
#             WHERE date = %s;
#         """.format(database_name=f'{database_name}')

#         sql_query_pending = """
#             SELECT COUNT(*) AS total_count
#             FROM {database_name}.appointment
#             WHERE date = %s AND check_in_time = '' AND check_out_time = '';
#         """.format(database_name=f'{database_name}')

#         with connection.cursor() as cursor:
#             cursor.execute(sql_query_check_in_count, [total_visitors_date])
#             check_in_count = cursor.fetchone()[0]

#             cursor.execute(sql_query_check_out_count, [total_visitors_date])
#             check_out_count = cursor.fetchone()[0]

#             cursor.execute(sql_query_total_visitors, [total_visitors_date])
#             total_visitors_count = cursor.fetchone()[0]

#             cursor.execute(sql_query_pending, [total_visitors_date])
#             pending_count = cursor.fetchone()[0]

#         # Return JSON response
#         return Response({
#             'pending_count':pending_count,
#             'check_in_count': check_in_count,
#             'check_out_count': check_out_count,
#             'total_visitors_count': total_visitors_count
            
#         })



class dashboard(APIView):
    def post(self, request):        
        constants = my_constants(request)        
        database_name = constants['database_name']
        employee_id = request.data.get('employee_id', '')
        year = datetime.datetime.now().strftime("%Y")[:2]
        today_date = date_time().split(' ')[0]
        total_visitors_date = f'{year}{today_date}'      
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
        
        WHERE date = %s AND check_in_time IS NOT NULL AND check_in_time != '' AND check_out_time = '' AND employee_id = %s; 
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
            WHERE date = %s AND check_out_time IS NOT NULL AND check_out_time != '' AND employee_id = %s;
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
            WHERE date = %s AND employee_id = %s;
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
                date = %s AND check_in_time = '' AND check_out_time = '' AND employee_id = %s;
        
        """
        
        with connection.cursor() as cursor:
            cursor.execute(sql_query_check_in_count, [total_visitors_date,employee_id])
            check_in_data = cursor.fetchone()
            check_in_count = check_in_data[0] if check_in_data else 0
            
            cursor.execute(sql_query_check_out_count, [total_visitors_date,employee_id])
            check_out_data = cursor.fetchone()
            check_out_count = check_out_data[0] if check_out_data else 0

            cursor.execute(sql_query_total_visitors, [total_visitors_date,employee_id])
            total_visitors_data = cursor.fetchone()
            total_visitors_count = total_visitors_data[0] if total_visitors_data else 0

            cursor.execute(sql_query_pending, [total_visitors_date,employee_id])
            pending_data = cursor.fetchone()
            pending_count = pending_data[0] if pending_data else 0
        base_url = request.build_absolute_uri('/')[:-1]
        context = [
            {"name": "Today Appointment", "number": total_visitors_count,"image":f"{base_url}/images/calendardash.png"},
            {"name": "Today Pending", "number": pending_count,"image":f"{base_url}/images/pendingdash.png","title": "pending"},
            {"name": "Total Check In", "number": check_in_count,"image":f"{base_url}/images/signindash.png","title": "check in"},
            {"name": "Total Check Out", "number": check_out_count,"image":f"{base_url}/images/signoutdash.png","title": "check out"},
        ]
        return Response({
            "status": "true",
            "data": context
        })
    
    
# class dashboard_pending(APIView):
#     def post(self, request):
#         constants = my_constants(request)
#         database_name = constants['database_name']
#         year = datetime.datetime.now().strftime("%Y")[:2]
#         today_date = date_time().split(' ')[0]
#         # total_visitors_date = f'{year}{today_date}'
#         total_visitors_date = '2024-09-30'
#         employee_id = request.data.get('employee_id', '')
#         total = request.data.get('total_request', '')
#         page = request.data.get('page_no', 1)
#         page_size = 15
#         offset = (int(page) - 1) * page_size

#         # Base SQL query
#         base_query = f"""
#             SELECT 
#                 appointment.*, 
#                 visitors.first_name AS visitors_name, 
#                 visitors.last_name AS visitors_last_name, 
#                 visitors.uni_id AS visitors_uni_id,
#                 visitors.image AS visitors_image,
#                 visitors.email AS visitors_email,
#                 visitors.mobile AS visitors_mobile,
#                 employees.first_name AS employee_name,
#                 employees.last_name AS employee_last_name,
#                 employees.uni_id AS employee_uni_id,
#                 appointment.check_in_time AS start_time,
#                 appointment.check_out_time AS stop_time,
#                 created_by.first_name AS created_by_first_name,
#                 created_by.last_name AS created_by_last_name
#             FROM 
#                 {database_name}.appointment
#             INNER JOIN 
#                 {database_name}.users AS visitors ON visitors.id = appointment.visitors_id
#             INNER JOIN 
#                 {database_name}.users AS employees ON employees.id = appointment.employee_id
#             INNER JOIN 
#                 {database_name}.users AS created_by ON created_by.id = appointment.created_by
#             WHERE
#                 date = %s AND employee_id = %s
#         """
#         if total == 'pending':
#             condition = "AND check_in_time = '' AND check_out_time = ''"
#         elif total == 'check in':
#             condition = "AND check_out_time IS NOT NULL AND check_out_time != '' AND check_out_time = ''"
#         elif total == 'check out':
#             condition = "AND check_in_time IS NOT NULL AND check_in_time != '' AND check_out_time = ''"
#         else:
#             return Response({"status": "false", "message": "Invalid request value"})

#         # Add condition, ordering, limit, and offset
#         sql_query = f"{base_query} {condition} ORDER BY visitors.id DESC LIMIT %s OFFSET %s;"

#         with connection.cursor() as cursor:
#             cursor.execute(sql_query, [total_visitors_date, employee_id, page_size, offset])
#             database_all_data = cursor.fetchall()
#             columns = [col[0] for col in cursor.description]
#             result_list = [dict(zip(columns, row)) for row in database_all_data]

#         return Response({"status": "true", "data": result_list})



class dashboard_pending(APIView):
    
    def post(self, request):
        
        constants = my_constants(request)
        database_name = constants['database_name']
        base_image_url = constants['IMAGEPATH']
        placeholder_image_url = constants['DEFAULT_IMAGE']

        year = datetime.datetime.now().strftime("%Y")[:2]
        today_date = date_time().split(' ')[0]
        total_visitors_date = f'{year}{today_date}'
        employee_id = request.data.get('employee_id', '')
        total = request.data.get('total_request', '')
        page = request.data.get('page_no', '')
        
        if employee_id == '' and total == '':
            return Response({
                "status": "false",
                "message": "All fields are required",
            })
        
        page_size = 15
        offset = (int(page) - 1) * page_size

        # Base SQL query for fetching records
        base_query = f"""
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
                date = %s AND employee_id = %s
        """

    
        if total == 'pending':
            condition = "AND check_in_time = '' AND check_out_time = ''"
        elif total == 'check in':
            condition = "AND check_in_time IS NOT NULL AND check_in_time != '' AND check_out_time = ''"
        elif total == 'check out':
            condition = "AND check_in_time IS NOT NULL AND check_in_time != '' AND check_out_time IS NOT NULL"
        else:
            return Response({"status": "false", "message": "Invalid request value"})

        # Complete SQL query with condition, ordering, limit, and offset
        sql_query = f"{base_query} {condition} ORDER BY visitors.id DESC LIMIT %s OFFSET %s;"

        # Query to get the total number of records (without LIMIT and OFFSET)
        count_query = f"SELECT COUNT(*) FROM {database_name}.appointment WHERE date = %s AND employee_id = %s {condition};"

        with connection.cursor() as cursor:
            # Execute count query to get the total record count
            cursor.execute(count_query, [total_visitors_date, employee_id])
            total_records = cursor.fetchone()[0] 

            # Calculate total number of pages
            total_pages = (total_records + page_size - 1) // page_size

            # Check if the requested page is valid
            if int(page) > total_pages:
                return Response({
                    "status": "false",
                    "message": "No more records available",
                    "data": [],
                    "pagination": {
                        "current_page": page,
                        "page_size": page_size,
                        "total_records": total_records,
                        "total_pages": total_pages
                    }
                })

            # Execute the main query with pagination
            cursor.execute(sql_query, [total_visitors_date, employee_id, page_size, offset])
            database_all_data = cursor.fetchall()
            # columns = [col[0] for col in cursor.description]
            # result_list = [dict(zip(columns, row)) for row in database_all_data]
            columns = [col[0] for col in cursor.description]
            all_visitor_data = []

            # Append base_image_url to the image field
            for row in database_all_data:
                visitor_data = dict(zip(columns, row))
                
                # Update image URL if image is present, otherwise use placeholder
                if visitor_data.get('image'):  
                    visitor_data['visitors_image'] = f"{base_image_url}{visitor_data['image']}"
                else:  
                    visitor_data['visitors_image'] = placeholder_image_url
                
                all_visitor_data.append(visitor_data)

        return Response({
            "status": "true",
            "data": all_visitor_data,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,

            }
        })
