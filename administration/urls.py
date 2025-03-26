from django.urls import path
from . import views

urlpatterns = [
    path('administration-electeur/', views.administration_electeur, name='administration_electeur'),  
    
    path('valide-presence/', views.valide_presence, name='valide_presence'),  
    path('verifier-information-electeur/', views.verifie_info_electeur, name='verifie_info_electeur'),  
    path('valide-page/', views.valide_page, name='valide_page'),  
    
    path('inscription-electeur/', views.inscrire_electeur, name='inscription_electeur'),
    path('modifier-electeur/<int:id>/', views.modifier_electeur, name='modifier_electeur'),
    path('supprimer-electeur/<int:id>/', views.supprimer_electeur, name='supprimer_electeur'),
    path('electeur-list/', views.electeur_list, name='electeur_list'),
    
    # election
    path('administration-election/', views.administration_election, name='administration_election'), 
    
    path('election-list/', views.election_list, name='election_list'),
    path('create-election/', views.create_election, name='create_election'),
    
    path('lancer/<int:election_id>/', views.lancer_election, name='lancer_election'),
    path('cloturer/<int:election_id>/', views.cloturer_election, name='cloturer_election'),
    path('activer/<int:election_id>/', views.activer_election, name='activer_election'),
    
    # candidat
    path('administration-candidat/', views.administration_candidat, name='administration_candidat'), 
    path('create-candidat/', views.create_candidat, name='create_candidat'),
    path('candidat-list/', views.candidat_list, name='candidat_list'),
    
    path('election/results/', views.election_results, name='election_results'),
    path('election/results/<int:election_id>/download/', views.download_election_results, name='download_election_results'),

]
