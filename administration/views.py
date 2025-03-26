from django.shortcuts import render, redirect
import serial
import time
from django.contrib import messages
from rfid_app.models import Candidat, Election,Electeur,Admin
from django.contrib.auth.tokens import default_token_generator
from rfid_app.forms import CandidatForm, ElectionForm,ElecteurForm
from django.db import IntegrityError
from django.shortcuts import  get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas



def administration_electeur(request):
    # return render(request ,'administration/base_administration.html')
    return render(request ,'administration/administration_electeur.html',{'administration_electeur':"administration_electeur"})


def electeur_list(request):
    # Obtenir l'élection active
    election_active = Election.objects.filter(actif=True).first()
    
    if election_active:
        # Récupérer la liste des électeurs
        electeurs = Electeur.objects.all()
        
        # Vérifier pour chaque électeur si il a voté
        electeurs_votants = []
        for electeur in electeurs:
            if election_active.a_vote(electeur):
                electeurs_votants.append(electeur)
        
        return render(request, 'administration/electeur_list.html', {
            'electeurs': electeurs,
            'electeurs_votants': electeurs_votants,
            'election_active': election_active,
            'administration_electeur':"administration_electeur",
        })
    else:
        # Gérer le cas où il n'y a pas d'élection active
        return render(request, 'administration/electeur_list.html', {
            'message': 'Il n\'y a pas d\'élection active en ce moment.',
            'administration_electeur':"administration_electeur"
        })

# def electeur_list(request):
#     electeurs = Electeur.objects.all() 
#     election_active = Election.objects.filter(actif=True).first()
#     return render(request, 'administration/electeur_list.html', {'electeurs': electeurs,'election_active': election_active,'administration_electeur':"administration_electeur"})


def verifie_info_electeur(request):

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
        return render(request, 'administration/valide_page.html',{'message': f"Erreur de lecture RFID :{e}",'administration_electeur':"administration_electeur"})
        
    try:
        utilisateur = Electeur.objects.get(rfid_uid=card_id)
        request.session['rfid_uid'] = card_id
        messages.success(request, "Utilisateur retrouver")
        data={
            'utilisateur':utilisateur,
            'page':"verifie_info_electeur",
            'administration_electeur':"administration_electeur",
        }
        return render(request,'administration/valide_page.html',data)  
    except Electeur.DoesNotExist:
        render(request, 'administration/valide_page.html',{'message': 'l\'utilisateur n\'existe pas !','administration_electeur':"administration_electeur"})
    
    return render(request, 'administration/valide_page.html',{'message': 'Carte non reconnue, essayez à nouveau.','administration_electeur':"administration_electeur"})



def valide_presence(request):
    card_id=request.session.get('rfid_uid', False)
    if not card_id:
        return render(request, 'administration/valide_page.html',{'message': 'la verification de l\'électeur a echoué'})

    try:
        utilisateur = Electeur.objects.get(rfid_uid=card_id)
        del request.session['rfid_uid']
        utilisateur.generate_token()
        # token = default_token_generator.make_token(utilisateur)
        # utilisateur.token = token
        # utilisateur.save()
        messages.success(request, "vous aviez ete validé")
        return redirect('valide_page')  
    except Electeur.DoesNotExist:
        render(request, 'administration/valide_page.html',{'message': 'l\'utilisateur n\'existe pas !','administration_electeur':"administration_electeur"})
    
    return render(request ,'administration/administration_home.html',{'administration_electeur':"administration_electeur"})


def valide_page(request):
    data={
            'page':"valide_page",
            'administration_electeur':"administration_electeur",
        }
    
    return render(request ,'administration/valide_page.html',data)


def inscrire_electeur(request):
    if request.method == 'POST':
        form = ElecteurForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "L'électeur a été inscrit avec succès.")
                return redirect('electeur_list')
            except IntegrityError:
                form.add_error(None, "Une erreur est survenue lors de l'inscription. Veuillez réessayer.")
        else:
            messages.error(request, "Erreur lors de l'inscription. Veuillez vérifier les informations fournies.")
    
    else:
        form = ElecteurForm()

    return render(request, 'administration/inscription_electeur.html', {'form': form, 'action': 'inscription','administration_electeur':"administration_electeur"})



def modifier_electeur(request, id):
    electeur = get_object_or_404(Electeur, id=id)

    if request.method == 'POST':
        form = ElecteurForm(request.POST, instance=electeur)
        if form.is_valid():
            try:
                form.save()
                return redirect('electeur_list')
            except IntegrityError:
                form.add_error(None, "Une erreur est survenue lors de la modification. Veuillez réessayer.")
    else:
        form = ElecteurForm(instance=electeur)

    return render(request, 'administration/inscription_electeur.html', {'form': form, 'action': 'modification','administration_electeur':"administration_electeur"})



def supprimer_electeur(request, id):
    electeur = get_object_or_404(Electeur, id=id)

    if electeur:
        electeur.delete()
        messages.success(request, "L'électeur a été supprimé avec succès.")
        return redirect('electeur_list')  # Redirige vers la liste des électeurs après suppression

    messages.error(request, "L'électeur n'a pas été supprimé !")
    electeurs = Electeur.objects.all() 
    return render(request, 'administration/electeur_list.html', {'elections': electeurs})




def administration_election(request):
    
    return render(request ,'administration/administration_election.html',{'administration_election':"administration_election"})


