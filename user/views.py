import json

from axes.decorators import axes_dispatch
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.views.generic import CreateView, FormView
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


from .tokens import account_activation_token
from user.forms import RegisterForm, LoginForm
from user.models import User


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = '/user/login/'


def login_view(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(request=request, username=email, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('/utilization/units')
            else:
                messages.add_message(request, messages.INFO, "Invalid login information.")
                return redirect('/user/login')


def logout_view(request):
    logout(request)
    return redirect('/')


def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            raw_password = form.cleaned_data['password1']
            user = User.objects.create_user(name=name, email=email, password=raw_password)

            token = default_token_generator.make_token(user)
            user.token = token
            user.save()
            mail_subject = 'Activate your BB Dash account'
            current_site = get_current_site(request)
            message = render_to_string('activation_email.html',
                                       {'user': user, 'domain': current_site.domain,
                                        'uid': urlsafe_base64_encode(force_bytes(user.id)).decode(),
                                        'token': token})
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()
            messages.add_message(request, messages.INFO, 'An email has been sent to your email address. Please click on'
                                                         ' the link to activate your account.')
        return redirect('/user/login')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and user.token == token:
        user.email_confirmed = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('/user/needs_approval/')


def needs_approval(request):
    return render(request, 'needs_approval.html')