from django import forms

class BulkUploadForm(forms.Form):
    bulk_text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 12,
                "cols": 80,
                "placeholder": "Paste bulk input here. Use {..} or commas for multiple values.",
            }
        ),
        required=True,
        help_text="Use brace blocks like {val} or comma-separated values. Example: title: {A},{B}"
    )


class BulkTagUploadForm(forms.Form):
    bulk_text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 12,
                "cols": 80,
                "placeholder": "Enter tag names, one per line or comma-separated. Example: fiction, science-fiction, fantasy",
            }
        ),
        required=True,
        help_text="Enter tag names separated by commas or new lines. Duplicate tags will be ignored."
    )