from django.views import View
from django.shortcuts import render, redirect, reverse
from .models import User, Goals
from typing import Dict, Type
from django.http import QueryDict, HttpRequest, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist


class Home(View):
    def get(self, request):
        return render(request, "home.html")


class Information(View):
    def get(self, request):
        return render(request, "info.html")


class SelectPatientGoals(View):
    def get(self, request):
        user = User.objects.get(unique_id=request.session['uname'])
        if user.user_type == 2:
            return redirect("patient_goals_page.html", get_individual_goal_data(user))
        else:
            return render(request, "select_patient_goal.html", get_patients(''))

    def post(self, request):
        idforgoal = request.POST['patient']

        if not 'PatientToBeViewed' in request.session or not request.session['PatientToBeViewed']:
            request.session['PatientToBeViewed'] = idforgoal
        else:
            request.session['PatientToBeViewed'] = idforgoal

        print(request.session['PatientToBeViewed'])

        return redirect("view_specific_patient_goals.html")

class ViewSpecificPatient(View):
    def get(self, request):
        userinteger = request.session['PatientToBeViewed']
        user = User.objects.get(unique_id=userinteger)
        if user.user_type == 2:
            return render(request, "view_specific_patient_goals.html", get_individual_goal_data(user))
    def post(self):
        pass

class GetIndividualsGoals(View):
    def get(self, request):
        user = User.objects.get(unique_id=request.session['uname'])
        print(user.user_type)
        if user.user_type == 2:
            return render(request, "patient_goals_page.html", get_individual_goal_data(user))
        else:
            return redirect("goals.html")
    def post(self, request):
        pass

class GetGoals(View):
    def get(self, request):
        user = User.objects.get(unique_id=request.session['uname'])
        if user.user_type == 2:
            return redirect("patient_goals_page.html", get_individual_goal_data(user))
        else:
            return render(request, "goals.html", get_goal_data())

    def post(self, request):

        idforgoal = request.POST['GoalId']

        if not 'currentgoalid' in request.session or not request.session['currentgoalid']:
            request.session['currentgoalid'] = idforgoal
        else:
            request.session['currentgoalid'] = idforgoal

        print(request.session['currentgoalid'])

        return redirect("edit_goal.html")

def get_specific_goal_data(goalid, editgoalmessage):
    return{
        "thisgoal": Goals.objects.get(id=goalid),
        "message": editgoalmessage
    }

class AddGoalView(View):
    def get(self, request):
        user = User.objects.get(unique_id=request.session['uname'])
        if user.user_type == 2:
            return redirect("patient_goals_page.html", get_individual_goal_data(user))
        elif user.user_type == 1:
            return redirect("goals.html", get_goal_data())
        else:
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

            a = Goals.objects.create(id=id1, goal=validgoal, notesforgoal=validgoalnotes, userforgoal=user2,
                                     goalcurrency=validgoalcurrency, statusofgoal=validgoalcompletionstatus)
            a.save()

        except:
            return render(request, "add_goal.html",
                          get_patients('Error adding goal to the database. Try filling out the form again.'))

        return redirect("goals.html", get_goal_data())




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
        user = User.objects.get(unique_id=request.session['uname'])
        if user.user_type == 2:
            return redirect("patient_goals_page.html", get_individual_goal_data(user))
        else:
            all_users = User.objects.all()
            cur_user = User.objects.get(unique_id=request.session["uname"])
            print(cur_user.name)
            return render(request, "home_Supervisor.html", {"all_users": all_users, "cur_user": cur_user})

    def post(self, request):
        pass


class EditGoalView(View):
    def get(self, request):
        user = User.objects.get(unique_id=request.session['uname'])
        if user.user_type == 2:
            return redirect("patient_goals_page.html", get_individual_goal_data(user))
        else:
            return render(request, "edit_goal.html", get_specific_goal_data(request.session['currentgoalid'], ''))

    def post(self, request):

        validgoalinput = ValidateGoalInput(request.POST['goalinput'])
        validgoalnotes = ValidateGoalNotes(request.POST['goalnotes'])
        validgoalcurrency = ValidateGoalCurrency(request.POST['goalcurrency'])
        validgoalid = ValidateGoalId(request.POST['goalid'])
        validgoalstatus = ValidateGoalCompletionStatus(request.POST['goalcompletionstatus'])

        if not validgoalid:
            return redirect("goals.html", get_goal_data(), {'message': 'Invalid Goal Id'})
        if not validgoalinput:
            return render(request, "edit_goal.html",
                          get_specific_goal_data(request.POST['goalid'], 'Goal input was not valid'))
        if not validgoalnotes:
            return render(request, "edit_goal.html",
                          get_specific_goal_data(request.POST['goalid'], 'Goal notes input was not valid'))
        if not validgoalcurrency:
            return render(request, "edit_goal.html",
                          get_specific_goal_data(request.POST['goalid'], 'Goal Currency selection input was not valid'))
        if not validgoalstatus:
            return render(request, "edit_goal.html",
                          get_specific_goal_data(request.POST['goalid'], 'Goal Status Selected was not valid'))

        GoalUser = Goals.objects.get(id=request.POST['goalid']).userforgoal

        UpdatedGoal = Goals(request.POST['goalid'])
        UpdatedGoal.goal = request.POST['goalinput']
        UpdatedGoal.notesforgoal = request.POST['goalnotes']
        UpdatedGoal.userforgoal = GoalUser
        UpdatedGoal.goalcurrency = validgoalcurrency
        UpdatedGoal.statusofgoal = validgoalstatus

        UpdatedGoal.save()

        return redirect("goals.html", get_goal_data(), {'message': 'Successfully edited goal.'})

