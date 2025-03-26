from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError

class Candidat(AbstractUser):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    parti_politique = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    programme = models.TextField()
    photo_profile = models.ImageField(upload_to="photos de profile", default="photos de profile/candidat_img.jpg")
    election = models.ForeignKey('Election', on_delete=models.CASCADE, related_name='election_list')

    groups = models.ManyToManyField(Group, related_name="candidats_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="candidats_permissions", blank=True)

    def inscrire(self):
        self.save()

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.parti_politique})"

    
    
    
class Electeur(AbstractUser):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    adresse = models.TextField()
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=15, unique=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    rfid_uid = models.CharField(max_length=20, unique=True)
    token = models.CharField(max_length=250,blank=True, null=True)
    token_expiration_date = models.DateTimeField(null=True, blank=True)
    a_voter = models.BooleanField(default=False)  

    groups = models.ManyToManyField(Group, related_name="electeur_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="electeur_permissions", blank=True)
    
    def generate_token(self):
        # Génère un token et définit une date d'expiration (par exemple 1 heure)
        token = default_token_generator.make_token(self)
        self.token = token
        self.token_expiration_date = timezone.now() + timedelta(minutes=10)  # Le token expire après 1 heure
        self.save()

    def is_token_valid(self):
        if self.token_expiration_date and timezone.now() < self.token_expiration_date:
            return True
        return False
    
    def inscrire(self):
        # Vérification si l'électeur existe déjà dans le système
        if Electeur.objects.filter(email=self.email).exists():
            raise ValidationError("Cet électeur est déjà inscrit.")
        self.save()

    def voter(self, election_id, candidat_id):
        election_active = Election.objects.filter(actif=True).first()
        if election_active.a_vote(self):
            raise ValidationError("Cet électeur a déjà voté dans cette election.")
        
        # if election.is_closed():
        #     raise ValidationError("L'élection est déjà clôturée.")
        
        # if election.date < timezone.now().date():
        #     raise ValidationError("L'élection n'est pas encore ouverte ou a déjà eu lieu.")
        
        # Vote pour le candidat
        election = Election.objects.get(id=election_id)
        candidat = Candidat.objects.get(id=candidat_id)
        
        if candidat.id not in election.resultats:
            election.resultats[str(candidat.id)] = 0

        
        election.resultats[str(candidat.id)] += 1  
        self.a_voter = True
        self.save()
        election.save()
        election.enregistrer_vote(self)
        
        
    
        # election.lancer()
        # election.resultats[str(candidat.id)] += 1
        # self.a_voter = True
        # self.save()
        # election.save()  # Sauvegarde des résultats

    def __str__(self):
        return f"{self.prenom} {self.nom}"
    


class Election(models.Model):
    date = models.DateField(default=timezone.now)
    date_cloture = models.DateField(null=True, blank=True)
    type = models.CharField(max_length=100) 
    candidats = models.ManyToManyField(Candidat, related_name='candidat_list')
    electeurs = models.ManyToManyField(Electeur, related_name='Electeur_list')
    resultats = models.JSONField(default=dict) 
    actif = models.BooleanField(default=False)
    
    

    def lancer(self):
        self.resultats = {}
        self.electeurs.clear()
        for candidat in self.candidats.all():
            self.resultats[candidat.id] = 0  
        self.save()

    def cloturer(self):
        # Clôture de l'élection, empêchant tout autre vote
        self.date_cloture = timezone.now()
        self.save()

    def is_closed(self):
        # Vérification si l'élection est clôturée
        return self.date_cloture is not None
    
    def activer(self):
        # Désactiver toutes les autres élections
        Election.objects.update(actif=False)
        # Activer cette élection
        self.actif = True
        self.save()
    
    def a_vote(self, electeur):
        """
        Vérifie si un électeur a déjà voté dans cette élection.
        Retourne True si l'électeur a voté, sinon False.
        """
        return self.electeurs.filter(id=electeur.id).exists()

    def enregistrer_vote(self, electeur):
        """
        Enregistre qu'un électeur a voté dans cette élection.
        Ajoute l'électeur à la liste des électeurs ayant voté.
        """
        if not self.is_closed():  # Si l'élection n'est pas encore clôturée
            if not self.a_vote(electeur):  # Si l'électeur n'a pas encore voté
                self.electeurs.add(electeur)  # Ajouter l'électeur à la liste
                self.save()
                return True  # Le vote a été enregistré
        return False  # Le vote n'a pas été enregistré (élection clôturée ou déjà voté)


    def __str__(self):
        return f"Election {self.type} du {self.date}"



class Admin(AbstractUser):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    rfid_uid = models.CharField(max_length=20, unique=True)
    
    groups = models.ManyToManyField(Group, related_name="admin_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="admin_permissions", blank=True)

    def gerer_inscriptions(self):
        # Logique de gestion des inscriptions (électeurs et candidats)
        pass

    def superviser_elections(self):
        # Superviser les élections (clôturer, lancer, etc.)
        pass

    def __str__(self):
        return f"Admin: {self.prenom} {self.nom}"