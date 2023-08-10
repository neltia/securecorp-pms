from django.urls import path
from managers import views

app_name = "managers"

urlpatterns = [
    path('login/', views.manager_login, name="login"),
    path('logout/', views.manager_logout, name="logout"),
    path('profile/', views.manger_profile, name="profile"),
    path('change_password/', views.change_password, name="re_password")
]
