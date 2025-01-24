from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from . import visitors_profile
from . import visitors_appointment

urlpatterns = [
    path('', views.home, name='home'),
    path('register/<str:encrypted_appointment_id>', views.register, name='register'),
    path('visitors',views.visitors,name='visitors'),
    path('visitors/sign_up',views.visitors_sign_up,name='visitors_sign_up'),
    path('visitors/dashboard',views.visitors_dashboard,name='visitors_dashboard'),
    path('visitors/profile/edit',visitors_profile.visitors_edit ,name='visitors_edit'),
    path('visitors/logout',views.visitors_logout ,name='visitors_logout'),
    path('visitors/appointment',visitors_appointment.visitors_appointment ,name='visitors_appointment'),
    path('visitors/appointment_page_ajax',visitors_appointment.appointment_page_ajax ,name='appointment_page_ajax'),
    path('visitors/upcoming_appointment_page_ajax',visitors_appointment.upcoming_appointment_page_ajax ,name='upcoming_appointment_page_ajax'),
    path('visitors/appointment/add',visitors_appointment.visitors_appointment_add ,name='visitors_appointment_add'),
    path('visitors/appointment/edit/<int:id>',visitors_appointment.visitors_appointment_edit ,name='visitors_appointment_edit'),
    path('visitors/appointment/delete/<int:id>',visitors_appointment.visitors_appointment_delete ,name='visitors_appointment_delete'),
    path('visitors/appointment/upcoming_appointment',visitors_appointment.visitors_appointment_upcoming_appointment ,name='visitors_appointment_upcoming_appointment'),
    path('visitors/safety_training',views.visitors_safety_training,name='visitors_safety_training'),
    path('Self-Service_Kiosk',views.visitors_self_safety_training,name='visitors_self_safety_training'),
    path('update-safety-training-status/', views.update_safety_training_status, name='update_safety_training_status'),
    path('visitors/appointment_reject',views.visitors_appointment_reject,name='visitors_appointment_reject'),
# dashboard_all_users_pages_ajax
# admin_layout.html
    path('',include('gate_keeper_app.urls')),
    path('',include('employee_app.urls')),
    path('',include('admin_app.urls')),
    path('api/',include('api.urls'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



