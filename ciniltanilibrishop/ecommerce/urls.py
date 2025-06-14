from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import logout_view


app_name = 'ecommerce'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registrazione/', views.registrazione_view, name='registrazione'),
    path('logout/', logout_view, name='logout'),
    path('',views.homepage, name='homepage'),
    path('chi_sono',views.chi_sono, name='chi_sono'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('catalogo/<int:pk>/', views.dettaglio_prodotto, name='dettaglio_prodotto'),
    path('contatti/',views.contatti, name='contatti'),
    path('risultati/',views.risultati_ricerca, name='risultati_ricerca'),
    path('profilo/',views.visualizza_profilo, name='profilo_utente'),
    path('carrello/', views.visualizza_carrello, name='visualizza_carrello'),
    path('aggiungi-al-carrello/<int:pk>/', views.aggiungi_al_carrello, name='aggiungi_al_carrello'),
    path('aggiorna_carrello/<int:pk>/', views.aggiorna_carrello, name='aggiorna_carrello'),
    path('rimuovi_dal_carrello/<int:pk>/', views.rimuovi_dal_carrello, name='rimuovi_dal_carrello'),
    path('svuota-carrello/', views.svuota_carrello, name='svuota_carrello'),
    path('checkout/', views.checkout, name='checkout'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('invia_email/', views.invia_email, name="invia_email"),
    path('profilo/modifica/', views.modifica_dati_utente, name='modifica_dati_utente'),
    path('aggiungi_indirizzo', views.aggiungi_indirizzo, name='aggiungi_indirizzo'),
    path('novita', views.novita, name='novita'),

]