def create_election(request):
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('election_list')  # Rediriger vers une page qui liste les élections
    else:
        form = ElectionForm()
    return render(request, 'administration/create_election.html', {'form': form,'administration_election':"administration_election"})


def election_list(request):
    elections = Election.objects.all()  # Récupère toutes les élections
    return render(request, 'administration/election_list.html', {'elections': elections,'administration_election':"administration_election"})


def lancer_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    
    if election.is_closed():
        messages.warning(request, f"L'élection du {election.date} est déjà clôturée.")
    else:
        election.lancer()
        messages.success(request, f"L'élection du {election.date} a été lancée avec succès.")

    return redirect('election_list')

def cloturer_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    
    if election.is_closed():
        messages.warning(request, f"L'élection du {election.date} est déjà clôturée.")
    else:
        election.cloturer()
        messages.success(request, f"L'élection du {election.date} a été clôturée avec succès.")

    return redirect('election_list')


def activer_election(request, election_id):
    # Récupère l'élection ou renvoie une erreur 404
    election = get_object_or_404(Election, id=election_id)

    if election.actif:
        # Si l'élection est déjà active, on la désactive
        election.actif = False
        election.save()
        messages.success(request, f"L'élection '{election.type}' a été désactivée avec succès.")
    else:
        # Désactiver toutes les autres élections
        Election.objects.filter(actif=True).update(actif=False)
        
        # Activer l'élection sélectionnée
        election.actif = True
        election.save()
        messages.success(request, f"L'élection '{election.type}' a été activée avec succès.")
    
    return redirect('election_list')




def administration_candidat(request):
    
    return render(request ,'administration/administration_candidat.html',{'administration_candidat':"administration_candidat"})


def create_candidat(request):
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('candidat_list')  # Rediriger vers une page qui liste les candidats
    else:
        form = CandidatForm()
    return render(request, 'administration/create_candidat.html', {'form': form,'administration_candidat':"administration_candidat"})




def candidat_list(request):
    candidats = Candidat.objects.all()  # Récupère tous les candidats
    return render(request, 'administration/candidat_list.html', {'candidats': candidats,'administration_candidat':"administration_candidat"})



def election_results(request):
    # Récupérer l'élection active
    election_active = Election.objects.filter(actif=True).first()
    
    if not election_active:
        return render(request, 'administration/election_results.html', {
            'message': "Aucune élection active pour le moment."
        })

    # Récupérer les résultats triés par nombre de votes (descendant)
    resultats = election_active.resultats
    candidats = election_active.candidats.all()
    candidats_tries = sorted(
        candidats,
        key=lambda c: resultats.get(str(c.id), 0),
        reverse=True
    )

    # Identifier le gagnant (le premier dans la liste triée)
    gagnant = candidats_tries[0] if candidats_tries else None

    context = {
        'election_active': election_active,
        'candidats_tries': candidats_tries,
        'gagnant': gagnant,
        'administration_election': "administration_election",
    }
    return render(request, 'administration/election_results.html', context)


from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def download_election_results(request, election_id):
    # Récupérer l'élection
    election = Election.objects.get(id=election_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="resultats_{election.type}_{election.date}.pdf"'

    # Créer le canvas
    p = canvas.Canvas(response, pagesize=letter)
    
    # Définir les styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.fontName = 'Helvetica-Bold'
    title_style.fontSize = 20
    title_style.textColor = colors.darkblue
    
    subtitle_style = styles['Normal']
    subtitle_style.fontName = 'Helvetica'
    subtitle_style.fontSize = 14
    subtitle_style.textColor = colors.black

    # Titre principal
    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(colors.darkblue)
    p.drawCentredString(letter[0] / 2, 750, f"Résultats de l'Élection : {election.type}")
    
    # Sous-titre (date)
    p.setFont("Helvetica", 14)
    p.setFillColor(colors.grey)
    p.drawCentredString(letter[0] / 2, 720, f"Date : {election.date}")
    
    # Ligne de séparation
    p.setLineWidth(1)
    p.setStrokeColor(colors.grey)
    p.line(50, 700, letter[0] - 50, 700)

    # Liste des candidats triés
    y = 670
    candidats = election.candidats.all()
    candidats_tries = sorted(
        candidats,
        key=lambda c: election.resultats.get(str(c.id), 0),
        reverse=True
    )

    for i, candidat in enumerate(candidats_tries, 1):
        votes = election.resultats.get(str(candidat.id), 0)
        # Rang et nom en gras
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(colors.black)
        p.drawString(50, y, f"{i}. {candidat.prenom} {candidat.nom}")
        
        # Parti politique en italique
        p.setFont("Helvetica-Oblique", 10)
        p.setFillColor(colors.darkgrey)
        p.drawString(50, y - 15, f"Parti : {candidat.parti_politique}")
        
        # Votes en couleur
        p.setFont("Helvetica", 12)
        p.setFillColor(colors.blue if i == 1 else colors.black)  # Bleu pour le gagnant
        p.drawString(300, y, f"Votes : {votes}")
        
        # Ligne de séparation entre candidats
        p.setLineWidth(0.5)
        p.setStrokeColor(colors.lightgrey)
        p.line(50, y - 25, letter[0] - 50, y - 25)
        
        y -= 40
        if y < 50:  # Nouvelle page si nécessaire
            p.showPage()
            y = 750

    p.showPage()
    p.save()
    return response

