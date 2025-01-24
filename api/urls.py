from django.urls import path,include
from . import views
from .api_signin import  UsersigninView
from .api_forgot_password import Userforgot_passwordView
from .api_user_profile import user_profileView,profile_updateView
from .api_visitore import visitore_listingView,status_changesView,visitore_detailView
from .dashboard import dashboard,dashboard_pending
urlpatterns = [
    path('signin', UsersigninView.as_view(), name='signin'), 
    path('forgot_password', Userforgot_passwordView.as_view(), name='forgot_password'),
    path('user_profile', user_profileView.as_view(), name='user_profile'),
    path('profile_update', profile_updateView.as_view(), name='profile_update'),
    path('visitore_listing', visitore_listingView.as_view(), name='visitore_listing'),
    path('status_changes',status_changesView.as_view(), name='status_changes'),
    path('visitore_detail',visitore_detailView.as_view(), name='visitore_detail'),
    path('send_checkouts_email', views.api_send_email_View.as_view(), name='send_checkouts_email'),
    path('visitor_type',views.visitor_type.as_view(), name='visitor_type'),
    path('employee',views.employee.as_view(), name='employee'),
    path('employee_data',views.employee_data.as_view(), name='employee_data'),
    path('new_appointment',views.new_appointment.as_view(), name='new_appointment'),
    path('all_visitor',views.all_visitor.as_view(), name='all_visitor'),
    path('dashboard',dashboard.as_view(), name='dashboard'),
    path('dashboard/visitor_requests',dashboard_pending.as_view(), name='dashboard_pending')
    
]
