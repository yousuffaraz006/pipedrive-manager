from django.contrib import admin
from .models import *

class EmailVerifyTime(admin.ModelAdmin):
    readonly_fields = ('created_at',)

class FormTime(admin.ModelAdmin):
    readonly_fields = ('created_at',)

admin.site.register(EmailVerification, EmailVerifyTime)
admin.site.register(Form, FormTime)
admin.site.register(Company)
admin.site.register(Contact)
admin.site.register(Deal)
admin.site.register(Post_Data)