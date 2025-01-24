from django.contrib import admin
from .models import user,appointment,roles,countries,states,cities,location,areas,company,department,appointment_reject,visitors_log,auto_email,gate_pass_no,designation,website_setting,safety_training
# Register your models here.
@admin.register(user)
class user(admin.ModelAdmin):
    list_display = ['id', 'first_name','last_name', 'email', 'password', 'mobile', 'gender','company_id','department_id','designation_id','location_id','address', 'is_active','uni_id','created_by','employee_code', 'created_at', 'updated_at','type','image','document','is_safety_training']


 
@admin.register(appointment)
class appointment(admin.ModelAdmin):
    list_display = ['id', 'visitors_id','employee_id', 'date', 'time','purpose','visitors_timing', 'visitors_type','detail','status','employee_approval','check_in_time','check_out_time','created_by', 'created_at', 'updated_at']

@admin.register(roles)
class roles(admin.ModelAdmin):
    list_display = ['id', 'name']
    
    

@admin.register(countries)
class rocountriesles(admin.ModelAdmin):
    list_display = ['id', 'shortname','name','phonecode']
    
@admin.register(states)
class states(admin.ModelAdmin):
    list_display = ['id','name','country_id']
    

@admin.register(cities)
class cities(admin.ModelAdmin):
    list_display = ['id','name','state_id']

@admin.register(location)
class location(admin.ModelAdmin):
    list_display = ['id','country_id','state_id','city_id','location_name','status','created_at']
    


@admin.register(areas)
class areas(admin.ModelAdmin):
    list_display = ['id','area_code','area_name','location_id','created_at']
    
    
@admin.register(company)
class company(admin.ModelAdmin):
    list_display = ['id','company_code','company_name','location_id','address_1','address_2','pincode','status','created_at']
    
    
@admin.register(department)
class department(admin.ModelAdmin):
    list_display = ['id','department_name','department_code','department_color_code','company_id','location_id','created_at','updated_at']
    
    
@admin.register(appointment_reject)
class appointment_reject(admin.ModelAdmin):
    list_display = ['id','appointment_id','reason','date','time','created_at','updated_at']
    

@admin.register(visitors_log)
class visitors_log(admin.ModelAdmin):
    list_display = ['id','appointment_id','start_time','stop_time','created_at','updated_at']
    
@admin.register(auto_email)
class auto_email(admin.ModelAdmin):
    list_display = ['id','email','created_at','updated_at']
    
    
@admin.register(gate_pass_no)
class gate_pass_no(admin.ModelAdmin):
    list_display = ['id','appointment_id','gate_pass_number','created_at','updated_at']

@admin.register(designation)
class designation(admin.ModelAdmin):
    list_display = ['id','name','allow_check_in','created_at','updated_at']
    
@admin.register(website_setting)
class website_setting(admin.ModelAdmin):
    list_display = ['id','image','favicon','website_name','website_link','copyright','smtp_host','smtp_user','smtp_password','from_name','from_email','whatsapp_notification','created_at','updated_at']
    
    

@admin.register(safety_training)
class safety_training(admin.ModelAdmin):
    list_display = ['id','title','video_file','is_active','created_at','updated_at']