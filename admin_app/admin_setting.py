
from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
import datetime
from django.contrib import messages
from visitors_app.models import website_setting
from django.contrib.auth.hashers import check_password
from visitors_app.context_processors import my_constants
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
# def admin_setting_add(request):
#     constants = my_constants(request)
#     username = request.session.get('admin')
#     if not username:
#         return redirect('admin')
#     admin_data = constants.get('admin_data', {})
#     user_id = admin_data.get('id')
#     if request.method == "POST":
#         image = request.POST.get('image')
#         favicon = request.POST.get('favicon')
#         website_name = request.POST.get('website_name')
#         website_link = request.POST.get('website_link')
#         copyright = request.POST.get('copyright')
#         w_email = request.POST.get('w_email')
#         w_user = request.POST.get('w_user')
#         w_password = request.POST.get('w_password')
#         w_from_name = request.POST.get('w_from_name')
#         w_from_email = request.POST.get('w_from_email')

#         # Validate image file
#         if 'image' in request.FILES:
#             file = request.FILES['image']
#             file_extension = file.name.split('.')[-1].lower()
#             if file_extension in ['png', 'jpg', 'jpeg']:
#                 image = file
#             else:
#                 messages.error(request, 'Error: Invalid image format. Only PNG, JPG, and JPEG are allowed.',
#                               extra_tags='danger')
#                 return redirect('admin_setting_add')

#         # Validate favicon file
#         if 'favicon' in request.FILES:
#             favicon_file = request.FILES['favicon']
#             favicon_extension = favicon_file.name.split('.')[-1].lower()
#             if favicon_extension != 'ico':
#                 messages.error(request, 'Error: Invalid favicon format. Only ICO format is allowed.',
#                               extra_tags='danger')
#                 return redirect('admin_setting_add')
#             else:
#                 favicon = favicon_file  # If valid, assign the favicon file

#         # Create the website settings
#         user_create = website_setting.objects.create(
#             image=image,
#             website_name=website_name,
#             website_link=website_link,
#             copyright=copyright,
#             w_email=w_email,
#             w_user=w_user,
#             w_password=w_password,
#             w_from_name=w_from_name,
#             w_from_email=w_from_email,
#             favicon=favicon  # Ensure you also save the favicon if required
#         )
#         user_create.save()
#         messages.success(request, "Successfully setting created:")
#         return redirect('admin_setting_add')


#     return render(request, 'dashboard/admin_dashboard/admin_setting/admin_setting_add.html')


def admin_setting_update(request):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')

    admin_data = constants.get('admin_data', {})
    user_id = admin_data.get('id')

    # Fetch the first or specific setting (assuming only one exists)

    setting = website_setting.objects.first()
    

    if request.method == "POST":
        website_name = request.POST.get('website_name')
        website_link = request.POST.get('website_link')
        copyright = request.POST.get('copyright')
        smtp_host = request.POST.get('smtp_host')
        smtp_user = request.POST.get('smtp_user')
        smtp_password = request.POST.get('smtp_password')
        w_from_name = request.POST.get('w_from_name')
        w_from_email = request.POST.get('w_from_email')
        whatsapp_notificationes = request.POST.get('whatsapp_notification')
        if whatsapp_notificationes == 'on':
            whatsapp_notificationes = 1
        else:
            whatsapp_notificationes = 0
        if setting != None:
            # Validate image file
            if 'image' in request.FILES:
                file = request.FILES['image']
                file_extension = file.name.split('.')[-1].lower()
                if file_extension in ['png', 'jpg', 'jpeg']:
                    setting.image = file
                else:
                    messages.error(request, 'Error: Invalid image format. Only PNG, JPG, and JPEG are allowed.',
                                  extra_tags='danger')
                    return redirect('admin_setting_update')
    
            # Validate favicon file
            if 'favicon' in request.FILES:
                favicon_file = request.FILES['favicon']
                favicon_extension = favicon_file.name.split('.')[-1].lower()
                if favicon_extension != 'ico':
                    messages.error(request, 'Error: Invalid favicon format. Only ICO format is allowed.',
                                  extra_tags='danger')
                    return redirect('admin_setting_update')
                else:
                    setting.favicon = favicon_file  # Update favicon if valid
            now = datetime.datetime.now()
            updated_at = now.strftime("%y-%m-%d %H:%M:%S")
            # Update the fields with new data
            setting.website_name = website_name
            setting.website_link = website_link
            setting.copyright = copyright
            setting.smtp_host = smtp_host
            setting.smtp_user = smtp_user
            setting.smtp_password = smtp_password
            setting.from_name = w_from_name
            setting.from_email = w_from_email
            setting.whatsapp_notification=whatsapp_notificationes
            setting.updated_at = updated_at
            setting.save()  # Save the updated setting
            setting.save()
            messages.success(request, "Successfully updated setting.")
            return redirect('admin_setting_update')
        else:
            if 'image' in request.FILES:
                file = request.FILES['image']
                file_extension = file.name.split('.')[-1].lower()
                if file_extension in ['png', 'jpg', 'jpeg']:
                    image = file
                else:
                    messages.error(request, 'Error: Invalid image format. Only PNG, JPG, and JPEG are allowed.',
                                   extra_tags='danger')
                    return redirect('admin_setting_update')

            # Validate favicon file
            if 'favicon' in request.FILES:
                favicon_file = request.FILES['favicon']
                favicon_extension = favicon_file.name.split('.')[-1].lower()
                if favicon_extension != 'ico':
                    messages.error(request, 'Error: Invalid favicon format. Only ICO format is allowed.',
                                   extra_tags='danger')
                    return redirect('admin_setting_update')
                else:
                    favicon = favicon_file
            now = datetime.datetime.now()
            created_at = now.strftime("%y-%m-%d %H:%M:%S")
            if whatsapp_notificationes == 'on':
                whatsapp_notificationes = 1
            else:
                whatsapp_notificationes = 0

            user_create = website_setting.objects.create(
                image=image,
                website_name=website_name,
                website_link=website_link,
                copyright=copyright,
                smtp_host=smtp_host,
                smtp_user=smtp_user,
                smtp_password=smtp_password,
                from_name=w_from_name,
                from_email=w_from_email,
                favicon=favicon,
                created_at=created_at,
                whatsapp_notification=whatsapp_notificationes
                
                
            )
            user_create.save()
            messages.success(request, "Successfully setting created:")
            return redirect('admin_setting_update')
    # Render the update form with the existing setting data
    return render(request, 'dashboard/admin_dashboard/admin_setting/admin_setting_update.html', {
        'setting': setting
    })