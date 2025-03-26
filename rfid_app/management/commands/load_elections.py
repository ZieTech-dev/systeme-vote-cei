from django.core.management.base import BaseCommand
from rfid_app.models import Candidat, Election
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Charge des données d\'élections et de candidats dans la base de données'

    def handle(self, *args, **kwargs):
        Candidat.objects.all().delete()
        Election.objects.all().delete()
        # Créer une élection de test
        election = Election(
            date=timezone.now(),
            type="Présidentielle",
        )
        election.save()  # Sauvegarder l'élection avant de l'utiliser

        self.stdout.write(self.style.SUCCESS(f"Élection du {election.date} créée avec succès."))

        # Créer des candidats de test et les associer à l'élection
        candidats = [
            Candidat(nom="Vessime", prenom="Yohan", parti_politique="Parti Socialiste", 
                     programme="L'amélioration de l'éducation", election=election,
                     username="yessime"),  # username unique
            Candidat(nom="Mian", prenom="Aude", parti_politique="Les Républicains", 
                     programme="La sécurité et l'économie", election=election,
                     username="aude"),  # username unique
            Candidat(nom="Koffi", prenom="Ornella", parti_politique="LREM", 
                     programme="L'innovation et la croissance", election=election,
                     username="ornella"),  # username unique
        ]
        
        
        for candidat in candidats:
            candidat.inscrire() 
        
        # election.candidats.add(*candidats)

        self.stdout.write(self.style.SUCCESS('Candidats créés avec succès.'))

        # Lancer l'élection (initialisation des résultats)
        election.lancer()
        self.stdout.write(self.style.SUCCESS(f"{len(candidats)} candidats associés à l'élection."))

        # Exemple de mise à jour de résultats d'élection
        election.resultats = {str(candidat.id): random.randint(0, 1000) for candidat in candidats}
        election.save()


        self.stdout.write(self.style.SUCCESS('Résultats de l\'élection mis à jour avec succès.'))
