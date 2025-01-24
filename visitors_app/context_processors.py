from django.conf import settings
from .models import user,website_setting
from datetime import datetime
# def my_constants(request):
#     DOMAIN_NAME = settings.DOMAIN_NAME
#     DOMAIN_ICON = settings.DOMAIN_ICON
#     return {
#         'DOMAIN_NAME': DOMAIN_NAME,
#         'DOMAIN_ICON':DOMAIN_ICON
#     }

def my_constants(request):
    
    database_name = settings.DATABASE_NAME
    website_settings = website_setting.objects.first()
    DOMAIN_NAME = settings.DOMAIN_NAME
    
    if website_settings:
        DOMAIN_ICON = f"website_setting/favicon/{website_settings.favicon}"
        GET_PASS_IMAGE = f"website_setting/logo/{website_settings.image}"
        From_Email = f"{website_settings.from_name} <{website_settings.from_email}>"
    
        website_name = website_settings.website_name
        website_linkes = website_settings.website_link
        website_copyright = website_settings.copyright
    else:
        DOMAIN_ICON= ''
        GET_PASS_IMAGE =''
        From_Email =''
        website_name = ''
        website_linkes = ''
        website_copyright =''
    ADMIN_PATH =  settings.DOMAIN_URL
    # GET_PASS_IMAGE = settings.GET_PASS_IMAGE
    
    BACKGROUND_IMAGE = settings.BACKGROUND_IMAGE
    IMAGEPATH = f'{ADMIN_PATH}user/'
    DEFAULT_IMAGE = f"{ADMIN_PATH}user/user.png"
    # From_Email = 'TEAfrica <visit@easyvisit.in>'
    
    user_data = {}
    gate_keeper_data = {}
    admin_data = {}
    employee_data = {}

    user_session = request.session.get('visitors')
    if user_session:
        email = user_session.get('user_email')
        if email:
            try:
                user_instance = user.objects.get(email=email)
                
                user_data = {
                    'id': user_instance.id,
                    'user_name': user_session.get('user_name'),
                    'user_email': email,
                    'first_name': user_instance.first_name,
                    'last_name': user_instance.last_name,
                    'image': user_instance.image.url if user_instance.image else None,
                    'document': f"{ADMIN_PATH}user/document",
                    'users_images': f"{ADMIN_PATH}user/",
                    'default_image': f"{ADMIN_PATH}user/user.png"
                }
            except user.DoesNotExist:
                user_data = {'error': 'User does not exist'}

    gate_keeper_session = request.session.get('gate_keeper')
    if gate_keeper_session:
        email = gate_keeper_session.get('user_email')
        if email:
            try:
                gate_keeper_instance = user.objects.get(email=email)
                gate_keeper_data = {
                    'id': gate_keeper_instance.id,
                    'user_name': gate_keeper_session.get('user_name'),
                    'user_email': email,
                    'first_name': gate_keeper_instance.first_name,
                    'last_name': gate_keeper_instance.last_name,
                    'image': gate_keeper_instance.image.url if gate_keeper_instance.image else None,
                    'document': f"{ADMIN_PATH}user/document",
                    'users_images': f"{ADMIN_PATH}user/",
                    'default_image': f"{ADMIN_PATH}user/user.png"
                }
            except user.DoesNotExist:
                gate_keeper_data = {'error': 'Gate Keeper does not exist'}

    admin_session = request.session.get('admin')
    
    if admin_session:
        email = admin_session.get('user_email')
        if email != 'admin_by@example.com':
            try:
                admin_instance = user.objects.get(email=email)
                if admin_instance:
                    admin_data = {
                        'id': admin_instance.id,
                        'user_name': admin_session.get('user_name'),
                        'user_email': email,
                        'first_name': admin_instance.first_name,
                        'last_name': admin_instance.last_name,
                        'image': admin_instance.image.url if admin_instance.image else None,
                        'users_images': f"{ADMIN_PATH}user/",
                        'document': f"{ADMIN_PATH}user/document",
                        'default_image': f"{ADMIN_PATH}user/user.png"
                    }
            except user.DoesNotExist:
                admin_data = {'error': 'Admin does not exist'}
        else:
            admin_data = {
                        'id': 0,
                        'user_name': admin_session.get('user_name'),
                        'user_email': email,
                        'first_name':'Admines',
                        'last_name': 'Admines',
                        'image': None,
                        'users_images': f"{ADMIN_PATH}user/",
                        'document': f"{ADMIN_PATH}user/document",
                        'default_image': f"{ADMIN_PATH}user/user.png"
                    }
    employee_session = request.session.get('employee')
    if employee_session:
        email = employee_session.get('user_email')
        if email:
            try:
                employee_instance = user.objects.get(email=email)
                employee_data = {
                    'admin_name':'Employee',
                    'id': employee_instance.id,
                    'user_name': employee_session.get('user_name'),
                    'user_email': email,
                    'first_name': employee_instance.first_name,
                    'last_name': employee_instance.last_name,
                    'image': employee_instance.image.url if employee_instance.image else None,
                    'document': f"{ADMIN_PATH}user/document",
                    'users_images': f"{ADMIN_PATH}user/",
                    'default_image': f"{ADMIN_PATH}user/user.png",
                    'employee_code':employee_instance.employee_code
                }
            except user.DoesNotExist:
                employee_data = {'error': 'Employee does not exist'}
                
    current_year = datetime.now().strftime('%Y')
    return {
        'DOMAIN_NAME': DOMAIN_NAME,
        'DOMAIN_ICON': DOMAIN_ICON,
        'user_data': user_data,
        'gate_keeper_data': gate_keeper_data,
        'employee_data': employee_data,
        'admin_data': admin_data,
        'IMAGEPATH': IMAGEPATH,
        'DEFAULT_IMAGE': DEFAULT_IMAGE,
        'From_Email': From_Email,
        'ADMIN_PATH':ADMIN_PATH,
        'current_year': current_year,
        'database_name':database_name,
        'GET_PASS_IMAGE':GET_PASS_IMAGE,
        'background_image':BACKGROUND_IMAGE,
        'website_name':website_name,
        'website_link':website_linkes,
        'copyright':website_copyright
        
    }