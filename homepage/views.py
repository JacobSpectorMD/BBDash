from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.db import transaction
from homepage.forms import *


def home(request):
    template_name = "home.html"
    return render(request, template_name)


def labs1(request):
    template_name = "labs1.html"
    return render(request, template_name)