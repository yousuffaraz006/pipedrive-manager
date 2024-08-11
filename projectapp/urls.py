from django.urls import path
from .views import *

urlpatterns = [
    path('logout/', logoutUser, name='logoutpage'),
    path('login/', loginUser, name='loginpage'),
    path('signup/', signupUser, name='signuppage'),
    path('sendmail/', sendmailUser, name='sendmailpage'),
    path('verify/<auth_token>', verify, name="verify"),
    path('error/', errorUser, name="errorpage"),
    path('', home, name='homepage'),
    path('contacts/', allcontacts, name='contactspage'),
    path('deals/', alldeals, name='dealspage'),
    path('forms/<str:form_pk>/', forms, name='formspage'),
]