
from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
# Create your views here.
# Create your views here.
from django.contrib import messages
from visitors_app.models import user,roles,safety_training
from django.contrib.auth.hashers import check_password
from visitors_app.context_processors import my_constants
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import connection
from visitors_app.views import generate_vms_string
from visitors_app.views import date_time
import os
def admin_safety_training_add(request):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    admin_data = constants.get('admin_data', {})
    if request.method == 'POST':
        title = request.POST['title']
        video_files = request.FILES.get('video_files')
        if video_files:
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'safety_training/')
            os.makedirs(upload_dir, exist_ok=True)  # Create the directory if it doesn't exist
            file_path = os.path.join(upload_dir, video_files.name)

            # Save the file to the defined directory
            with open(file_path, 'wb') as f:
                for chunk in video_files.chunks():
                    f.write(chunk)
        status = request.POST['status']
        created_at = date_time()
        safety_traininges = safety_training(title=title, video_file=video_files.name, is_active=status,created_at=created_at)
        safety_traininges.save()
        messages.success(request, "safety_traininges successfully.", extra_tags="success")
        return redirect('admin_safety_training_add')
    return render(request, 'dashboard/admin_dashboard/admin_safety_training/admin_safety_training_add.html')




def admin_safety_training(request):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')

    return render(request, 'dashboard/admin_dashboard/admin_safety_training/admin_safety_training.html')

def admin_safety_training_ajax_page_ajax(request):
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
        search = f'AND ( title LIKE "%{search_value}%" )'
    # First SQL query to get the count of appointments

    sql_query = f"""
            SELECT COUNT(*) AS safety_training_count
            FROM {database_name}.safety_training
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
        select {database_name}.safety_training.*
        from  {database_name}.safety_training
        where 1=1 {search}
    	ORDER BY
    		safety_training.id DESC 
        LIMIT {length} OFFSET {start};
    """
    # Execute the second SQL query
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        database_all_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        all_coupon_dtl = [dict(zip(columns, row)) for row in database_all_data]
    return JsonResponse({"recordsTotal": recordsTotal, "recordsFiltered": recordsTotal, 'data': all_coupon_dtl})




def admin_safety_training_delete(request,id):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    all_safety_training = get_object_or_404(safety_training,id=id)
    all_safety_training.delete()
    data = {
        'status': 1,
        'message': f'Safety Training Deleted Successfully.',
    }
    messages.success(request, f"successfully Safety Training Deleted!", extra_tags="success")
    return JsonResponse(data)




def admin_safety_training_edit(request, id):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    print('yes')
    user_data = constants.get('admin_data', {})
    all_safety_training = get_object_or_404(safety_training, id=id)
    
    if request.method == "POST":
        title = request.POST['title']
        video_files = request.FILES.get('video_files')
        status = request.POST['status']
        updated_at = date_time()

        if video_files:
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'safety_training/')
            os.makedirs(upload_dir, exist_ok=True)  # Create the directory if it doesn't exist
            file_path = os.path.join(upload_dir, video_files.name)

            # Save the new file to the defined directory
            with open(file_path, 'wb') as f:
                for chunk in video_files.chunks():
                    f.write(chunk)

            # Update the video file name if a new file is uploaded
            all_safety_training.video_file = video_files.name

        # Update the other fields
        all_safety_training.title = title
        all_safety_training.is_active = status
        all_safety_training.updated_at = updated_at
        all_safety_training.save()

        messages.success(request, "Safety training updated successfully.", extra_tags="success")
        return redirect('admin_safety_training')

    return render(request, 'dashboard/admin_dashboard/admin_safety_training/admin_safety_training_edit.html', {
        'training_instance': all_safety_training
    })