from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from visitors_app.models import user,roles,countries,states,cities,location,areas
from visitors_app.context_processors import my_constants
import os
from django.conf import settings

class UsersigninView(APIView):
    def post(self,request):
        constants = my_constants(request)
        employee_code = request.data.get('employee_code', '')
        password = request.data.get('password', '')
        errors = []

        # Check if employee_code and password are provided
        if not employee_code:
            errors.append("Employee code is required.")
        if not password:
            errors.append("Password is required.")
        
        # Return error response if there are missing fields
        if errors:
            return Response({"status": "false", "message": " ".join(errors)})

        user_exist = user.objects.filter(employee_code=employee_code, is_active=1).first()


        if 'employee' in user_exist.type:
 
            if check_password(password, user_exist.password):

                image_url = constants["DEFAULT_IMAGE"] 

                if user_exist.image:
                    image_name = user_exist.image.name
                    image_path = os.path.join(settings.MEDIA_ROOT, 'user', image_name)

                    if os.path.isfile(image_path):
                        image_url = f'{constants["IMAGEPATH"]}{user_exist.image.url}'

                user_data = {
                    'id': user_exist.id,
                    'first_name': user_exist.first_name,
                    'last_name': user_exist.last_name,
                    'email': user_exist.email,
                    'image': image_url,
                    'emp_code':user_exist.employee_code,
                }

                # Return success response with user data
                return Response({"status": "true", 'message': 'Successfully Logged in', "data": user_data})
            else:
                # If the password is incorrect
                return Response({"status": "false", "message": "Invalid employee code or password."})
        else:
            # If the user does not exist or is not of type 'employee'
            return Response({"status": "false", "message": "User does not exist or is not an employee."})


