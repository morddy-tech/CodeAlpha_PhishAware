from django import forms

from core.models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["rating", "category", "message"]
        widgets = {
            "rating": forms.RadioSelect(choices=Feedback.Rating.choices),
            "category": forms.Select(choices=Feedback.Category.choices),
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell us what you think about the training…",
                }
            ),
        }