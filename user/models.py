from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, editor=False, admin=False):
        if not email:
            raise ValueError("Please enter an email address.")
        if not password:
            raise ValueError("Please enter a password.")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.name = name
        user.editor = editor
        user.admin = admin
        user.save(using=self._db)
        return user

    def create_editor(self, email, name, password=None):
        user = self.create_user(email, name, password=password, editor=True, admin=False)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password=password, editor=True, admin=True)
        return user

    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    email_confirmed = models.BooleanField(default=False)
    name = models.CharField(max_length=100, default='')
    password = models.CharField(max_length=500, default='')
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=500, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.name

    @property
    def get_name(self):
        return self.name

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
