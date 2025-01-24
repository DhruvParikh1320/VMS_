from django.urls import path
from . import views,visitor_verification,gate_keeper_visitor_add,gate_keeper_user

urlpatterns = [
    path('gate_keeper',views.gate_keeper,name='gate_keeper'),
    path('gate_keeper/logout',views.gate_keepe_logout ,name='gate_keepe_logout'),
    path('gate_keeper/dashboard',views.gate_keeper_dashboard,name='gate_keeper_dashboard'),
    path('gate_keeper/visitor',visitor_verification.gate_keeper_visitor_verification,name='gate_keeper_visitor_verification'),
    path('gate_keeper/visitor_page_ajax',visitor_verification.gate_keeper_visitor_verification_page_ajax,name='gate_keeper_visitor_verification_page_ajax'),
    path('gate_keeper/start/<int:id>/', visitor_verification.gate_keeper_start_time, name='gate_keeper_start_time'),
    path('gate_keeper/stop/<int:id>/', visitor_verification.gate_keeper_stop_time, name='gate_keeper_stop_time'),
    path('gate_keeper/print_gate_pass/<int:id>/', visitor_verification.gate_keeper_print_gate_pass, name='gate_keeper_print_gate_pass'),
    
    path('gate_keeper/visitor/add',gate_keeper_visitor_add.gate_keeper_visitor_add,name='gate_keeper_visitor_add'),
    path('gate_keeper/visitor/ajax_load_employee',gate_keeper_visitor_add.gate_keeper_ajax_load_employee,name='gate_keeper_ajax_load_employee'),
    path('gate_keeper/visitor/edit/<int:id>',gate_keeper_visitor_add.gate_keeper_visitor_edit,name='gate_keeper_visitor_edit'),
    path('accept/<str:encrypted_appointment_id>', gate_keeper_visitor_add.accept_appointment, name='accept_appointment'),
    path('reject/<str:encrypted_appointment_id>', gate_keeper_visitor_add.reject_appointment, name='reject_appointment'),
    path('gate_keeper/profile/edit',views.gate_keeper_edit ,name='gate_keeper_edit'),
    
    path('gate_keeper/user',gate_keeper_user.gate_keeper_user,name='gate_keeper_user'),
    path('gate_keeper/user_page_ajax',gate_keeper_user.gate_keeper_user_page_ajax,name='gate_keeper_user_page_ajax'),
    path('gate_keeper/user/new_appointment/<int:id>/',gate_keeper_user.gate_keeper_user_new_appointment,name='gate_keeper_user_new_appointment'),
    
    
    
    path('capture_photo/', views.capture_photo, name='capture_photo'),
    
    
    path('get-user-data/', views.get_user_data, name='get_user_data'),
    path('autocomplete-mobile-numbers/', views.autocomplete_mobile_numbers, name='autocomplete_mobile_numbers'),
    path('autocomplete-emails/',views.autocomplete_emails,name="autocomplete_emails"),
    path('get-user-data-by-email/', views.get_user_data_by_email, name='get_user_data_by_email'),
    # Add other URL patterns here
    
    
    path('visitor_details/<int:id>/', views.visitor_details, name='visitor_details'),
]

