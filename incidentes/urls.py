from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('registrar/', views.registrar_incidente, name='registrar_incidente'),
    path('incidentes/', views.lista_incidentes, name='lista_incidentes'),
    path('editar/<int:id>/', views.editar_incidente, name='editar_incidente'),
    path('eliminar/<int:id>/', views.eliminar_incidente, name='eliminar_incidente'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
