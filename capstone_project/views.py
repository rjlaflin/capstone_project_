from django.views import View
from django.shortcuts import render, redirect
from .models import User
from typing import Dict, Type
from django.http import QueryDict, HttpRequest, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

class Home(View):
    def get(self, request):
        return render(request, "home.html")

class Information(View):
    def get(self, request):
        return render(request, "info.html")

class Login(View):
    def get(self, request):
        request.session.pop("uname", None)
        return render(request, "login.html")

    def post(self, request):
        print(request.POST['uname'] + request.POST['psw'])

        name = None
        try:
            name = User.objects.get(name=request.POST['uname'])
            request.session["name"] = name.name
        except:
            pass
        if name is not None and name.pwd == request.POST['psw']:
            request.session["uname"] = request.POST["uname"]
            if name.user_type == 0:
                return redirect("/home_Supervisor.html")
        return render(request, "login.html", {'message': 'Invalid name/password'})

class HomeSupervisor(View):
    def get(self, request):
        return render(request, "home_Supervisor.html")


