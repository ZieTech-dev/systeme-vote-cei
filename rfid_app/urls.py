from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Page d'accueil
    path('scan_card/', views.scan_card, name='scan_card'),  # Page de scan de la carte
    path('card_recognized/', views.card_recognized, name='card_recognized'),  # Page après reconnaissance
    # path('reset_session/', views.reset_session, name='reset_session'),

    
    
    
    path('voter/<int:election_id>/<int:candidat_id>', views.voter, name='voter'),
]
