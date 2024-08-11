from django.db import models
from django.contrib.auth.models import User

class EmailVerification(models.Model):
    user = models.CharField(max_length=30)
    auth_token = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user
    
class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=100, null=True, blank=True)
    apitoken = models.CharField(max_length=200, null=True, blank=True)
    baseurl = models.CharField(max_length=100, null=True, blank=True)
    userid = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.user)

class Form(models.Model):
    reciever = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    deal = models.TextField(max_length=200, null=True, blank=True)
    note = models.TextField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.reciever)
    
class Contact(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.owner)
    
class Deal(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=True, blank=True)
    person = models.CharField(max_length=50, null=True, blank=True)
    value = models.IntegerField(default=1000, null=True, blank=True)

    def __str__(self):
        return str(self.owner)