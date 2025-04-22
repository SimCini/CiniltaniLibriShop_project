from django.urls import path
from . import views


app_name = 'ecommerce'

urlpatterns = [
    path('login',views.login, name='login'),
    path('registrati',views.registrati, name='registrati'),
    path('',views.homepage, name='home'),
    path('chi_sono',views.chi_sono, name='chi_sono'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('catalogo/<int:pk>/', views.dettaglio_prodotto, name='dettaglio_prodotto'),
    path('contatti/',views.contatti, name='contatti'),
]