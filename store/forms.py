from django import forms

from store.models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['subject','review']