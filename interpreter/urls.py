from django.urls import path
from . import views

urlpatterns = [
    path('', views.interpreter_view, name='interpreter'),
]