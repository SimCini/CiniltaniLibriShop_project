from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'ecommerce'

urlpatterns = [
    path('login',views.login, name='login'),
    path('registrati',views.registrati, name='registrati'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('',views.homepage, name='homepage'),
    path('chi_sono',views.chi_sono, name='chi_sono'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('catalogo/<int:pk>/', views.dettaglio_prodotto, name='dettaglio_prodotto'),
    path('contatti/',views.contatti, name='contatti'),
    path('risultati/',views.risultati_ricerca, name='risultati_ricerca'),
    path('profilo/',views.profilo, name='profilo_utente'),
    path('carrello/', views.visualizza_carrello, name='visualizza_carrello'),
]