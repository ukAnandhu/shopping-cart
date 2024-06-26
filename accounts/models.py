from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,AbstractUser, PermissionsMixin

class MyAccountManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User have an username')
        user = self.model(
            email = self.normalize_email(email),  #makes small letter
            username = username,
            first_name = first_name,
            last_name = last_name
        )
        user.set_password(password) #for password
        user.save(using=self._db)
        return user
    #superuser
    def create_superuser(self,first_name,last_name,email,username,password):
        user = self.create_user(
            email = self.normalize_email(email),  #makes small letter
            username = username,
            password=password,
            first_name = first_name,
            last_name = last_name
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True

        user.save(using =self._db)
        return user
class Account(AbstractBaseUser,PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100,unique=True)
    email = models.CharField(max_length=100,unique=True)
    phn = models.CharField(max_length=100)

    #required always
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    pass

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']
    objects = MyAccountManager()
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    def __str__(self):
        return self.email
    def has_perm(self,perm,obj=None):
        return self.is_admin 

    def has_module_perms(self,add_label):
        return True

class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)  #one to one - unique
    address = models.CharField(blank=True, max_length=100)
    profile_picture = models.ImageField(blank=True,null=True, upload_to='userprofile/')
    city = models.CharField(blank=True, max_length=20)
    state = models.CharField(blank=True, max_length=20)

    def __str__(self): 
        return self.user.first_name

