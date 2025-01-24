from django.shortcuts import render,HttpResponse,redirect
from django.conf import settings
# Create your views here.
# Create your views here.
from django.contrib import messages
from visitors_app.models import user,roles
from django.contrib.auth.hashers import check_password
from visitors_app.context_processors import my_constants
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
def admin_role_all(request):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    admin_data = constants.get('admin_data', {})
    user_id = admin_data.get('id')
    all_role = roles.objects.all()
    return render(request, 'dashboard/admin_dashboard/admin_roles/admin_role.html', {'all_role':all_role})



def admin_role_add(request):
    constants = my_constants(request)
    username = request.session.get('admin')
    if not username:
        return redirect('admin')
    admin_data = constants.get('admin_data', {})
    user_id = admin_data.get('id')
    all_roles= roles.objects.filter()
    if request.method == "POST":
        name = request.POST['name']
        try:
            if roles.objects.filter(name=name).exists():
                messages.error(request, "Role with this name already exists.",extra_tags="danger")
                return redirect('admin_role_add')
            # print('provider_id:', request.POST.get('provider_id', None))
            user_create =roles.objects.create(name=name)
            roles.save(user_create)
            messages.success(request, f"Successfully roles created:")
            return redirect('admin_role_all')
            error = 'no'
        except Exception as e:
            return redirect('admin_role_add')
    return render(request, 'dashboard/admin_dashboard/admin_roles/admin_role_add.html')


def admin_role_edit(request,id):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    
    all_role = roles.objects.get(id=id)
    print('all_role:-',all_role.name)
    if request.method == "POST":
        new_name = request.POST['name']
        
        # if roles.objects.filter(name=new_name).exclude(id=id).exists():
        #     messages.error(request, "Role with this name already exists.", extra_tags="danger")
        #     return redirect('admin_role_edit', id=id)
        all_role.name = new_name
        all_role.save()
        messages.success(request, "Roles successfully updated.", extra_tags="success")
        return redirect('admin_role_all')
    all_role = {'all_role':all_role}
    return render(request,'dashboard/admin_dashboard/admin_roles/admin_role_edit.html',all_role)


def admin_role_delete(request,id):
    username = request.session.get('admin')
    if not username :
        return redirect('admin')
    all_roles = get_object_or_404(roles,id=id)
    all_roles.delete()
    data = {
        'status': 1,
        'message': f'Roles Deleted Successfully.',
    }
    messages.success(request, f"successfully Roles Deleted!", extra_tags="success")
    return JsonResponse(data)

