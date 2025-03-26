from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
import serial
from django.contrib.auth import login
from django.contrib import messages
import time
from rfid_app.models import Candidat, Election,Electeur,Admin
from .forms import CandidatForm, ElectionForm,ElecteurForm
from django.http import HttpRequest
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.shortcuts import  get_object_or_404



# Une liste des cartes RFID reconnues (exemple avec des ID)
RECOGNIZED_CARDS = ['13141314']  # Remplace par tes vrais IDs RFID

def home(request):
    return render(request, 'home.html')

def scan_card(request):
    card_id = None
    
    # Connexion au lecteur RFID (assume que tu utilises un port série)
    try:
        ser = serial.Serial('COM3', 9600, timeout=1)  # À ajuster en fonction du port
        ser.flush()
        
        # Attendre un peu pour lire la carte RFID
        time.sleep(2)
        
        while True:
            # Lire la carte RFID
            card_id = ser.readline().decode('utf-8').strip()
            
            card_id = ser.readline().decode('utf-8').strip()
            card_id = ''.join(filter(str.isalnum, card_id))
            card_id = card_id.replace("IDdelacarte", "")
            if card_id:
                print(f"\nID RFID lu : {card_id}\n")
                break
            
            time.sleep(0.5)
        
        print(f"""
            
            ID RFID lu: {card_id}
            
            """*10)
        
        ser.close()
    except Exception as e:
        print("Erreur de lecture RFID :", e)
        
    try:
        if Admin.objects.get(rfid_uid=card_id):
            login(request, Admin.objects.get(rfid_uid=card_id))
            return redirect('administration_electeur')
    except Admin.DoesNotExist:
        print("il n'es pas admin")
    
    
    try:
        utilisateur = Electeur.objects.get(rfid_uid=card_id)
        print(utilisateur.token)
        # print(default_token_generator.check_token(utilisateur, utilisateur.token)*40,"++++++++++++++++")
        # if not default_token_generator.check_token(utilisateur, utilisateur.token):
        #     return render(request, 'home.html', {'message': "❌ Vous devez vous faire valider par l'administrateur"})
        if not utilisateur.is_token_valid():
            return render(request, 'home.html', {
                'message': "❌ Votre token a expiré. Vous devez vous faire valider à nouveau."
            })
        login(request, utilisateur)
        
        # if card_id in RECOGNIZED_CARDS:
        #     request.session['card_scanned'] = True
        #     request.session['rfid_uid'] = card_id
        
        request.session['card_scanned'] = True
        request.session['rfid_uid'] = card_id
        return redirect('card_recognized')  # Redirige vers la page de succès (ex: tableau de bord)
    except Electeur.DoesNotExist:
        
        return render(request, 'home.html', {'message': 'Carte non reconnue, essayez à nouveau.'})
    
    
    # # Vérifier si la carte est reconnue
    # if card_id in RECOGNIZED_CARDS:
    #     request.session['card_scanned'] = True
    #     return redirect('card_recognized')
    # else:
    #     # Afficher un message d'erreur
    #     return render(request, 'home.html', {'message': 'Carte non reconnue, essayez à nouveau.'})

def card_recognized(request):
    card_id = request.session.get('rfid_uid', None)
    utilisateur = Electeur.objects.get(rfid_uid=card_id)
    if not utilisateur.is_token_valid():
            return render(request, 'home.html', {
                'message': "❌ Votre token a expiré. Vous devez vous faire valider à nouveau."
            })
            
    if not request.session.get('card_scanned', False):
        messages.error(request, "Vous devez vous authentifier")
        return redirect('home') 
    
    election_active = Election.objects.filter(actif=True).first()
    candidats = Candidat.objects.all() if election_active else []
    # candidats = election_active.candidats.all() if election_active else []
    if not election_active:
        messages.warning(request, "Aucune élection active n'est actuellement définie.")
        return redirect('home') 
    election = Election.objects.get(id=election_active.id)
    print(candidats)
    # del request.session['card_scanned']
    return render(
                    request,
                    'scan_card.html', 
                    {       
                    'message': 'Carte Valide !',
                    'candidats': candidats,
                    'election': election,
                    }
                  )


def reset_session(request):
    # Réinitialiser la session
    if 'card_scanned' in request.session:
        del request.session['card_scanned']
    return redirect('home')



# from django.shortcuts import render, redirect


from django.db import IntegrityError


def voter(request, election_id, candidat_id):
    card_id = request.session.get('rfid_uid', None)
    # election = get_object_or_404(Election, id=election_id)
    candidat = get_object_or_404(Candidat, id=candidat_id)
    electeur = get_object_or_404(Electeur, rfid_uid=card_id)
    print(f"{electeur} "*50)

    try:
        electeur.voter(election_id, candidat_id)
        return render(request, 'end_vote.html', {
                'success': True,
                'candidat': candidat
            })
    except ValidationError as e:
        return render(request, 'end_vote.html', {
                'error': str(e)
            })
        
# if request.user.is_authenticated:
#     return HttpResponse(f"oui.")
# else:
#     return HttpResponse(f"non.")