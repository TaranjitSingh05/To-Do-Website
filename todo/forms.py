from django import forms
from .models import Todo

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'goal_type', 'progress']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter task title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter task description', 'rows': 3}),
            'goal_type': forms.Select(attrs={'class': 'form-select'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter progress percentage', 'min': 0, 'max': 100}),
        } 