from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_status', views.get_parsing_status, name='get_parsing_status'),
    path('start_parsing', views.start_parsing, name='start_parsing'),
    path('reset', views.reset, name='reset'),
]