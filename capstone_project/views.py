from django.views import View
from django.shortcuts import render, redirect
from .models import User
from typing import Dict, Type
from django.http import QueryDict, HttpRequest, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

id_count = 0

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

    def post(self,request):
        pass

class AddSupervisor(View):
    def get(self, request):
        return render(request, "add_supervisor.html")

    def post(self, request):
        name = request.POST["name"]
        uname = request.POST["uname"]
        password = request.POST["pwd"]
        insurance_info = request.POST["ins"]
        id1 = User.objects.all().count()
        print(id1)
        #id2 = id+1
        if name != '':
            new_supervisor = User(id=id1, name=name, unique_id=uname, pwd=password,
                                 insurance_information=insurance_info)
            new_supervisor.save()

        return render(request, "home_Supervisor.html")