def ValidateGoalId(input):
    ThisGoal = Goals.objects.get(id=input)
    if ThisGoal is not None:
        return True
    else:
        return False


def get_admin_template_data():
    return {
        "User": list(User.objects.all()),
        "Supervicor": list(User.objects.all()),
    }

def get_goal_data():
    return {
        "Goals": list(Goals.objects.all())
    }

def get_individual_goal_data(ThisPatient):
    return {

        "Goals": Goals.objects.filter(userforgoal=ThisPatient)
    }


def get_patients(input):
    return {
        "Patients": User.objects.filter(user_type__in=['2']),
        "message": input
    }

class HomeInstructor(View):
    def get(self, request):
        user = User.objects.get(unique_id=request.session['uname'])
        if user.user_type == 2:
            return redirect("patient_goals_page.html", get_individual_goal_data(user))
        elif user.user_type == 0:
            return redirect(("home_supervisor.html"))
        else:
            return render(request, "home_instructor.html", {"user": user})

    def post(self, request):
        get_user = request.POST[""]
        return render(request, "home_instructor.html")


class HomePatient(View):
    def get(self, request):
        user = User.objects.get(unique_id=request.session["uname"])
        if user.user_type == 0:
            return redirect("home_supervisor.html")
        elif user.user_type == 1:
            return redirect("home_instructor.html")
        else:
            return render(request, "home_patient.html", {"user_info": user})

    def post(self,request):
        pass

class AddUser(View):
    def get(self, request):
        user = User.objects.get(unique_id=request.session["uname"])
        if user.user_type == 2:
            return redirect("home_patient.html", {"user_info": user})
        elif user.user_type == 1:
            return redirect("home_instructor.html")
        else:
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
        print(request)
        user = User.objects.get(name=request.GET["name"])
        return render(request, "user_status.html", {"user": user})

    def post(self, request):
        print(request)
        user = User.objects.get(name=request.GET["name"])
        print(user.name)
        if user is not None:
            user.delete()
            return redirect("/update_successful.html")
        else:
            return redirect("login.html")


class EditName(View):
    def get(self, request):
        user = User.objects.get(name=request.GET["name"])
        return render(request, "edit_name.html", {"user": user})

    def post(self, request):
        user = User.objects.get(name=request.GET["name"])
        user.name = request.POST["name"]
        print(request.POST["name"])
        user.save()
        print(user.name)
        user = User.objects.get(name=user.name)
        return redirect("/update_successful.html", {"user": user})


class EditUsername(View):
    def get(self, request):
        user = User.objects.get(name=request.GET["name"])
        return render(request, "edit_username.html", {"user": user})

    def post(self, request):
        user = User.objects.get(name=request.GET["name"])
        user.unique_id = request.POST["user_name"]
        #print(request.POST["name"])
        user.save()
        print(user.name)
        user = User.objects.get(name=user.name)
        return redirect("/update_successful.html", {"user": user})


class EditPassword(View):
    def get(self, request):
        user = User.objects.get(name=request.GET["name"])
        return render(request, "edit_password.html", {"user": user})

    def post(self, request):
        user = User.objects.get(name=request.GET["name"])
        user.pwd = request.POST["user_pwd"]
        #print(request.POST["name"])
        user.save()
        print(user.name)
        user = User.objects.get(name=user.name)
        return redirect("/update_successful.html", {"user": user})


class EditUsertype(View):
    def get(self, request):
        user = User.objects.get(name=request.GET["name"])
        return render(request, "edit_usertype.html", {"user": user})

    def post(self, request):
        user = User.objects.get(name=request.GET["name"])
        user.user_type = request.POST["user_type"]
        # print(request.POST["name"])
        user.save()
        print(user.name)
        user = User.objects.get(name=user.name)
        return redirect("/update_successful.html", {"user": user})


