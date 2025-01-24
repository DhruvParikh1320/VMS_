from django.urls import path
from . import views

urlpatterns = [
    
    ####  dashboard  ###### 
    path('employee',views.employee,name='employee'),
    path('employee/logout',views.employee_logout ,name='employee_logout'),
    path('employee/profile/edit',views.employee_edit ,name='employee_edit'),
    path('employee/dashboard',views.employee_dashboard,name='employee_dashboard'),
    path('employee/visitor/approve_reject',views.employee_visitore_approve_reject,name='employee_visitore_approve_reject'),
    path('employee/visitor_send_invitations',views.employee_visitore_send_invitations,name='employee_visitore_send_invitations'),
    path('employee/visitor/all_page',views.employee_visitore_all_page,name='employee_visitore_all_page'),
    path('employee/visitor/ajax_page_ajax',views.employee_visitore_ajax_page_ajax,name='employee_visitore_ajax_page_ajax'),
     
     
    path('employee/user',views.employee_user,name='employee_user'),
    path('employee/user_page_ajax',views.employee_page_ajax,name='employee_user_page_ajax'),
    path('employee/user/new_appointment/<int:id>/',views.employee_new_appointment,name='employee_user_new_appointment'),
]