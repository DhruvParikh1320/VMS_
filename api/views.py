from django.http import JsonResponse
from django.conf import settings
from django.db import connection
from visitors_app.views import date_time,generate_vms_string
from datetime import datetime
from visitors_app.context_processors import my_constants
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
import datetime
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password,make_password 
from visitors_app.models import user,roles,countries,states,cities,location,areas,appointment,auto_email
from visitors_app.context_processors import my_constants
from visitors_app.models import user,roles,countries,states,cities,location,areas,appointment,company,department
from visitors_app.context_processors import my_constants
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
import base64
import os
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from visitor_management import settings
from requests.auth import HTTPBasicAuth
from django.core import signing
# Function to retrieve today's checkouts from the database
def get_todays_checkouts(request):
    constants = my_constants(request)
    database_name = constants['database_name']
    # print('date:-',date_time())
    # today_date = date_time().split(' ')[0]
    # print('today_date:-',today_date)
    # today_str = f'20{today_date}'
    today_str =timezone.now().strftime('%Y-%m-%d')
    with connection.cursor() as cursor:
        query = f"""
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
        cursor.execute(query, [today_str])
        rows = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        all_visitor = [dict(zip(columns, row)) for row in rows]

    return all_visitor

# Function to format the checkout data into an HTML table
def format_checkouts_table(rows):
    table = "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>"
    table += "<thead><tr><th>#</th><th>Visitor Name</th><th>Visitor ID</th><th>To Meet</th><th>Visitor Email</th><th>Visitor Mobile</th><th>Check-In Time</th><th>Check-Out Time</th><th>Visitor Purpose</th><th>Visitor Type</th><th>Visitor Appointment Date</th><th>Visitor Appointment Time</th></tr></thead>"
    table += "<tbody>"

    count = 1
    for row in rows:
        print('yes.......row',row)
        visitor_name = f"{row['visitors_name']} {row['visitors_last_name']}"
        visitor_iD = row['visitors_uni_id'] 
        employee_name = f"{row['employee_name']} {row['employee_last_name']}"
        check_in_time = row['start_time']
        check_out_time = row['stop_time']
        visitor_email = row['visitors_email']
        visitor_mobile = row['visitors_mobile']
        visitor_purpose = row['purpose']
        visitor_type = row['visitors_type']
        appointment_date = row['date']
        appointment_time = row['time']
        table += f"<tr><td>{count}</td><td>{visitor_name}</td><td>{visitor_iD}</td><td>{employee_name}</td><td>{visitor_email}</td><td>{visitor_mobile}</td><td>{check_in_time}</td><td>{check_out_time}</td><td>{visitor_purpose}</td><td>{visitor_type}</td><td>{appointment_date}</td><td>{appointment_time}</td></tr>"
        count += 1

    table += "</tbody></table>"
    return table

# Function to send an email with the checkout data
def send_checkouts_email(request):
    constants = my_constants(request)
    
    checkouts = get_todays_checkouts(request)

    # if not checkouts:
    #     return None  # No checkouts today, no email to send
    
    subject = "Today's Check-In/Check-Out Reports"

    from_email = constants['From_Email']
    
    
    email_string = auto_email.objects.values_list('email', flat=True).first()  # Get the first (and possibly only) email string
    if email_string:
        # Split the comma-separated email addresses into a list
        to_email = [email.strip() for email in email_string.split(',')]
    else:
        to_email = []

    # Print the list of email addresses
    print('to_email', to_email)
    
    #to_email = ["taiyabshaikhs@gmail.com","narendra@indianinfotech.org","amit_tak@outlook.com"]  # Replace with actual recipients

    table = format_checkouts_table(checkouts)
    
    today = datetime.datetime.now().date()
    if not checkouts:

         # If no checkouts, send an email indicating that
        html_content = f"""
        <html>
        <body>
            <h2>No Check-Outs for {today.strftime('%B %d, %Y')}</h2>
            <p>There were no checkouts recorded today.</p>
        </body>
        </html>
        """
    else:
       
        html_content = f"""
        <html>
        <body>
            <h2>Check-Outs for {today.strftime('%B %d, %Y')}</h2>
            {table}
        </body>
        </html>
        """
    
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send()

    return True

# API view to trigger the email sending process and return a JSON response



class api_send_email_View(APIView):
    def get(self, request):
        try:
            result = send_checkouts_email(request)

            if result:
                return JsonResponse({"status": "success", "message": "Email sent successfully!"})
            else:
                return JsonResponse({"status": "success", "message": "No checkouts to send."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"})



class visitor_type(APIView):
    def get(self, request):
        data = [            
            {"value": "candidate", "label": "Candidate"},
            {"value": "customer", "label": "Customer"},
            {"value": "general", "label": "General"},
            {"value": "government officer", "label": "Government Officer"},
            {"value": "interviewer", "label": "Interviewer"},
            {"value": "vender", "label": "Vender"},
            {"value": "other", "label": "Other"}
        ]
        # Return as JSON response
        return Response({ "status": "true",'data':data})


class employee(APIView):
    def post(self, request):
        try:
            # Load constants
            constants = my_constants(request)
            from_email = constants['From_Email']
            live_ip = constants['ADMIN_PATH']

            # Extract data from the request
            firstname = request.data.get('Firstname', '')
            lastname = request.data.get('Lastname', '')
            email = request.data.get('Email', '')
            mobile = request.data.get('mobile', '')
            gender = request.data.get('gender', '')
            address = request.data.get('Address', '')
            visitors_type = request.data.get('visitors_type', '')
            image = request.FILES.get('image')
            employees = request.data.get('employee', '')
            company_id = request.data.get('company_id', '')
            department_id = request.data.get('department_id', '')
            location_id = request.data.get('location_id', '')
            date = request.data.get('date', '')
            time = request.data.get('time', '')
            detail = request.data.get('detail', '')
            purpose = request.data.get('Purpose', '')
            status = request.data.get('status', '')
            visitors_timing = request.data.get('visitors_timing', '')
            created_at = date_time()
            updated_at = date_time()
            # Check if user with the given email already exists
            user_exist = user.objects.filter(email=email).first()
            if not user_exist:
                # Create a new user
                new_user = user(
                    first_name=firstname,
                    last_name=lastname,
                    email=email,
                    password='',
                    address=address,
                    mobile=mobile,
                    gender=gender,
                    image=image,
                    type='visitors',
                    company_id=company_id,
                    department_id=department_id,
                    location_id=location_id,
                    is_active=status,
                    created_at=created_at,
                    uni_id=generate_vms_string(),
                    created_by=employees,
                    employee_code=0
                )

                # Save the image if provided
                if image:
                    valid_extensions = ['jpg', 'jpeg', 'png']
                    extension = os.path.splitext(image.name)[1][1:].lower()
                    if extension not in valid_extensions:
                        return Response({"status": "false", "message": "Invalid image format. Only jpg, jpeg, and png are allowed."}, status=400)

                    original_filename = image.name
                    saved_path = default_storage.save(f'user/{original_filename}', image)
                    new_user.image = saved_path.split('/')[-1]

                # Save the user
                new_user.save()
            else:
               
                return Response({"status": "false", "message": "User already exists."})

            # Create appointment
            visitors_type = visitors_type if visitors_type else 'other'
            new_appointment = appointment(
                employee_id=employees,
                date=date,
                time=time,
                status='pending',
                purpose=purpose,
                visitors_type=visitors_type,
                detail=detail,
                visitors_id=new_user.id,
                created_at=date_time(),
                created_by=employees,
                visitors_timing = visitors_timing,
            )
            new_appointment.save()

            # Send employee notification email
            employee_email = user.objects.filter(id=employees).first()
            if employee_email:
                try:
                    subject_employee = 'Visitor Appointment'
                    context_employee = {
                        'employee_data': employee_email,
                        'visitor_data': new_user,
                        'new_appointment': new_appointment,
                    }
                    template_name_employee = 'dashboard/admin_dashboard/admin_notifitation/employee_notification_email.html'
                    message_employee = render_to_string(template_name_employee, context_employee)
                    plain_message_employee = strip_tags(message_employee)
                    recipient_list_employee = [employee_email]  # Ensure email field is used

                    mail_employee = EmailMultiAlternatives(subject_employee, plain_message_employee, from_email, recipient_list_employee)
                    mail_employee.attach_alternative(message_employee, "text/html")
                    mail_employee.send()
                except Exception as e:
                    pass
                    #return Response({"status": "false", "message": f"Error in employee email: {str(e)}"})

            # Send visitor confirmation email
            if email:
                try:
                    appointment_id = new_appointment.id
                    encrypted_appointment_id = signing.dumps(appointment_id)
                    confirmation_link = f"{live_ip}/register/{encrypted_appointment_id}"
                    subject_visitor = 'Appointment Confirmation'
                    context_visitor = {
                        'visitor_data': new_user,
                        'employee_data': employee_email,
                        'new_appointment': new_appointment,
                        'confirmation_link': confirmation_link,
                        'is_link': True,
                    }

                    template_name_visitor = 'dashboard/admin_dashboard/admin_notifitation/visitor_confirmation_email.html'
                    message_visitor = render_to_string(template_name_visitor, context_visitor)
                    plain_message_visitor = strip_tags(message_visitor)
                    recipient_list_visitor = [email]

                    mail_visitor = EmailMultiAlternatives(subject_visitor, plain_message_visitor, from_email, recipient_list_visitor)
                    mail_visitor.attach_alternative(message_visitor, "text/html")
                    mail_visitor.send()
                except Exception as e:
                    return Response({"status": "false", "message": f"Error in visitor email: {str(e)}","data":context_visitor})

            # Prepare response data
            user_data = {
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'mobile_number': new_user.mobile,
                'email': new_user.email,
                'gender': new_user.gender,
                'image': f'{constants["IMAGEPATH"]}{new_user.image.url}' if new_user.image else f'{constants["DEFAULT_IMAGE"]}',
                'address': new_user.address,
            }
        
            return Response({"status": "true", "message": f"User created successfully.", "data": user_data})

        except Exception as e:
            return Response({"status": "false", "message": f"Error: {str(e)}"})
        

class employee_data(APIView):
    def post(self,request):
        employee_id = request.data.get('employee_code', '')
        
        if employee_id == '':
            return Response({"status": "false", "message": "All fields are required."})
        user_instance = user.objects.filter(employee_code=employee_id).first()
        
        if user_instance is not None:
            company_data = company.objects.filter(id=user_instance.company_id).values('id', 'company_name').first()
            department_data = department.objects.filter(id=user_instance.department_id).values('id', 'department_name').first()
            location_data = location.objects.filter(id=user_instance.location_id).values('id', 'location_name').first()
            
            response_data = {
                'company': [company_data] if company_data else [],
                'departments': [department_data] if department_data else [],
                'location': [location_data] if location_data else [],
            }
            # response_data = {
            #     'company': [
            #         "id": company_data['id'],
            #         "company_name": company_data['company_name']
            #     ] if company_data else [],
            #     'departments': [
            #         f"id: {department_data['id']}",
            #         f"department_name: {department_data['department_name']}"
            #     ] if department_data else [],
            #     'location': [
            #         f"id: {location_data['id']}",
            #         f"location_name: {location_data['location_name']}"
            #     ] if location_data else [],
            # }
            
            return Response({"status": "true","data":response_data})
        else:
            return Response({"status": "false", "message": "User not found"})


class new_appointment(APIView):
    def post(self, request):
        constants = my_constants(request)        
        from_email = constants['From_Email']
        visitors_id = request.data.get('visitors_id', '')
        employee_id = request.data.get('employee','')
        date = request.data.get('date','')
        time = request.data.get('time','')
        purpose = request.data.get('Purpose','')
        visitors_type = request.data.get('visitors_type','')
        detail = request.data.get('detail','')
        visitors_timing = request.data.get('visitors_timing', '')
        
        if not all([visitors_id, employee_id, date, time, purpose, visitors_type]):
            return Response({"status": "false", "message": "All fields are required."})
        
        Visitor = user.objects.filter(id=visitors_id).first()
       
        Employee = user.objects.filter(id=employee_id).first()
        
        if Visitor is None:
            return Response({"status": "false", "message": "Visitor not found"})

        if Employee is None :
            return Response({"status": "false", "message": "Employee not found"})
        try:
            # Create new appointment object
            appointment_obj = appointment(
                visitors_id=visitors_id,
                employee_id=employee_id,
                date=date,
                time=time,
                status='pending',
                created_at=date_time(),  # Assuming date_time() is a helper function
                purpose=purpose,
                visitors_type=visitors_type,
                detail=detail,
                created_by=employee_id,
                visitors_timing = visitors_timing,
            )
            appointment_obj.save()

            # Fetch visitor and employee data
            visitor = user.objects.filter(id=visitors_id).first()
            employee = user.objects.filter(id=employee_id).first()
            
            if employee:
                try:
                    # Email to employee
                    subject_employee = 'Visitor Appointment'
                    context_employee = {
                        'employee_data': employee,
                        'visitor_data': visitor,
                        'new_appointment': appointment_obj,
                    }
                    template_name_employee = 'notification_email/employee_notification_email.html'
                    message_employee = render_to_string(template_name_employee, context_employee)
                    plain_message_employee = strip_tags(message_employee)
                    recipient_list_employee = [employee.email]
                    print('recipient_list_employee',recipient_list_employee)
                    mail_employee = EmailMultiAlternatives(subject_employee, plain_message_employee, from_email, recipient_list_employee)
                    mail_employee.attach_alternative(message_employee, "text/html")
                    mail_employee.send()
                except Exception as e:
                    print('Email send error:', e)
                    return Response({"status": "false", "message": f"Email send error: {e}"})
            
            # Email to visitor
            if visitor and visitor.email:
                try:
                    subject_visitor = 'Appointment Confirmation'
                    context_visitor = {
                        'visitor_data': visitor,
                        'employee_data': employee,
                        'new_appointment': appointment_obj,
                        'is_link': False
                    }
                    
                    template_name_visitor = 'dashboard/admin_dashboard/admin_notifitation/visitor_confirmation_email.html'
                    message_visitor = render_to_string(template_name_visitor, context_visitor)
                    plain_message_visitor = strip_tags(message_visitor)
                    recipient_list_visitor = [visitor.email]
                    print('recipient_list_visitor:-',recipient_list_visitor)
                    mail_visitor = EmailMultiAlternatives(subject_visitor, plain_message_visitor, from_email, recipient_list_visitor)
                    mail_visitor.attach_alternative(message_visitor, "text/html")
                    mail_visitor.send()

                    return Response({"status": "true", "message": "Appointment successfully created."})
                except Exception as e:
                    print(f"Email to visitor error: {e}")
                    return Response({"status": "false", "message": f"Email to visitor error: {e}"})
            else:
                return Response({"status": "false", "message": "Visitor email not found."})
        
        except Exception as e:
            print(f"Appointment creation error: {e}")
            return Response({"status": "false", "message": f"Appointment creation error: {e}"})
        
        
# class all_visitor(APIView):
#     def post(self, request):
#         constants = my_constants(request)
#         page = request.data.get('page', 1)  # Default to page 1 if not provided
        
#         if page == '':
#             return Response({"status": "false", "message": "Page number is required."})
#         page = int(page)

#         database_name = constants['database_name']
#         results_per_page = 10  # Define the number of results per page
#         base_image_url = constants['IMAGEPATH']
#         placeholder_image_url = constants['DEFAULT_IMAGE']
#         offset = (page - 1) * results_per_page  # Calculate the offset for pagination

#         # Extracting search parameter from the request (if needed)
#         search_term = request.data.get('search', '')
#         search_params = []
#         search = ""

#         # If there's a search term, add it to the WHERE clause
#         if search_term:
#             search = """ AND (users.first_name LIKE %s 
#                               OR users.last_name LIKE %s
#                               OR created_by.first_name LIKE %s 
#                               OR created_by.last_name LIKE %s)"""
#             search_params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])

#         with connection.cursor() as cursor:
#             # First query to count total users
#             sql_query_count = f"""
#             SELECT COUNT(*) AS users
#             FROM {database_name}.users AS users
#             LEFT JOIN {database_name}.users AS created_by ON created_by.id = users.created_by
#             WHERE users.type = 'visitors' {search}
#             """
#             cursor.execute(sql_query_count, search_params)
#             database_all_data = cursor.fetchone()
#             recordsTotal = database_all_data[0] if database_all_data else 0
#             total_pages = (recordsTotal + results_per_page - 1) // results_per_page  # Calculate total pages
#             is_last_page = page == total_pages
#             # Second query to fetch paginated user details
#             sql_query = f"""
#             SELECT 
#                 users.*, 
#                 created_by.first_name AS created_by_first_name,
#                 created_by.last_name AS created_by_last_name
#             FROM {database_name}.users AS users
#             LEFT JOIN {database_name}.users AS created_by ON created_by.id = users.created_by
#             WHERE users.type = 'visitors' {search}
#             ORDER BY users.id DESC
#             LIMIT %s OFFSET %s;
#             """
#             cursor.execute(sql_query, search_params + [results_per_page, offset])
#             database_all_data = cursor.fetchall()
#             print('database_all_data:-',database_all_data)
#             # Get column names
#             columns = [col[0] for col in cursor.description]
#             # all_visitor_data = [dict(zip(columns, row)) for row in database_all_data]
#             all_visitor_data = []

#             # Append base_image_url to the image field
#             for row in database_all_data:
#                 visitor_data = dict(zip(columns, row))
                
#                 # Update image URL if image is present, otherwise use placeholder
#                 if visitor_data.get('image'):  
#                     visitor_data['image'] = f"{base_image_url}{visitor_data['image']}"
#                 else:  
#                     visitor_data['image'] = placeholder_image_url
                
#                 all_visitor_data.append(visitor_data)
                
#         # Return the response with total records and paginated data
#         return Response({
#             'recordsTotal': recordsTotal,
#             'data': all_visitor_data,
#             'totalPages': total_pages,                 # Total number of pages
#             'currentPage': page,                       # Current page number
#             'isLastPage': is_last_page,
            
#         })


class all_visitor(APIView):
    def post(self, request):
        constants = my_constants(request)
        page = request.data.get('page', 1)  # Default to page 1 if not provided
        
        if page == '':
            return Response({"status": "false", "message": "Page number is required."})
        page = int(page)

        database_name = constants['database_name']
        results_per_page = 10  # Define the number of results per page
        base_image_url = constants['IMAGEPATH']
        placeholder_image_url = constants['DEFAULT_IMAGE']
        offset = (page - 1) * results_per_page  # Calculate the offset for pagination

        # Extracting search parameter from the request (if needed)
        search_term = request.data.get('search', '')
        search_params = []
        search = ""

        # If there's a search term, add it to the WHERE clause
        if search_term:
            search = """ AND (users.first_name LIKE %s 
                              OR users.last_name LIKE %s
                              OR created_by.first_name LIKE %s 
                              OR created_by.last_name LIKE %s
                              OR users.email LIKE %s 
                              OR users.mobile LIKE %s)"""
            search_params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])

        with connection.cursor() as cursor:
            # First query to count total users
            sql_query_count = f"""
            SELECT COUNT(*) AS users
            FROM {database_name}.users AS users
            LEFT JOIN {database_name}.users AS created_by ON created_by.id = users.created_by
            WHERE users.type = 'visitors' {search}
            """
            cursor.execute(sql_query_count, search_params)
            database_all_data = cursor.fetchone()
            recordsTotal = database_all_data[0] if database_all_data else 0
            total_pages = (recordsTotal + results_per_page - 1) // results_per_page  # Calculate total pages
            is_last_page = page == total_pages

            # Second query to fetch paginated user details
            sql_query = f"""
            SELECT 
                users.*, 
                created_by.first_name AS created_by_first_name,
                created_by.last_name AS created_by_last_name
            FROM {database_name}.users AS users
            LEFT JOIN {database_name}.users AS created_by ON created_by.id = users.created_by
            WHERE users.type = 'visitors' {search}
            ORDER BY users.id DESC
            LIMIT %s OFFSET %s;
            """
            cursor.execute(sql_query, search_params + [results_per_page, offset])
            database_all_data = cursor.fetchall()

            # Get column names
            columns = [col[0] for col in cursor.description]
            all_visitor_data = []

            # Append base_image_url to the image field
            for row in database_all_data:
                visitor_data = dict(zip(columns, row))
                
                # Update image URL if image is present, otherwise use placeholder
                if visitor_data.get('image'):  
                    visitor_data['image'] = f"{base_image_url}{visitor_data['image']}"
                else:  
                    visitor_data['image'] = placeholder_image_url
                
                all_visitor_data.append(visitor_data)
                
        # Return the response with total records and paginated data
        return Response({
            'recordsTotal': recordsTotal,
            'data': all_visitor_data,
            'totalPages': total_pages,                 # Total number of pages
            'currentPage': page,                       # Current page number
            'isLastPage': is_last_page,
        })