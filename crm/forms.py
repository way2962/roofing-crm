from django import forms
from .models import CallLog


class CallLogForm(forms.ModelForm):
    class Meta:
        model = CallLog
        fields = ['caller_phone', 'caller_name', 'call_type', 'is_new_client', 'notes', 'duration_seconds']
        widgets = {
            'caller_phone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '(555) 123-4567',
                'hx-post': '/lookup-phone/', 'hx-trigger': 'change, keyup delay:500ms',
                'hx-target': '#phone-lookup-result', 'hx-swap': 'innerHTML',
            }),
            'caller_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Smith'}),
            'call_type': forms.Select(attrs={'class': 'form-select'}),
            'is_new_client': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Call notes…'}),
            'duration_seconds': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
        }
