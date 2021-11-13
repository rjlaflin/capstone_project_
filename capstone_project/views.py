from django.views import View
from django.shortcuts import render, redirect
from .models import User, Goals
from typing import Dict, Type
from django.http import QueryDict, HttpRequest, HttpResponse
from django.core.exceptions import ObjectDoesNotExist


class Home(View):
    def get(self, request):
        return render(request, "home.html")


class Information(View):
    def get(self, request):
        return render(request, "info.html")


class GetGoals(View):
    def get(self, request):
        return render(request, "goals.html", get_goal_data())

class AddGoalView(View):
    def get(self, request):
        return render(request, "add_goal.html", get_patients())

    def post(self, request):

        mygoalinput = request.POST["goalinput"]
        mygoalnotes = request.POST["goalnotes"]
        mypatient = request.POST["patient"]
        mygoalcurrency = request.POST["goalcurrency"]
        mygoalcompletionstatus = request.POST["goalcompletionstatus"]

        if mygoalinput == '':
            return render(request, "add_goal.html", {'message': 'Goal input cannot be nothing'})
        if mygoalnotes == '':
            return render(request, "add_goal.html", {'message': 'Goal notes cannot be nothing'})
        if mypatient == '':
            return render(request, "add_goal.html", {'message': 'Patient cannot be nothing'})
        if mygoalcurrency == '':
            return render(request, "add_goal.html", {'message': 'Goal Currency cannot be nothing'})
        if mygoalcompletionstatus == '':
            return render(request, "add_goal.html", {'message': 'Goal CompletionStatus cannot be nothing'})






class Login(View):
    def get(self, request):
        request.session.pop("uname", None)
        return render(request, "login.html")

    def post(self, request):
        print(request.POST['uname'] + request.POST['psw'])

        user = None
        try:
            user = User.objects.get(unique_id=request.POST['uname'])
            request.session["uname"] = user.uname
        except:
            pass
        if user is not None and user.pwd == request.POST['psw']:
            request.session["uname"] = request.POST["uname"]
            if user.user_type == 0:
                return redirect("/home_Supervisor.html")
            if user.user_type == 1:
                return redirect("/home_instructor.html")
            if user.user_type == 2:
                return redirect("/home_patient.html")
        return render(request, "login.html", {'message': 'Invalid name/password'})


class HomeSupervisor(View):
    def get(self, request):

        return render(request, "home_Supervisor.html", get_admin_template_data())

    def post(self,request):
        pass

def get_admin_template_data():
    return {
        "User": list(User.objects.all()),
        "Supervicor": list(User.objects.all()),
    }

def get_goal_data():
    return {
        "Goals": list(Goals.objects.all())
    }



def get_patients():
    return {
        "Patients": User.objects.filter(user_type__in=['2'])
    }

class HomeInstructor(View):
    def get(self, request):
        return render(request, "home_instructor.html")

    def post(self,request):
        pass


class HomePatient(View):
    def get(self, request):
        user = User.objects.get(unique_id=request.session["uname"])
        return render(request, "home_patient.html", {"user_info": user})

    def post(self,request):
        pass

class AddUser(View):
    def get(self, request):
        return render(request, "add_user.html")

    def post(self, request):
        name = request.POST["name"]
        uname = request.POST["uname"]
        password = request.POST["pwd"]
        insurance_info = request.POST["ins"]
        id1 = User.objects.all().count()
        if name != '' and uname != '' and password != '':
            if request.POST["role"] == 'Supervisor':
                new_user = User(id=id1, name=name, unique_id=uname, pwd=password,
                                 insurance_information=insurance_info, user_type='0')
                new_user.save()
            elif request.POST["role"] == 'Instructor':
                new_user = User(id=id1, name=name, unique_id=uname, pwd=password,
                                 insurance_information=insurance_info, user_type='1')
                new_user.save()
            elif request.POST["role"] == 'Patient':
                new_user = User(id=id1, name=name, unique_id=uname, pwd=password,
                                 insurance_information=insurance_info, user_type='2')
                new_user.save()
            else:
                return render(request, "home.html")

        return render(request, "home_Supervisor.html")

