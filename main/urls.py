from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('csv/upload', views.profile_upload),
    path('register', views.register),
    path('login', views.login),
    path('dashboard', views.dashboard),
    path('add_user_info', views.add_info),
    path('add_new_user', views.add_user),
    path('admin/user_change_password', views.user_change_password),
    path('logout', views.logout),
    path('admin/change_password', views.changePassword),
    path('deactivate_user', views.deactivate),
    path('reactivate_user', views.reactivate),
    path('add_attributes', views.add_attributes),
    path('add_alerts_warnings', views.add_alerts_warnings),
    path('display_name', views.display_name),
    path('delete_attribute', views.delete_attribute),
    path('csv/attribute/upload', views.attribute_upload),
    path('new_attribute', views.new_attribute),
]
