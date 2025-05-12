from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'ecommerce'

urlpatterns = [
    path('login',views.login, name='login'),
    path('registrati',views.registrati, name='registrati'),
    path('',views.homepage, name='homepage'),
    path('chi_sono',views.chi_sono, name='chi_sono'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('catalogo/<int:pk>/', views.dettaglio_prodotto, name='dettaglio_prodotto'),
    path('contatti/',views.contatti, name='contatti'),
    path('risultati/',views.risultati_ricerca, name='risultati_ricerca'),
    path('profilo/',views.visualizza_profilo, name='profilo_utente'),
    path('logout/', views.logout, name='logout'),
    path('carrello/', views.visualizza_carrello, name='visualizza_carrello'),
    path('aggiungi-al-carrello/<int:pk>/', views.aggiungi_al_carrello, name='aggiungi_al_carrello'),
    path('aggiorna_carrello/<int:pk>/', views.aggiorna_carrello, name='aggiorna_carrello'),
    path('rimuovi_dal_carrello/<int:pk>/', views.rimuovi_dal_carrello, name='rimuovi_dal_carrello'),
]