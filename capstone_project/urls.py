"""capstone_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from capstone_project.views import Home, Information, Login, HomeSupervisor, AddUser, HomeInstructor, HomePatient, GetGoals, AddGoalView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login.html', Login.as_view()),
    path('', Home.as_view()),
    path('info.html', Information.as_view()),
    path('home_Supervisor.html', HomeSupervisor.as_view()),
    path('add_user.html', AddUser.as_view()),
    path('home_instructor.html', HomeInstructor.as_view()),
    path('home_patient.html', HomePatient.as_view()),
    path('goals.html', GetGoals.as_view()),
    path('add_goal.html', AddGoalView.as_view())
]
