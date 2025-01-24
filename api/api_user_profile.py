from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password,make_password
from visitors_app.models import user,roles,countries,states,cities,location,areas
from visitors_app.context_processors import my_constants
import os
from django.conf import settings
from django.core.files.storage import default_storage
from visitors_app.views import date_time
class user_profileView(APIView):
    def post(self, request):

        constants = my_constants(request)
        
        user_id = request.data.get('user_id','')
        
        if not user_id:
            
            return Response({"status": "false", "message": "user id is required."})
        
                            
        user_exist = user.objects.filter(id = user_id,is_active=1,type='employee').first()

        if user_exist:
            
            image_name = user_exist.image.name if user_exist.image else None

            # image_path = os.path.join(settings.MEDIA_ROOT, 'user', image_name)

            
            # # Check if the image file exists
            # if os.path.isfile(image_path):
            #     image_url = f'{constants["IMAGEPATH"]}{user_exist.image.url}'
            # else:
            #     image_url =  f'{constants["DEFAULT_IMAGE"]}'
            
            
            image_url = constants["DEFAULT_IMAGE"] 

            if user_exist.image:
                image_name = user_exist.image.name
                image_path = os.path.join(settings.MEDIA_ROOT, 'user', image_name)

                if os.path.isfile(image_path):
                    image_url = f'{constants["IMAGEPATH"]}{user_exist.image.url}'
            
            first_name = user_exist.first_name
            last_name = user_exist.last_name
            email = user_exist.email
            mobile_number = user_exist.mobile
            gender = user_exist.gender
            address = user_exist.address
            user_data = {
                'first_name':first_name,
                'last_name':last_name,
                'mobile_number':mobile_number,
                'email':email,
                'gender':gender,
                'image':image_url,
                'address':address
                
            }
            return Response({"status": "true", "data": user_data}) 
        
        else:
            return Response({"status": "false", "message": "User does not exist."})
        

class profile_updateView(APIView):
    def post(self, request):

        constants = my_constants(request)
        
        user_id = request.data.get('user_id', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        email = request.data.get('email', '')
        gender = request.data.get('gender', '')
        address = request.data.get('address', '')
        mobile_number = request.data.get('mobile_number', '')
        password = request.data.get('password', '')
        image = request.FILES.get('image')

        if not user_id:
            return Response({"status": "false", "message": "User ID is required."})

        try:
            user_exist = user.objects.get(id=user_id, is_active=1, type='employee')
            
        except user.DoesNotExist:
            return Response({"status": "false", "message": "User does not exist."})

        try:
            if first_name:
                user_exist.first_name = first_name
            if last_name:
                user_exist.last_name = last_name
            if email:
                user_exist.email = email
            if gender:                
                user_exist.gender = gender
            if address:
                user_exist.address = address
            if mobile_number:
                user_exist.mobile = mobile_number

            
            
            if password:
                user_exist.password = make_password(password)

            if image:
                valid_extensions = ['jpg', 'jpeg', 'png']
                extension = os.path.splitext(image.name)[1][1:].lower()
                if extension not in valid_extensions:
                    return Response({"status": "false", "message": "Invalid image format. Only jpg, jpeg, and png are allowed."})

                original_filename = image.name
                saved_path = default_storage.save(f'user/{original_filename}', image)

                # If the user already has an image, delete the old image file
                if user_exist.image and default_storage.exists(user_exist.image.path):
                    default_storage.delete(user_exist.image.path)
                
                # Update the user's image field
                saved_path = saved_path.split('/')[-1]
                user_exist.image = saved_path
            user_exist.updated_at = date_time() 
            user_exist.save()

            # Retrieve updated user data
            user_exist.refresh_from_db()
            image_url = f'{constants["IMAGEPATH"]}{user_exist.image.url}' if user_exist.image else f'{constants["DEFAULT_IMAGE"]}'

            user_data = {
                'first_name': user_exist.first_name,
                'last_name': user_exist.last_name,
                'mobile_number': user_exist.mobile,
                'email': user_exist.email,
                'gender': user_exist.gender,
                'image': image_url,
                'address': user_exist.address,
            }

            return Response({"status": "true", "data": user_data})

        except Exception as e:
            return Response({"status": "false", "message": f"Error: {str(e)}"})

