from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from apicompany.settings import DEBUG
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings as conf_settings
from django.urls import reverse
from .models import *
from .forms import *
import requests
import json
import uuid

def sendmailUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user_obj = User.objects.filter(username=username).first()
        if not user_obj:
            auth_token = str(uuid.uuid4())
            profile_obj = EmailVerification.objects.create(user=username, auth_token=auth_token)
            profile_obj.save()
            send_mail_after_registration(username, auth_token)
            messages.info(request, 'Email has been sent to your mail address. Please verify your account to proceed.')
            return redirect('sendmailpage')
        else:
            messages.info(request, 'User already exists.')
            return redirect('sendmailpage')
    return render(request, 'projectapp/sendmailpage.html')

def signupUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_exist = User.objects.filter(username=username).first()
        if user_exist:
            messages.info(request, 'Username has already been taken.')
            return redirect('signuppage')
        elif password1 != password2:
            messages.info(request, 'Passwords did not match.')
            return redirect('signuppage')
        else:
            profile_obj = EmailVerification.objects.filter(user=username).first()
            if profile_obj:
                if profile_obj.is_verified:
                    user_obj = User.objects.create_user(username, first_name=firstname, last_name=lastname, password=password1)
                    url_token = str(uuid.uuid4())
                    company_obj = Company.objects.create(user=user_obj, url=url_token)
                    company_obj.save()
                    emailverifyform = EmailVerification.objects.filter(user=username).first()
                    emailverifyform.delete()
                    user = authenticate(username=username, password=password1)
                    login(request, user)
                    return redirect('homepage')
                else:
                    auth_token = str(uuid.uuid4())
                    profile_obj.auth_token = auth_token
                    profile_obj.save()
                    email_obj = User.objects.get(username=username).username
                    send_mail_after_registration(email_obj, auth_token)
                    messages.info(request, 'Your account is not verified. Please check your mailbox for "Account Verification" mail and click on the link to verify your account. We have sent a new "Account Verification" mail.')
            else:
                messages.info(request, 'You need to provide your mail address for account verification before you sign up.')
                return redirect('sendmailpage')
    return render(request, 'projectapp/signuppg.html')

def send_mail_after_registration(email, token):
    if DEBUG:
        link = '127.0.0.1:8000'
    else:
        link = 'https://yusuffrazofficial001.pythonanywhere.com/'
    subject = 'Account Verification'
    message = f'Hi {email}, please click on the link to verify your account on Desi Digilocker. {link}/verify/{token}'
    email_from = conf_settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

def verify(request, auth_token):
    try:
        profile_obj = EmailVerification.objects.filter(auth_token=auth_token).first()
        if profile_obj:
            if profile_obj.is_verified:
                messages.info(request, 'Your account is already verified.')
                return redirect('signuppage')
            else:
                print(auth_token)
                profile_obj.is_verified = True
                profile_obj.auth_token = ''
                profile_obj.save()
                messages.info(request, 'Your account has been verified.')
                return redirect('signuppage')
        else:
            return redirect('errorpage')
    except Exception as e:
        messages.info(request, e)
        return render(request, 'projectapp/signuppage.html')

def loginUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=username).first()
        if user_obj is None:
            messages.info(request, 'User not found.')
            return redirect('loginpage')
        else:
            emailverify_obj = EmailVerification.objects.filter(user=user_obj).first()
            user = authenticate(username=username, password=password)
            if user is None:
                messages.info(request, 'Please enter the credentials correctly.')
                return redirect('loginpage')
            else:
                if not emailverify_obj.is_verified:
                    auth_token = str(uuid.uuid4())
                    emailverify_obj.auth_token = auth_token
                    emailverify_obj.save()
                    email_obj = User.objects.get(username=username).username
                    send_mail_after_registration(email_obj, auth_token)
                    messages.info(request, 'Your account is not verified. Please check your mailbox for "Account Verification" mail and click on the link to verify your account. We have sent a new "Account Verification" mail.')
                    return redirect('loginpage')
                else:
                    login(request, user)
                    return redirect('homepage')                
    else:
        return render(request, 'projectapp/loginpg.html')

def logoutUser(request):
    logout(request)
    return redirect('loginpage')

def errorUser(request):
    return render(request, 'projectapp/errorpage.html')

