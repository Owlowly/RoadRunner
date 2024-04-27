from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the empty choice field
        self.fields['rating'].choices = [(i, str(i)) for i in range(1, 11)]

    class Meta:
        model = Review
        fields = ['rating', 'comment']


class ContactForm(forms.Form):
    subject = forms.CharField(label='Subject', max_length=100, required=True)
    email = forms.EmailField(label='Sender email', required=True)
    message = forms.CharField(label='Message', widget=forms.Textarea, required=True)
