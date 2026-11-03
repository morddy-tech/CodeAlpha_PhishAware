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
                    "maxlength": 2000,
                    "placeholder": "Tell us what you think about the training...",
                }
            ),
        }

    def clean_message(self):
        message = (self.cleaned_data.get("message") or "").strip()
        if len(message) > 2000:
            raise forms.ValidationError("Feedback must be 2,000 characters or fewer.")
        return message