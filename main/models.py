from django.db import models
import re

class UserManager(models.Manager):
    def login_validator(self, post_data):
        errors = {}
        # EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@+mail+\.+mil+$')
        # if not EMAIL_REGEX.match(post_data['military_email']):
        #     errors['email'] = 'Invalid email address. Please use @mail.mil address.'
        if len(post_data['password']) < 8:
            errors['password_length'] = 'Password must be at least 8 characters.'
        return errors
    def registration_validator(self, post_data):
        errors = {}
        if len(post_data['last_name']) < 1 or len(post_data['first_name']) < 1 or len(post_data['middle']) < 1 or len(post_data['rank']) < 1 or len(post_data['military_email']) < 1 or len(post_data['password']) < 1 or len(post_data['confirm_pw']) < 1 or len(post_data['leadership']) < 1:
            errors['required'] = 'Required Fields are: Last Name, First Name, Middle Initial, Rank, Military Email, Password, Confirmation Password, and Leadership Type'
        if post_data['password'] != post_data['confirm_pw']:
            errors['match'] = 'Password and confirmation do not match. Please try again'
        return errors
    def password_reset_validator(self, post_data):
        errors = {}
        if post_data['new_password'] != post_data['confirm_pw']:
            errors['match'] = 'Password and confirmation do not match. Please try again'
        return errors 

class FormManager(models.Manager):
    def form_validator(self, post_data):
        errors = {}
        PHONE_REGEX = re.compile(r'^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$')
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(post_data['civilian_email']):
            errors['email'] = 'Invalid email address'
        if not PHONE_REGEX.match(post_data['phone_number']):
            errors['number'] = 'Please enter a valid phone number'
        if len(post_data['location']) < 1 or len(post_data['phone_number']) < 1 or len(post_data['address']) < 1 or len(post_data['city']) < 1 or len(post_data['state']) < 1 or len(post_data['zipcode']) < 1 or len(post_data['civilian_email']) < 1 or len(post_data['unit_origin']) < 1 or len(post_data['unit_destination']) < 1 or len(post_data['plans_after']) < 1 or len(post_data['military_schools']) < 1 or len(post_data['civilian_school']) < 1 or len(post_data['credits']) < 1 or len(post_data['major']) < 1 or len(post_data['employer']) < 1:
            errors['required'] = 'All fields are required'
        if len(post_data['zipcode']) < 5:
            errors['zipcode'] = 'Zip code must be at least 5 digits'
        return errors
class AttributeManager(models.Manager):
    def alerts_validator(self, attribute_type, form_value):
            errors = {}
            attribute_type = AttributeType.objects.filter(id = attribute_type.id)
            this_attribute_type = attribute_type[0]
            this_attribute = Attribute.objects.filter(attribute_type = this_attribute_type)
            for attribute in this_attribute:
                if attribute.value in ['y', 'Y', 'n', 'N', 'p', 'P', 'f', 'F', 'Pass', 'Fail', 'Yes', 'No'] and form_value in ['Dateforward', 'Dateback']:
                    errors['alert'] = 'Field is not a date field'
                    return errors
            return errors

class AttributeManager(models.Manager):
    def alerts_validator(self, attribute_type, form_value):
            errors = {}
            attribute_type = AttributeType.objects.filter(id = attribute_type.id)
            this_attribute_type = attribute_type[0]
            this_attribute = Attribute.objects.filter(attribute_type = this_attribute_type)
            for attribute in this_attribute:
                if attribute.value in ['y', 'Y', 'n', 'N', 'p', 'P', 'f', 'F', 'Pass', 'Fail', 'Yes', 'No'] and form_value in ['Dateforward', 'Dateback']:
                    errors['alert'] = 'Field is not a date field'
                    return errors
            return errors
    
class User(models.Model):
    last_name = models.CharField(max_length = 255)
    first_name = models.CharField(max_length = 255)
    middle_initial = models.CharField(max_length = 1)
    rank = models.CharField(max_length = 255)
    military_email = models.CharField(max_length = 255)
    password = models.CharField(max_length = 255)
    leadership_type = models.CharField(max_length = 255)
    hq = models.IntegerField(default = 1)
    platoon = models.CharField(max_length = 255, blank=True, null=True)
    squad = models.CharField(max_length = 255, blank=True, null=True)
    team = models.CharField(max_length = 255, blank=True, null=True)
    active = models.BooleanField()
    objects = UserManager()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)


class AttributeType(models.Model):
    display_name = models.CharField(max_length = 255, blank=True, null=True)
    type = models.CharField(max_length = 255, blank=True, null=True)
    alert_type = models.CharField(max_length = 255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = AttributeManager()

class Attribute(models.Model):
    name = models.CharField(max_length = 255, blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    attribute_type = models.ForeignKey(AttributeType, related_name = "attribute", on_delete = models.CASCADE)
    alert_or_warning = models.CharField(max_length = 20, blank = True, null = True)
    user = models.ForeignKey(User, related_name = 'attributes', on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = AttributeManager()


class InputData(models.Model):
    location = models.CharField(max_length = 255, blank=True, null=True)
    phone_number = models.CharField(max_length = 255, blank=True, null=True)
    address = models.CharField(max_length = 255, blank=True, null=True)
    city = models.CharField(max_length = 255, blank=True, null=True)
    state = models.CharField(max_length = 2, blank=True, null=True)
    zipcode = models.CharField(max_length = 5, blank=True, null=True)
    civilian_email = models.CharField(max_length = 255, blank=True, null=True)
    unit_origin = models.CharField(max_length = 255, blank=True, null=True)
    unit_destination = models.CharField(max_length = 255, blank=True, null=True)
    plans_after = models.TextField(blank=True, null=True)
    military_schools = models.TextField(blank=True, null=True)
    civilian_school = models.CharField(max_length = 255, blank=True, null=True)
    num_credits = models.IntegerField(blank=True, null=True)
    major = models.CharField(max_length = 255, blank=True, null=True)
    employer = models.CharField(max_length = 255, blank=True, null=True)
    user = models.ForeignKey(User, related_name = 'additional_info', on_delete = models.CASCADE)
    objects = FormManager()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