'''
Code For Acceptance Tests and Unit Tests for Edit user and Insurance, not working at the moment
class EditUsertype(View):
   def get(self, request: HttpRequest):
        user = LoginUtil.get_user_and_validate_by_user_id(request.session, password_change_redirect=False)

        if type(user) is HttpResponseRedirect:
            return user

        if user.id is None:
            MessageQueue.push(request.session, Message(f'No user with id {user.id} exists.', Message.Type.ERROR))
            return redirect(reverse('/home_Supervisor.html'))

        if user.id != user.id and Users.check_user_type(user) != User.UserType.Supervisor:
            MessageQueue.push(request.session, Message('You are not allowed to edit other users.', Message.Type.ERROR))
            return redirect(reverse('/home_instructor.html'))

        return render(request, "edit_usertype.html", {"user": user})

    def post(self, request):
        user = LoginUtil.get_user_and_validate_by_user_id(request.session, password_change_redirect=False)

        if type(user) is HttpResponseRedirect:
            return user

        if user.id is None:
            MessageQueue.push(request.session, Message(f'No user with id {user.id} exists.', Message.Type.ERROR))
            return redirect(reverse('/home_Supervisor.html'))

        if user.id != user.id and Users.check_user_type(user) != User.UserType.ADMIN:
            MessageQueue.push(request.session, Message('You are not allowed to edit other users.', Message.Type.ERROR))
            return redirect(reverse('/home_instructor.html'))

        fields: Dict[str, Optional[str]] = {}
        try:
            fields['user_type'] = str(request.POST['user_type'])
        except KeyError:
            fields['univ_id'] = None

        def render_error(error: UserEditError):
            return render(request, 'edit_usertype.html', {
                'user': user,
                'error': error,
            })

        if user.user_type is not None:
            # Chane user type
            if Users.check_user_type(user) != User.UserType.Supervisor:
                return render_error(UserEditError(
                        'Only admins may change user types',
                        UserEditPlace.TYPE
                    ))

            # to_edit.type = fields['user_type']

            if fields['user_type'] == 'A':
                user.user_type = User.UserType.Supervisor
            elif fields['user_type'] == 'P':
                user.user_type = User.UserType.Staff
            else:
                user.user_type = User.UserType.Patient

            user.save()
            MessageQueue.push(request.session, Message(f'User {user.unique_id} is now a {user.get_user_type_display()}'))

        print(user.name)
        user = User.objects.get(name=user.name)
        return redirect("/update_successful.html", {"user": user})


class EditInsurance(View):
    def get(self, request):
        user = User.objects.get(name=request.GET["name"])

        if user.user_type is None:
            MessageQueue.push(request.session, Message(f'No user with id {user.id} exists.', Message.Type.ERROR))
            return redirect(reverse('/home_Supervisor.html'))

        if user.id != user.id and user.user_type != User.UserType.ADMIN:
            MessageQueue.push(request.session, Message('You are not allowed to edit other users.', Message.Type.ERROR))
            return redirect(reverse('/home_instructor.html'))

        return render(request, "edit_insurance.html", {"user": user})

    def post(self, request):
        user = User.objects.get(name=request.GET["name"])
        user.insurance_information = request.POST["user_insurance"]
        #print(request.POST["name"])

        if user.user_type is None:
            MessageQueue.push(request.session, Message(f'No user with id {user.id} exists.', Message.Type.ERROR))
            return redirect(reverse('/home_Supervisor.html'))

        if user.id != user.id and user.user_type != User.UserType.ADMIN:
            MessageQueue.push(request.session, Message('You are not allowed to edit other users.', Message.Type.ERROR))
            return redirect(reverse('/home_instructor.html'))

        try:
            user.user_type = request.POST["user_type"]
            user.save()
        except KeyError:
            user.user_type = None

        print(user.name)
        user = User.objects.get(name=user.name)
        return redirect("/update_successful.html", {"user": user})
'''


class EditInsurance(View):
    def get(self, request):
        user = User.objects.get(name=request.GET["name"])
        return render(request, "edit_insurance.html", {"user": user})

    def post(self, request):
        user = User.objects.get(name=request.GET["name"])
        user.insurance_information = request.POST["user_insurance"]
        #print(request.POST["name"])
        user.save()
        print(user.name)
        user = User.objects.get(name=user.name)
        return redirect("/update_successful.html", {"user": user})


class UpdateSuccessful(View):
    def get(self, request):
        return render(request, "update_successful.html")

    def post(self, request):
        pass