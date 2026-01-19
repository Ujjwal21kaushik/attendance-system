from django.shortcuts import render
from django.urls import path
from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home.html')