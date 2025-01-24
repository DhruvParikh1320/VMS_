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
# class visitore_listingView(APIView):
#     def post(self, request):        
#         constants = my_constants(request)
#         employee_id = request.data.get('employee_id', '')
#         page = request.data.get('page', 1)  # Default to page 1 if not provided
#         type = request.data.get('type', '')
#         page = int(page)

        
#         database_name = constants['database_name']
#         if not employee_id:
#             return Response({"status": "false", "message": "Employee ID is required."})

#         # Define the number of results per page
#         results_per_page = 10

#         base_image_url = constants['IMAGEPATH']
#         # Define a placeholder image URL
#         placeholder_image_url = constants['DEFAULT_IMAGE']
#         # Calculate the offset for the SQL query
#         offset = (page - 1) * results_per_page

#         with connection.cursor() as cursor:
#             # Construct the base query
#             base_query = f"""
#                 SELECT 
#                     {database_name}.appointment.*, 
#                     {database_name}.users.first_name as visitors_first_name,
#                     {database_name}.users.email as visitors_email,
#                     {database_name}.users.mobile as visitors_mobile,
#                     {database_name}.users.image as visitors_image
#                 FROM 
#                     {database_name}.appointment
#                 INNER JOIN 
#                     {database_name}.users 
#                 ON 
#                     {database_name}.users.id = {database_name}.appointment.visitors_id 
#                 WHERE 
                    
#                     {database_name}.appointment.employee_id = %s 
#             """

#             # Handle different values for `type`
#             if type == 'all':
#                 count_query = f"""
#                     SELECT COUNT(*) 
#                     FROM 
#                         {database_name}.appointment 
#                     WHERE 
#                         employee_id = %s
#                         AND status != 'pending' 
                        
#                 """
#                 query = base_query + f"""
#                     AND {database_name}.appointment.status != 'pending'
#                     ORDER BY {database_name}.appointment.id DESC
#                     LIMIT %s OFFSET %s
#                 """
#                 params = [employee_id, results_per_page, offset]
#             elif type == 'pending':
#                 count_query = f"""
#                     SELECT
#                         COUNT(*)
#                     FROM
#                         {database_name}.appointment
#                     INNER JOIN
#                         {database_name}.users
#                     ON
#                         {database_name}.users.id = {database_name}.appointment.visitors_id
#                     WHERE
#                         {database_name}.appointment.employee_id = %s 
#                         AND {database_name}.appointment.status = 'pending'; 
#                 """

#                 query = base_query + f"""
#                     AND {database_name}.appointment.status = 'pending'
#                     LIMIT %s OFFSET %s
#                 """
#                 params = [employee_id, results_per_page, offset]
#             else:
#                 # Handle invalid `type` values
#                 return Response({"status": "false", "message": "Invalid type value. Allowed values are 'all' or 'pending'."})

#             try:
#                 # Execute the count query
#                 cursor.execute(count_query, [employee_id])
#                 total_items_result = cursor.fetchone()

#                 if total_items_result is None:
#                     total_items = 0
#                 else:
#                     total_items = total_items_result[0]

#                 # Calculate total pages
#                 total_pages = total_items // results_per_page
#                 if total_items % results_per_page != 0:
#                     total_pages += 1

#                 # Execute the main query with pagination
#                 cursor.execute(query, params)
#                 columns = [col[0] for col in cursor.description]
#                 results = [
#                     dict(zip(columns, row))
#                     for row in cursor.fetchall()
#                 ]
#                 for result in results:
#                     if 'visitors_image' in result and result['visitors_image']:
#                         # If the image URL is not empty or invalid, prepend the base URL
#                         result['visitors_image'] = base_image_url + result['visitors_image']
#                     else:
#                         # Use the placeholder image URL if no image is provided
#                         result['visitors_image'] = placeholder_image_url
#             except Exception as e:
#                 print(f"Error: {e}")
#                 return Response({"status": "false", "message": "An error occurred."})

