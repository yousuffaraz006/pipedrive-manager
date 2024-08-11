from .models import *
import uuid

def create_company(backend, user, response, *args, **kwargs):
    if not Company.objects.filter(user=user).exists():
        url_token = str(uuid.uuid4())
        Company.objects.create(user=user, url=url_token)
        emailverifyform = EmailVerification.objects.filter(user=user.email).first()
        if emailverifyform:
            emailverifyform.delete()
        else:
            print('Not Found')