import datetime

from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
# Create your views here.
from django.contrib import messages
from .models import user
from django.contrib.auth.hashers import check_password ,make_password
from django.contrib.auth import authenticate, login
from django.core.files.images import get_image_dimensions


def visitors_edit(request):
    username = request.session.get('visitors')
    # user_type = request.session.get('user_type')
    # print('user_type:-', user_type)

    if not username :
        return redirect('visitors')
        # return redirect('gate_keeper')
    email = username['user_email']
    user_name = username['user_name']
    visitors_user = user.objects.get(email=email)
    if request.method == "POST":
        visitors_user.frist_name = request.POST['Firstname']
        
        visitors_user.last_name = request.POST['Lastname']
        
        visitors_user.email = request.POST['Email']
        
        # visitors_user.password = request.POST['Password']
        #
        # visitors_user.password = request.POST['Confirm_Password']
        
        visitors_user.address = request.POST['Address']
        
        visitors_user.mobile = request.POST['mobile']
        
        visitors_user.gender = request.POST['gender']
        password = request.POST['Password']
        confirm_password = request.POST['Confirm_Password']

        if password == '' and confirm_password == '':
            visitors_user.password = visitors_user.password

        elif password == confirm_password:
            visitors_user.password = make_password(confirm_password)
        else:
            messages.error(request, 'Passwords do not match.', extra_tags='danger')
            return redirect('visitors_edit')

        if 'image' in request.FILES:
            file = request.FILES['image']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension in ['png', 'jpg', 'jpeg']:
                visitors_user.image = file
            else:
                messages.error(request, 'Error: Invalid image format.', extra_tags='danger')
                return redirect('visitors_edit')
        if 'document' in request.FILES:
            document = request.FILES['document']
            document_extension = document.name.split('.')[-1].lower()
            if document_extension in ['png', 'jpg', 'jpeg', 'pdf']:
                visitors_user.document = document
            else:
                messages.error(request, 'Error: Invalid document format.', extra_tags='danger')
                return redirect('visitors_edit')
        visitors_user.save()
        visitors_user.save()
        messages.success(request, f"Successfully created:", extra_tags="success")
    return render(request,'dashboard/visitors_dashboard/profile_edit.html',{'visitors_user':visitors_user,'username': username})
    