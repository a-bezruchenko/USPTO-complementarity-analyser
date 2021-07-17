from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_status', views.get_clustering_status, name='get_clustering_status'),
    path('start_clustering', views.start_clustering, name='start_clustering'),
    path('reset', views.reset, name='reset'),
]