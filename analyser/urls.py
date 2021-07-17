from django.urls import path

from . import views

urlpatterns = [
path('', views.index, name='index'),
path('get_firm_heatmap', views.get_firm_heatmap, name='getComplementarityHeatmap'),
path('get_complementary_firms', views.get_complementary_firms, name='get_complementary_firms'),
path('get_complementarity_heatmap', views.get_complementarity_heatmap, name='getComplementarityHeatmap'),
path('get_firm_list',views.get_firm_list, name='get_firm_list'), 
path('start_analyse', views.start_analyse, name='startAnalyse'),
path('get_status', views.get_status, name='get_status'),
path('reset', views.reset, name='reset'),
path('get_firm_choosing_list', views.get_firm_choosing_list, name='get_firm_choosing_list'),

]