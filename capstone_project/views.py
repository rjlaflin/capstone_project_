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
        return render(request, "add_goal.html", get_patients(''))

    def post(self, request):

        validgoal = ValidateGoalInput(request.POST["goalinput"])
        validgoalnotes = ValidateGoalNotes(request.POST["goalnotes"])
        validpatient = ValidatePatient(request.POST["patient"])
        validgoalcurrency = ValidateGoalCurrency(request.POST["goalcurrency"])
        validgoalcompletionstatus = ValidateGoalCompletionStatus(request.POST["goalcompletionstatus"])

        if not validgoal:
            return render(request, "add_goal.html", get_patients('Error with Adding Goal'))
        if not validgoalnotes:
            return render(request, "add_goal.html", get_patients('Error with Goal Notes'))
        if not validpatient:
            return render(request, "add_goal.html", get_patients('Error with selecting Patient'))
        if not validgoalcurrency:
            return render(request, "add_goal.html", get_patients('Error with selecting Goal Currency'))
        if not validgoalcompletionstatus:
            return render(request, "add_goal.html", get_patients('Error with adding Goal Completion Status'))

        try:
            user2 = User(User.objects.get(unique_id=request.POST['patient']).id)
            id1 = Goals.objects.all().count()

            a = Goals.objects.create(id=id1, goal=validgoal, notesforgoal=validgoalnotes,userforgoal=user2, goalcurrency=validgoalcurrency, statusofgoal=validgoalcompletionstatus)
            a.save()

        except:
            return render(request, "add_goal.html", get_patients('Error adding goal to the database. Try filling out the form again.'))

        return render(request, "goals.html", get_goal_data())

def ValidateGoalInput(input):
    if input is None:
        return False
    elif input == '':
        return False
    elif len(input) > 400:
        return False
    else:
        return input

def ValidateGoalNotes(input):
    if input is None:
        return False
    elif input == '':
        return False
    else:
        return input

def ValidatePatient(input):
    validuser = User.objects.filter(unique_id=input)
    if validuser is None:
        return False
    else:
        myuser = User.objects.get(unique_id=input).user_type
        if myuser != 2:
            return False
        else:
            return True

def ValidateGoalCurrency(input):
    if input is None:
        return False
    else:
        if input == 'Completed Goal':
            return '0'
        elif input == 'Current Goal':
            return '1'
        elif input == 'Future Goal':
            return '2'
        else:
            return False

def ValidateGoalCompletionStatus(input):
    if input is None:
        return False
    else:
        if input == 'Not Completed Goal':
            return '0'
        elif input == 'Not Adequate':
            return '1'
        elif input == 'Adequate':
            return '2'
        elif input == 'Exceeds Adequacy':
            return '3'
        elif input == 'Great':
            return '4'
        else:
            return False





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
        all_users = User.objects.all()
        return render(request, "home_Supervisor.html", {"all_users": all_users})

    def post(self, request):
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



def get_patients(input):
    return {
        "Patients": User.objects.filter(user_type__in=['2']),
        "message": input
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
        ids = list(User.objects.all().values_list('id', flat=True))
        new_id = max(ids)
        new_id = new_id + 1
        print(new_id)
        if name != '' and uname != '' and password != '':
            if request.POST["role"] == 'Supervisor':
                new_user = User(id=new_id, name=name, unique_id=uname, pwd=password,
                                insurance_information=insurance_info, user_type='0')
                new_user.save()
            elif request.POST["role"] == 'Instructor':
                new_user = User(id=new_id, name=name, unique_id=uname, pwd=password,
                                insurance_information=insurance_info, user_type='1')
                new_user.save()
            elif request.POST["role"] == 'Patient':
                new_user = User(id=new_id, name=name, unique_id=uname, pwd=password,
                                insurance_information=insurance_info, user_type='2')
                new_user.save()
            else:
                return render(request, "home.html")

        all_users = User.objects.all()
        return render(request, "home_Supervisor.html", {"all_users": all_users})


class UserStatus(View):
    def get(self, request):
        user = User.objects.get(unique_id=request.session["uname"])
        return render(request, "user_status.html", {"user_info": user})

    def post(self, request):
        pass