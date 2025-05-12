from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User  # Importa il modello User di Django
from .models import Utente  # Importa il tuo modello Utente

class LoginForm(forms.Form):
    email_o_username = forms.CharField(max_length=255, label='Email o Nome Utente')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')

    def clean(self):
        cleaned_data = super().clean()
        email_o_username = cleaned_data.get('email_o_username')
        password = cleaned_data.get('password')

        if email_o_username and password:
            user = authenticate(request=self.request, username=email_o_username, password=password)
            if user is None:
                # Tenta l'autenticazione usando l'email
                try:
                    utente = Utente.objects.get(email=email_o_username)
                    user = authenticate(request=self.request, username=utente.username, password=password)
                except Utente.DoesNotExist:
                    pass

            if user is not None:
                if user.is_active:
                    cleaned_data['user'] = user
                else:
                    raise forms.ValidationError('Questo account è disattivato.')
            else:
                raise forms.ValidationError('Email o nome utente e password non validi.')
        return cleaned_data

    def set_request(self, request):
        self.request = request

class RegistrazioneForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')
    conferma_password = forms.CharField(widget=forms.PasswordInput(), label='Conferma Password')

    class Meta:
        model = Utente
        fields = ('nome', 'cognome', 'email', 'username') # Campi che vuoi nel form

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        conferma_password = cleaned_data.get('conferma_password')
        email = cleaned_data.get('email')

        if password != conferma_password:
            raise forms.ValidationError("Le password non corrispondono.")
        if Utente.objects.filter(email=email).exists():
            raise forms.ValidationError("Un utente con questa email è già registrato.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user