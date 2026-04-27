# petitions/forms.py
from django import forms
from .models import Petition
from accounts.utils import contains_profanity

from .models import Comment
from accounts.utils import contains_profanity

class PetitionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Seleccionar"
    
    class Meta:
        model = Petition
        fields = ['title', 'description','category']
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            'description': forms.Textarea(attrs={'rows': 5}),
            "category": forms.Select(attrs={"class": "form-select"})
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if contains_profanity(title):
            raise forms.ValidationError("El título contiene lenguaje inapropiado.")
        return title

    def clean_description(self):
        description = self.cleaned_data['description']
        if contains_profanity(description):
            raise forms.ValidationError("La descripción contiene lenguaje inapropiado.")
        return description


class CommentForm(forms.ModelForm):
    alias = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe tu comentario...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_content(self):
        content = self.cleaned_data['content']
        if contains_profanity(content):
            raise forms.ValidationError("El comentario contiene lenguaje inapropiado.")
        return content

    def clean_alias(self):
        profile = self.user.userprofile
        if profile.comment_alias:
            return profile.comment_alias

        # Si no tiene alias, generar uno temporal o pedirlo
        alias = self.cleaned_data.get('alias', '').strip()
        if not alias:
            raise forms.ValidationError("Debes elegir un alias para comentar.")
        if len(alias) < 3:
            raise forms.ValidationError("El alias debe tener al menos 3 caracteres.")
        if contains_profanity(alias):
            raise forms.ValidationError("El alias contiene lenguaje inapropiado.")
        return alias

class ResolveReportForm(forms.Form):
    resolution_message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Ej: Contenido eliminado por violar las normas de convivencia.',
            'class': 'form-control'
        }),
        label="Mensaje para el denunciante",
        help_text="Este mensaje se enviará al usuario que reportó el contenido."
    )