#         pagination = {
#             'current_page': page,
#             'per_page_count': results_per_page,
#             'total': total_items,
#             'last_page': total_pages
#         }

#         if results:
#             return Response({
#                 "status": "true",
#                 "data": results,
#                 "pagination": pagination,
#             })
#         else:
#             # If no results are found, set total_items to 0 in the response
#             pagination['total'] = 0
#             return Response({
#                 "status": "false",
#                 "message": "No data found.",
#                 "data": results,
#                 "pagination": pagination,
#             })


class visitore_listingView(APIView):
    def post(self, request):
        constants = my_constants(request)
        employee_id = request.data.get('employee_id', '')
        page = request.data.get('page', 1)
        type = request.data.get('type', '')
        search_term = request.data.get('search', '')
        page = int(page)

        database_name = constants['database_name']
        if not employee_id:
            return Response({"status": "false", "message": "Employee ID is required."})

        # Define the number of results per page
        results_per_page = 10

        base_image_url = constants['IMAGEPATH']
        placeholder_image_url = constants['DEFAULT_IMAGE']
        offset = (page - 1) * results_per_page

        with connection.cursor() as cursor:
            # Construct the base query
            base_query = f"""
                SELECT 
                    {database_name}.appointment.*, 
                    {database_name}.users.first_name as visitors_first_name,
                    {database_name}.users.email as visitors_email,
                    {database_name}.users.mobile as visitors_mobile,
                    {database_name}.users.image as visitors_image
                FROM 
                    {database_name}.appointment
                INNER JOIN 
                    {database_name}.users 
                ON 
                    {database_name}.users.id = {database_name}.appointment.visitors_id
                WHERE 
                    {database_name}.appointment.employee_id = %s
            """

            # Prepare the parameters for the main query
            params = [employee_id]

            # Handle search term if provided
            if search_term:
                base_query += " AND ("
                base_query += f"{database_name}.users.first_name LIKE %s OR "
                base_query += f"{database_name}.users.email LIKE %s OR "
                base_query += f"{database_name}.users.mobile LIKE %s OR "  # Fix applied here
                base_query += f"{database_name}.appointment.status LIKE %s"
                base_query += ")"
                params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])

            # Handle different values for `type`
            if type == 'all':
                count_query = f"""
                    SELECT COUNT(*) 
                    FROM 
                        {database_name}.appointment 
                    INNER JOIN 
                        {database_name}.users 
                    ON 
                        {database_name}.users.id = {database_name}.appointment.visitors_id
                    WHERE 
                        {database_name}.appointment.employee_id = %s
                        AND {database_name}.appointment.status != 'pending'
                """
                if search_term:
                    count_query += " AND (users.first_name LIKE %s OR users.email LIKE %s OR users.mobile LIKE %s OR appointment.status LIKE %s)"  # Fix applied here
                
                query = base_query + f"""
                    AND {database_name}.appointment.status != 'pending'
                    ORDER BY {database_name}.appointment.id DESC
                    LIMIT %s OFFSET %s
                """
                params.append(results_per_page)
                params.append(offset)
            elif type == 'pending':
                count_query = f"""
                    SELECT COUNT(*)
                    FROM
                        {database_name}.appointment
                    INNER JOIN
                        {database_name}.users
                    ON
                        {database_name}.users.id = {database_name}.appointment.visitors_id
                    WHERE
                        {database_name}.appointment.employee_id = %s
                        AND {database_name}.appointment.status = 'pending'
                """
                if search_term:
                    count_query += " AND (users.first_name LIKE %s OR users.email LIKE %s OR users.mobile LIKE %s OR appointment.status LIKE %s)"  # Fix applied here
                
                query = base_query + f"""
                    AND {database_name}.appointment.status = 'pending'
                    LIMIT %s OFFSET %s
                """
                params.append(results_per_page)
                params.append(offset)
            else:
                return Response({"status": "false", "message": "Invalid type value. Allowed values are 'all' or 'pending'."})

            try:
                # Execute the count query
                if search_term:
                    cursor.execute(count_query, [employee_id] + [f"%{search_term}%"] * 4)
                else:
                    cursor.execute(count_query, [employee_id])
                    
                total_items_result = cursor.fetchone()
                total_items = total_items_result[0] if total_items_result else 0

                # Calculate total pages
                total_pages = (total_items // results_per_page) + (1 if total_items % results_per_page else 0)

                # Execute the main query with pagination
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                results = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
                for result in results:
                    result['visitors_image'] = (
                        base_image_url + result['visitors_image']
                        if result.get('visitors_image') else placeholder_image_url
                    )

            except Exception as e:
                print(f"Error: {e}")
                return Response({"status": "false", "message": f"An error occurred: {e}"})

        pagination = {
            'current_page': page,
            'per_page_count': results_per_page,
            'total': total_items,
            'last_page': total_pages,
            'search_term': search_term
        }

        if results:
            return Response({
                "status": "true",
                "data": results,
                "pagination": pagination,
            })
        else:
            pagination['total'] = 0
            return Response({
                "status": "false",
                "message": "No data found.",
                "data": results,
                "pagination": pagination,
            })






# class status_changesView(APIView):
#      def post(self, request):
#         constants = my_constants(request) 
#         from_email = constants['From_Email']
#         employee_id = request.data.get('appointment_id', '')

#         status = request.data.get('status', '')

#         reason = request.data.get('reason', '')

#         date = request.data.get('date', '')

#         time = request.data.get('time', '')

#         if not employee_id:
#             return Response({"status": "false", "message": "Employee ID is required."})
#         if status not in ['accepted', 'rejected']:
#             return Response({"status": "false", "message": "Status is required."})
        
#         appointment_exist = appointment.objects.filter(id=employee_id).first()
#         if appointment_exist:
#             if status == 'rejected':
#                 if not reason or not date or not time:
#                     return Response({"status": "false", "message": "Reason, date, and time are required for rejected status."})
#             try:
#                 with connection.cursor() as cursor:
#                     # Update the status in vms.appointment
#                     cursor.execute("""
#                         UPDATE vms.appointment
#                         SET status = %s, updated_at = %s
#                         WHERE id = %s
#                     """, [status,date_time(), employee_id])
                    
#                     # If the status is 'rejected', insert into appointment_reject
#                     if status == 'rejected':
#                         cursor.execute("""
#                             INSERT INTO vms.appointment_reject (appointment_id, reason,date,time,created_at)
#                             VALUES (%s, %s,%s,%s,%s)
#                         """, [employee_id,reason,date,time,date_time()])
                        
#                     cursor.execute("""
#                         SELECT  
#                             vms.appointment.*,
#                             visitors.first_name AS visitors_first_name,                        
#                             visitors.email AS visitors_email,
#                             visitors.mobile AS visitors_mobile,
#                             visitors.image AS visitors_image,
#                             employees.first_name AS employee_first_name,
#                             employees.email AS employees_email,
#                             employees.mobile AS employees_mobile,
#                             employees.image AS employees_image
#                         FROM 
#                             vms.appointment
#                         INNER JOIN 
#                             vms.users AS visitors ON visitors.id = vms.appointment.visitors_id
#                         INNER JOIN 
#                             vms.users AS employees ON employees.id = vms.appointment.employee_id    
#                         WHERE 
#                             vms.appointment.id = %s;
#                         """, [employee_id])
#                     appointment_details = cursor.fetchone()
#                     if appointment_details:
#                         employee_email = appointment_details[14]  # Adjust index based on actual column position

#                         visitor_email = appointment_details[18]
#                         print('visitor_email:-',visitor_email)
#                         if status == 'accepted':
#                             send_mail(
#                                 'Appointment Accepted',
#                                 f'Your appointment has been accepted.',
#                                 'app.hexagon@gmail.com',
#                                 [visitor_email],
#                                 fail_silently=False,
#                             )
#                         elif status == 'rejected':
#                             send_mail(
#                                 'Appointment Rejected',
#                                 f'Your appointment has been rejected. Reason: {reason}.',
#                                 'app.hexagon@gmail.com',
#                                 [visitor_email],
#                                 fail_silently=False,
#                             )
#                     return Response({"status": "true", "message": "Status changed successfully."})
#             except IntegrityError as e:
#                 return Response({"status": "false", "message": f"Database integrity error{e}."})
#         else:
#             return Response({"status": "false", "message": "Appointment not found."})

# def send_status_change_email(subject, context, recipient_email, constants):
#     template_name = 'api_templates/status_change_email.html'
#     message = render_to_string(template_name, context)
#     plain_message = strip_tags(message)
#     from_email = constants['From_Email']
#     mail = EmailMultiAlternatives(subject, plain_message, from_email, [recipient_email])
#     mail.attach_alternative(message, "text/html")
    
#     try:
#         mail.send()
#     except Exception as e:
#         return {"status": "false", "message": f"Error sending email: {e}"}
    
#     return {"status": "true", "message": "Email sent successfully."}
class status_changesView(APIView):
    def post(self, request):
        constants = my_constants(request)
        database_name = constants['database_name']
        from_email = constants['From_Email'] 
         
        employee_id = request.data.get('appointment_id', '')
        status = request.data.get('status', '')
        reason = request.data.get('reason', '')
        date = request.data.get('date', '')
        time = request.data.get('time', '')

        if not employee_id:
            return Response({"status": "false", "message": "Employee ID is required."})
        if status not in ['accepted', 'rejected']:
            return Response({"status": "false", "message": "Status is required."})
        
        appointment_exist = appointment.objects.filter(id=employee_id).first()
        if appointment_exist:
            if status == 'rejected':
                if not reason or not date or not time:
                    return Response({"status": "false", "message": "Reason, date, and time are required for rejected status."})
            try:
                with connection.cursor() as cursor:
                    # Update the status in vms.appointment
                    cursor.execute(f"""
                        UPDATE {database_name}.appointment
                        SET status = %s, employee_approval = %s ,updated_at = %s
                        WHERE id = %s
                    """, [status,status, date_time(), employee_id])
                    
                    # If the status is 'rejected', insert into appointment_reject
                    if status == 'rejected':
                        cursor.execute(f"""
                            INSERT INTO {database_name}.appointment_reject (appointment_id, reason, date, time, created_at)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [employee_id, reason, date, time, date_time()])
                        
                    cursor.execute(f"""
                        SELECT  
                            {database_name}.appointment.*,
                            visitors.first_name AS visitors_first_name,                        
                            visitors.email AS visitors_email,
                            visitors.mobile AS visitors_mobile,
                            visitors.image AS visitors_image,
                            employees.first_name AS employee_first_name,
                            employees.email AS employees_email,
                            employees.mobile AS employees_mobile,
                            employees.image AS employees_image
                        FROM 
                        {database_name}.appointment
                        INNER JOIN 
                        {database_name}.users AS visitors ON visitors.id ={database_name}.appointment.visitors_id
                        INNER JOIN 
                        {database_name}.users AS employees ON employees.id ={database_name}.appointment.employee_id    
                        WHERE 
                        {database_name}.appointment.id = %s;
                    """, [employee_id])
                    
                    # appointment_details = cursor.fetchone()
                    # columns = [col[0] for col in cursor.description]
                    # all_data = [dict(zip(columns, row)) for row in columns]
                    # print('all_data',all_data)
                    
                    database_all_data = cursor.fetchone()
                    columns = [col[0] for col in cursor.description]
                    all_data = dict(zip(columns, database_all_data))
                    
                    if all_data:
                        recipient_email = all_data.get('visitors_email')
                        if recipient_email != '' :
                
                            
                            if status == 'accepted':
                                context = {'status': 'accepted'}
                                subject = 'Appointment Accepted'
                            elif status == 'rejected':
                                context = {'status': 'rejected', 'reason': reason, 'date': date, 'time': time}
                                subject = 'Appointment Rejected'
                            # subject = 'Appointment Rejected'      
                            # # context = {'status': 'rejected', 'reason': reason, 'date': date, 'time': time} 
                            # context = {'status': 'rejected'}
                            template_name = 'api_templates/status_change_email.html'
                            message = render_to_string(template_name, context)
                            plain_message = strip_tags(message)
                            from_email = from_email
                            recipient_list = [recipient_email] if recipient_email else []
                        
                            mail = EmailMultiAlternatives(subject, plain_message, from_email, recipient_list)
                            mail.attach_alternative(message, "text/html")
                            
                            mail.send()                
                    
                    return Response({"status": "true", "message": "Status changed successfully."}) 
            except IntegrityError as e:
                return Response({"status": "false", "message": f"Database integrity error: {e}."})
        else:
            return Response({"status": "false", "message": "Appointment not found."})
        







class visitore_detailView(APIView):
    def post(self, request):
        constants = my_constants(request)
        database_name = constants['database_name']
        appointment_id = request.data.get('appointment_id', '')
        
        if not appointment_id:
            return Response({"status": "false", "message": "Appointment ID is required."})

        try:
            appointment_id = int(appointment_id)
        except ValueError:
            return Response({"status": "false", "message": "Appointment ID must be a number."})
        
        base_image_url = constants['IMAGEPATH']
        # Define a placeholder image URL
        placeholder_image_url =  constants['DEFAULT_IMAGE']
        appointment_exist = appointment.objects.filter(id=appointment_id)
        if appointment_exist:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT    
                        {database_name}.appointment.*,
                        visitors.first_name AS visitor_first_name, 
                        visitors.email AS visitor_email, 
                        visitors.mobile AS visitor_mobile,
                        visitors.image as visitors_image,
                        employees.first_name AS employee_first_name, 
                        employees.email AS employee_email, 
                        employees.mobile AS employee_mobile
                        
                    FROM 
                        {database_name}.appointment 
                        INNER JOIN {database_name}.users AS visitors ON visitors.id = {database_name}.appointment.visitors_id
                        INNER JOIN {database_name}.users AS employees ON employees.id = {database_name}.appointment.employee_id
                    WHERE 
                        {database_name}.appointment.id = %s;
                    ;
                """, [appointment_id])

                columns = [col[0] for col in cursor.description]

                results = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
                for result in results:
                    if 'visitors_image' in result and result['visitors_image']:
                        # If the image URL is not empty or invalid, prepend the base URL
                        result['visitors_image'] = base_image_url + result['visitors_image']
                    else:
                        # Use the placeholder image URL if no image is provided
                        result['visitors_image'] = placeholder_image_url
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT  
                            {database_name}.appointment.*,
                            appointmentes.reason AS appointment_reason, 
                            appointmentes.date AS appointment_date, 
                            appointmentes.time AS appointment_time,
                            appointmentes.created_at AS  appointment_created_at, 
                            appointmentes.updated_at AS appointment_updated_at
                            
                        FROM 
                            {database_name}.appointment 
                            INNER JOIN {database_name}.appointment_reject AS appointmentes ON appointment_id = {database_name}.appointment.id
                        WHERE 
                            {database_name}.appointment.id = %s;
                        ;
                    """, [appointment_id])

                    columns = [col[0] for col in cursor.description]
                    appointment_reason = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]
                
                return Response({
                        "status": "true",
                        "data": results,
                        "appointment_reason":appointment_reason
                        
                    })
        else:
            return Response({"status": "false", "message": "Appointment not found."})