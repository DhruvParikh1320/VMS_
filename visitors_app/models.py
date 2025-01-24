from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from visitor_management.settings import ADMIN_STATIC_PATH
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class user(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=599, null=True, default=None)
    mobile = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    address = models.TextField()
    is_active = models.BooleanField(default=1)
    confirmed = models.BooleanField(default=0)
    type = models.CharField(max_length=200)
    uni_id = models.CharField(max_length=200)
    image = models.ImageField(upload_to='user')
    company_id = models.IntegerField()
    department_id = models.IntegerField()
    designation_id = models.IntegerField()
    location_id = models.IntegerField()
    created_by = models.IntegerField()
    employee_code = models.IntegerField()
    created_at = models.CharField(max_length=200)
    updated_at = models.CharField(max_length=200)
    document  = models.FileField(upload_to='user/document',null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set_permissions', blank=True)
    is_safety_training = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'mobile', 'gender', 'dob', 'address', 'website', 'brief']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    def save(self, *args, **kwargs):
        if self.image:
            filename = self.image.name.split('/')[-1]
            self.image.name = filename
        if self.document:
            # Example of modifying document name (if needed)
            document_filename = self.document.name.split('/')[-1]
            self.document.name = document_filename
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "User"
        db_table = "users"

class appointment(models.Model):
    visitors_id = models.IntegerField()
    employee_id = models.IntegerField()
    date = models.CharField(max_length=200)
    time = models.CharField(max_length=200)
    visitors_type = models.CharField(max_length=200,null=True, blank=True)
    detail  = models.TextField(null=True, blank=True)
    purpose = models.TextField()
    visitors_timing = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    employee_approval = models.CharField(max_length=200,null=True)
    check_in_time  = models.CharField(max_length=200)
    check_out_time  = models.CharField(max_length=200)
    created_by = models.IntegerField()
    created_at = models.CharField(max_length=200)
    updated_at = models.CharField(max_length=200)
    class Meta:
        verbose_name = "Appointment"
        db_table = "appointment"

class roles(models.Model):
    name = models.CharField(max_length=200)
    class Meta:
        verbose_name = "roles"
        db_table = "roles"

class countries(models.Model):
    shortname = models.CharField(max_length=3)
    name = models.CharField(max_length=150)
    phonecode = models.IntegerField()
    
    class Meta:
        verbose_name = "countries"
        db_table = "countries"


class states(models.Model):
    name = models.CharField(max_length=30)
    country_id = models.IntegerField()
    
    class Meta:
        verbose_name = "states"
        db_table = "states"


class cities(models.Model):
    name = models.CharField(max_length=30)
    state_id = models.IntegerField()
    
    class Meta:
        verbose_name = "cities"
        db_table = "cities"
    

class location(models.Model):
    country_id = models.IntegerField()
    state_id = models.IntegerField()
    city_id = models.IntegerField()
    location_name = models.CharField(max_length=200)
    status = models.IntegerField()
    created_at = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = "location"
        db_table = "location"

class areas(models.Model):
    area_code = models.CharField(max_length=10)
    area_name = models.CharField(max_length=100)
    location_id = models.IntegerField()
    created_at = models.CharField(max_length=200)
    class Meta:
        verbose_name = "areas"
        db_table = "areas"

class company(models.Model):
    company_code = models.CharField(max_length=599)
    company_name = models.CharField(max_length=100)
    location_id = models.IntegerField()
    address_1 = models.TextField()
    address_2 = models.TextField()
    pincode = models.CharField(max_length=15)
    status =  models.IntegerField()
    created_at = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = "company"
        db_table = "company"
        
        
class department(models.Model):
    department_name = models.CharField(max_length=255)
    department_code = models.CharField(max_length=50)
    department_color_code = models.CharField(max_length=50)
    company_id = models.IntegerField()
    location_id = models.IntegerField()
    created_at = models.CharField(max_length=200)
    updated_at = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = "department"
        db_table = "department"
        

class appointment_reject(models.Model):
    appointment_id = models.IntegerField()
    reason = models.CharField(max_length=999)
    date = models.CharField(max_length=200)
    time = models.CharField(max_length=200)
    created_at = models.CharField(max_length=200)
    updated_at = models.CharField(max_length=200) 
    class Meta:
        verbose_name = "appointment_reject"
        db_table = "appointment_reject"

class visitors_log(models.Model):
    appointment_id = models.IntegerField()
    start_time  = models.CharField(max_length=200)
    stop_time  = models.CharField(max_length=200)
    created_at = models.CharField(max_length=200)
    updated_at = models.CharField(max_length=200)
    class Meta:
        verbose_name = "visitors_log"
        db_table = "visitors_log"
class auto_email(models.Model):
    email = models.TextField()
    created_at = models.CharField(max_length=200)
    updated_at = models.CharField(max_length=200)
    class Meta:
        verbose_name = "auto_email"
        db_table = "auto_email"

class gate_pass_no(models.Model):
    appointment_id = models.IntegerField()
    gate_pass_number = models.IntegerField()
    created_at = models.CharField(max_length=200)
    updated_at = models.CharField(max_length=200)
    class Meta:
        verbose_name = "gate_pass_no"
        db_table = "gate_pass_no"
        
        
class designation(models.Model):
    name = models.CharField(max_length=200)
    allow_check_in = models.BooleanField()
    created_at = models.CharField(max_length=200)
    updated_at = models.CharField(max_length=200)
    class Meta:
        verbose_name = "designation"
        db_table = "designation"
        
        
class website_setting(models.Model):
    image = models.ImageField(upload_to='static/website_setting/logo')
    favicon = models.ImageField(upload_to='static/website_setting/favicon')
    website_name = models.CharField(max_length=200) 
    website_link = models.CharField(max_length=200)
    copyright = models.CharField(max_length=999)
    smtp_host = models.CharField(max_length=200)
    smtp_user = models.CharField(max_length=200)
    smtp_password = models.CharField(max_length=200) 
    from_name = models.CharField(max_length=200)
    from_email = models.CharField(max_length=200)
    whatsapp_notification = models.BooleanField()
    created_at = models.CharField(max_length=200)
    updated_at = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if self.image:
            filename = self.image.name.split('/')[-1]
            self.image.name = filename
        if self.favicon:
            favicon_filename = self.favicon.name.split('/')[-1]
            self.favicon.name = favicon_filename
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "website_setting"
        db_table = "website_setting"

class safety_training(models.Model):
    title = models.CharField(max_length=100)
    video_file  = models.FileField(upload_to='safety_training')
    is_active = models.BooleanField()
    created_at = models.CharField(max_length=200)
    updated_at = models.CharField(max_length=200)
    def save(self, *args, **kwargs):
        if self.video_file:
            filename = self.video_file.name.split('/')[-1]
            self.video_file.name = filename
        super().save(*args, **kwargs)
            
    class Meta: 
        verbose_name = "safety_training"
        db_table = "safety_training"
