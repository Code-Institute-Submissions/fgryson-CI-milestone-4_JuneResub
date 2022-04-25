from django.urls import path

from . import views

app_name = 'sales'
urlpatterns = [
    path('', views.TestView.as_view() , name='test')
]