@login_required(login_url="/login")
def home(request):
    company_instance = get_object_or_404(Company, user=request.user)
    company_obj = Company.objects.get(user=request.user)
    forms = Form.objects.filter(reciever=request.user).order_by('-created_at')
    if request.method == 'POST':
        tokenval = request.POST.get('apitoken')
        urlval = request.POST.get('baseurl')
        userval = request.POST.get('userid')
        form = CompanyForm(request.POST, instance=company_instance)
        form_vals = form.save(commit=False)
        form_vals.apitoken = tokenval
        form_vals.baseurl = urlval
        form_vals.userid = userval
        form_vals.save()
        return redirect('homepage')
    context = {'company_obj':company_obj, 'forms':forms}
    return render(request, 'projectapp/homepage.html', context)

def allcontacts(request):
    company_obj = Company.objects.get(user=request.user)
    tokenval = company_obj.apitoken
    urlval = company_obj.baseurl
    url = f'{urlval}persons?api_token={tokenval}'

    # Making the GET request
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        contacts = data.get('data', [])
        for contact in contacts:
            email = contact['email'][0]['value'] if contact['email'] else ''
            phone = contact['phone'][0]['value'] if contact['phone'] else ''
            contact_exist = Contact.objects.filter(email=email).first()
            if contact_exist:
                print('All Contacts Up to Date')
            else:
                Contact.objects.create(
                    owner = request.user,
                    name=contact['name'],
                    email=email,
                    phone=phone,
                )
    else:
        contacts = []
        print('Failed to search:', response.status_code, response.json())
    contactsvar = Contact.objects.filter(owner=request.user)

    contactsv = Contact.objects.filter(owner=request.user)
    if request.method == 'POST':
        contactsv.delete()
        return redirect('contactspage')
    context = {'contactsvar': contactsvar}
    return render(request, 'projectapp/contactspage.html', context)


def alldeals(request):
    company_obj = Company.objects.get(user=request.user)
    tokenval = company_obj.apitoken
    urlval = company_obj.baseurl
    url = f'{urlval}deals?api_token={tokenval}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        deals = data.get('data', [])
        for deal in deals:
            person = deal['person_id']['email'][0]['value'] if deal['person_id']['email'] else ''
            title = deal['title']
            deal_exist = Deal.objects.filter(person=person, title=title).first()
            if deal_exist:
                print('All Deals Up to Date')
            else:
                Deal.objects.create(
                    owner = request.user,
                    title=title,
                    value=deal['value'],
                    person=person,
                )
    else:
        deals = []
        print('Failed to search:', response.status_code, response.json())
    dealsvar = Deal.objects.filter(owner=request.user)

    dealsv = Deal.objects.filter(owner=request.user)
    if request.method == 'POST':
        dealsv.delete()
        return redirect('dealspage')
    context = {'dealsvar': dealsvar}
    return render(request, 'projectapp/dealspage.html', context)

def testpost(request):
    post_datas = Post_Data.objects.filter(reciever=request.user).order_by('-created_at')
    context = {'post_datas': post_datas}
    return render(request, 'projectapp/testpage.html', context)

@csrf_exempt
def forms(request, form_pk):
    company_obj = Company.objects.get(url=form_pk)
    company_id = company_obj.id
    form_pk_value = company_obj.url
    endurl = reverse('formspage', args=[form_pk_value])
    if DEBUG:
        link = '127.0.0.1:8000'
    else:
        link = 'https://yusuffrazofficial001.pythonanywhere.com'
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        deal = request.POST.get('deal')
        note = request.POST.get('note')
        try:
            form = DealCreationForm(request.POST)
            if form.is_valid:
                newform = form.save(commit=False)
                newform.name = name
                newform.email = email
                newform.deal = deal
                newform.note = note
                newform.reciever = company_obj.user
                newform.save()
                url = link + endurl
                post_data_string = ', '.join([f'{key}={value}' for key, value in request.POST.items()])
                Post_Data.objects.create(reciever=company_obj.user, url=url, data=post_data_string)
                person_results = search_or_create_person(company_id, name, email)
                if person_results['status'] == 'Person search & creation SUCCEEDED' or person_results['status'] == 'Person search SUCCEEDED':
                    person_id = person_results['person_id']
                    d_created = create_deal(company_id, deal, person_id)
                    if d_created['status'] == 'Deal creation SUCCEEDED':
                        if note:
                            deal_id = d_created['deal_id']
                            n_created = create_note(company_id, note, deal_id)
                            if n_created['status'] == 'Note creation SUCCEEDED':
                                messages.info(request, 'All Is Well')
                            else:
                                print(n_created['status'])
                        else:
                            messages.info(request, 'All Is Well')
        except Exception as e:
            print(e)
    context = {'company_obj':company_obj}
    return render(request, 'projectapp/formpage.html', context)

