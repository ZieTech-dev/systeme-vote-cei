# forms.py
from django import forms
from .models import Candidat, Election

class CandidatForm(forms.ModelForm):
    class Meta:
        model = Candidat
        fields = ['username', 'nom', 'prenom', 'parti_politique', 'address', 'programme', 'photo_profile', 'election']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'parti_politique': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'programme': forms.Textarea(attrs={'class': 'form-control'}),
            'photo_profile': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'election': forms.Select(attrs={'class': 'form-control'}),
        }

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['type', 'candidats']
        widgets = {
            
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'candidats': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }



from .models import Electeur
from django.core.exceptions import ValidationError

class ElecteurForm(forms.ModelForm):
    class Meta:
        model = Electeur
        fields = ['username', 'nom', 'prenom', 'date_naissance', 'adresse', 'email', 'telephone', 'rfid_uid']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }
            
    def clean_username(self):
        username = self.cleaned_data['username']
        if Electeur.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if Electeur.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_telephone(self):
        telephone = self.cleaned_data['telephone']
        if Electeur.objects.filter(telephone=telephone).exclude(id=self.instance.id).exists():
            raise ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return telephone

    def clean_rfid_uid(self):
        rfid_uid = self.cleaned_data['rfid_uid']
        if Electeur.objects.filter(rfid_uid=rfid_uid).exclude(id=self.instance.id).exists():
            raise ValidationError("Cet identifiant RFID est déjà utilisé.")
        return rfid_uid
