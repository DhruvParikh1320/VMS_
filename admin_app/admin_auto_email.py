from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from visitors_app.models import user, roles, appointment, auto_email
from visitors_app.context_processors import my_constants
from visitors_app.views import date_time

def auto_email_view(request):
    constants = my_constants(request)
    
    username = request.session.get('admin')
    if not username:
        return redirect('admin')

    user_data = constants.get('admin_data', {})
    email = username['user_email']
    user_name = username['user_name']

    # Initialize admin_auto_email
    try:
        admin_auto_email = auto_email.objects.get(id=1)
    except ObjectDoesNotExist:
        admin_auto_email = None  # Handle if no email is configured yet

    if request.method == "POST":
        autoemail = request.POST.get('email')
        
        if autoemail:
            try:
                if admin_auto_email:
                    # Update the existing auto_email object
                    admin_auto_email.email = autoemail
                    admin_auto_email.updated_at = date_time()
                    admin_auto_email.save()
                    messages.success(request, "Successfully Updated", extra_tags="success")
                else:
                    # Create a new auto_email object if it doesn't exist
                    admin_auto_email = auto_email.objects.create(email=autoemail, created_at=date_time())
                    messages.success(request, "Successfully Created", extra_tags="success")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}", extra_tags="danger")
        else:
            messages.error(request, "Email is required.", extra_tags="danger")

    return render(request, 'dashboard/admin_dashboard/admin_auto_email/auto_email.html', {'admin_auto_email': admin_auto_email})
