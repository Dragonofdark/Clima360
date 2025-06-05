from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('medida/', views.medida, name='medida'),
    path('cidade/', views.cidade, name='cidades'),
    path('escolher/', views.escolher_mes, name='mes'),
    path('compara/', views.compara_anos, name='anos'),
    path('resultados/', views.resultados, name='resultados'),
]