def hit_pipedrive_api(company_id, endpoint, method, body={}, query=''):
    companyForm = get_object_or_404(Company, id=company_id)
    apitoken = companyForm.apitoken
    apiurl = f'{companyForm.baseurl}{endpoint}?api_token={apitoken}'
    if query:
        apiurl += '&' + query
    headers = {
        'Content-Type': 'application/json'
    }
    bodyjson = json.dumps(body)

    response_method = getattr(requests, method)
    status = 'Hit Pipedrive FAIL'
    response = response_method(apiurl, headers=headers, data=bodyjson)
    
    data = {}
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        if data.get('success'):
            status = 'Hit Pipedrive SUCCESS'
    print(status)
    print(data)
    return {'status': status, 'data': data}

def search_person(company_id, email):
    status = 'Person not found'
    person_id = ''
    endpoint = 'persons/search'
    method = 'get'
    query = 'term=' + email
    src_person_results = hit_pipedrive_api(company_id, endpoint, method, {}, query)
    
    if src_person_results['data'] and src_person_results['data'].get('data') and src_person_results['data']['data'].get('items'):
        items = src_person_results['data']['data']['items']
        if items:
            person_id = items[0]['item']['id']
            status = 'Person found'
            print(person_id, status)
        else:
            print(status)
    else:
        print(status)
    return {'status': status, 'id': person_id}

def create_person(company_id, name, email):
    status = 'Person creation FAILED'
    person_id = ''
    endpoint = 'persons'
    method = 'post'
    body = {
        'name': name,
        'email': email
    }
    crt_person_results = hit_pipedrive_api(company_id, endpoint, method, body)
    
    if crt_person_results['data'] and crt_person_results['data'].get('data'):
        person_id = crt_person_results['data']['data']['id']
        status = 'Person creation SUCCEEDED'
        print(person_id, status)
    else:
        print(status)
    return {'status': status, 'id': person_id}

def create_deal(company_id, deal_title, deal_person):
    companyForm = Company.objects.get(id=company_id)
    deal_user = companyForm.userid
    status = 'Deal creation FAILED'
    deal_id = ''
    endpoint = 'deals'
    method = 'post'
    body = {
        'user_id': deal_user,
        'title': deal_title,
        'value': 10000,
        'person_id': deal_person
    }
    crt_deal_results = hit_pipedrive_api(company_id, endpoint, method, body)
    
    if crt_deal_results['data'] and crt_deal_results['data'].get('data'):
        deal_id = crt_deal_results['data']['data']['id']
        status = 'Deal creation SUCCEEDED'
        print(deal_id, status)
    else:
        print(status)
    return {'status': status, 'deal_id': deal_id}

def create_note(company_id, note, deal_id):
    status = 'Note creation FAILED'
    note_id = ''
    endpoint = 'notes'
    method = 'post'
    body = {
        'content': note,
        'deal_id': deal_id
    }
    crt_note_results = hit_pipedrive_api(company_id, endpoint, method, body)
    
    if crt_note_results['data'] and crt_note_results['data'].get('data'):
        note_id = crt_note_results['data']['data']['id']
        status = 'Note creation SUCCEEDED'
        print(note_id, status)
    else:
        print(status)
    return {'status': status, 'note_id': note_id}

def search_or_create_person(company_id, name, email):
    status = 'Person search FAILED'
    person_id = ''
    is_exist = search_person(company_id, email)
    
    if is_exist['status'] == 'Person not found':
        status = 'Person search SUCCEEDED'
        print(status)
        p_created = create_person(company_id, name, email)
        if p_created['status'] == 'Person creation SUCCEEDED':
            person_id = p_created['id']
            status = 'Person search & creation SUCCEEDED'
            print(person_id, status)
        else:
            status = 'Person search SUCCEEDED BUT Person creation FAILED'
            print(status)
    elif is_exist['status'] == 'Person found':
        person_id = is_exist['id']
        status = 'Person search SUCCEEDED'
        print(person_id, status)
    else:
        print(status)
    return {'person_id': person_id, 'status': status}