from django.urls import path
from . import views,admin_role,admin_location,admin_area,admin_company,admin_department,admin_user,admin_report,admin_visitor,admin_auto_email,admin_designation,admin_setting,admin_safety_training
urlpatterns = [
    
    ####  dashboard  ###### 
    path('admin',views.admin,name='admin'),
    path('admin/logout',views.admin_logout ,name='admin_logout'),
    path('admin/profile/edit',views.admin_edit ,name='admin_edit'),
    path('admin/dashboard',views.admin_dashboard,name='admin_dashboard'),
    
    ###  role ####
    path('admin/role/add',admin_role.admin_role_add,name='admin_role_add'),
    path('admin/role',admin_role.admin_role_all,name='admin_role_all'),
    path('admin/role/delete/<int:id>',admin_role.admin_role_delete ,name='admin_role_delete'),
    path('admin/role/edit/<int:id>',admin_role.admin_role_edit ,name='admin_role_edit'),
    
    ##   location ###
    
    path('admin/location/add',admin_location.admin_location_add,name='admin_location_add'),
    path('admin/location/ajax_load_states',admin_location.admin_location_ajax_load_states,name='admin_location_ajax_load_states'),
    path('admin/location/ajax_load_cities',admin_location.admin_location_ajax_load_cities,name='admin_location_ajax_load_cities'),
    path('admin/location',admin_location.admin_location,name='admin_location'),
    path('admin/location/ajax_page_ajax',admin_location.admin_location_ajax_page_ajax,name='admin_location_ajax_page_ajax'),
    path('admin/location/delete/<int:id>',admin_location.admin_location_delete ,name='admin_location_delete'),
    path('admin/location/edit/<int:id>',admin_location.admin_location_edit ,name='admin_location_edit'),
    
    
    ###  area ###
    
    path('admin/area/add',admin_area.admin_area_add,name='admin_area_add'),
    path('admin/area',admin_area.admin_area,name='admin_area'),
    path('admin/area/ajax_page_ajax',admin_area.admin_area_ajax_page_ajax,name='admin_area_ajax_page_ajax'),
    path('admin/area/delete/<int:id>',admin_area.admin_area_delete ,name='admin_area_delete'),
    path('admin/area/edit/<int:id>',admin_area.admin_area_edit ,name='admin_area_edit'),
    ### company ###
    
    path('admin/company/add',admin_company.admin_company_add,name='admin_company_add'),
    path('admin/company',admin_company.admin_company,name='admin_company'),
    path('admin/company/ajax_page_ajax',admin_company.admin_company_ajax_page_ajax,name='admin_company_ajax_page_ajax'),
    path('admin/company/delete/<int:id>',admin_company.admin_company_delete ,name='admin_company_delete'),
    path('admin/company/edit/<int:id>', admin_company.admin_company_edit, name='admin_company_edit'),
    
    ### Department ##
    
    path('admin/department/add',admin_department.admin_department_add,name='admin_department_add'),
    path('admin/department',admin_department.admin_department,name='admin_department'),
    path('admin/department/ajax_page_ajax',admin_department.admin_department_ajax_page_ajax,name='admin_department_ajax_page_ajax'),
    path('admin/department/delete/<int:id>',admin_department.admin_department_delete ,name='admin_department_delete'),
    path('admin/department/edit/<int:id>', admin_department.admin_department_edit, name='admin_department_edit'),
    
     ### Designation ###

    path('admin/designation/add',admin_designation.admin_designation_add,name='admin_designation_add'),
    path('admin/designation',admin_designation.admin_designation,name='admin_designation'),
    path('admin/designation/ajax_page_ajax',admin_designation.admin_designation_ajax_page_ajax,name='admin_designation_ajax_page_ajax'),
    path('admin/designation/delete/<int:id>',admin_designation.admin_designation_delete ,name='admin_designation_delete'),
    path('admin/designation/edit/<int:id>', admin_designation.admin_designation_edit, name='admin_designation_edit'),
    
    
    ## admin_setting ##
    # path('admin/setting/add',admin_setting.admin_setting_add,name='admin_setting_add'),
    path('admin/setting/update',admin_setting.admin_setting_update,name='admin_setting_update'),


    ### user ### 
    path('admin/user/add',admin_user.admin_user_add,name='admin_user_add'),
    path('admin/user',admin_user.admin_user,name='admin_user'),
    path('admin/user/ajax_page_ajax',admin_user.admin_user_ajax_page_ajax,name='admin_user_ajax_page_ajax'),
    path('admin/user/edit/<int:id>', admin_user.admin_user_edit, name='admin_user_edit'),
    path('admin/user/delete/<int:id>',admin_user.admin_user_delete ,name='admin_user_delete'),
    # Add other URL patterns here
        
    ###### report #######
    path('admin/report',admin_report.admin_report,name='admin_report'),
    
    
    ##### visitor ######
    path('admin/visitor',admin_visitor.admin_visitor,name='admin_visitor'),
    path('admin/visitor_page_ajax',admin_visitor.admin_visitor_verification_page_ajax,name='admin_visitor_verification_page_ajax'),
    path('admin/visitor/user',admin_visitor.admin_visitor_user,name='admin_visitor_user'),
    path('admin/visitor_user_page_ajax',admin_visitor.admin_visitor_user_page_ajax,name='admin_visitor_user_page_ajax'),
    path('admin/update_user_status/', admin_visitor.admin_update_user_status, name='admin_update_user_status'),
    path('admin/start/<int:id>/', admin_visitor.admin_start_time, name='admin_start_time'),
    path('admin/stop/<int:id>/', admin_visitor.admin_stop_time, name='admin_stop_time'),
    path('admin/print_gate_pass/<int:id>/', admin_visitor.admin_print_gate_pass, name='admin_print_gate_pass'),
    
    
    path('admin/auto_email',admin_auto_email.auto_email_view,name='auto_email'),
    
    
    ### admin_safety_training ####
    path('admin/safety_training/add',admin_safety_training.admin_safety_training_add,name='admin_safety_training_add'),
    path('admin/safety_training',admin_safety_training.admin_safety_training,name='admin_safety_training'),
    path('admin/safety_training/ajax_page_ajax',admin_safety_training.admin_safety_training_ajax_page_ajax,name='admin_safety_training_ajax_page_ajax'),
    path('admin/safety_training/delete/<int:id>',admin_safety_training.admin_safety_training_delete ,name='admin_safety_training_delete'),
    path('admin/safety_training/edit/<int:id>', admin_safety_training.admin_safety_training_edit, name='admin_safety_training_edit'),
]