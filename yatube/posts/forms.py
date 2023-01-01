from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')

    def clean_text(self):
        text = self.cleaned_data['text']

        if not text:
            raise forms.ValidationError(
                'Содержание не может быть пустым'
            )
        elif len(text) < 5:
            raise forms.ValidationError(
                'Хочу статью больше!'
            )

        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        text = self.cleaned_data['text']

        if not text:
            raise forms.ValidationError(
                'Содержание не может быть пустым'
            )
        elif len(text) < 5:
            raise forms.ValidationError(
                'У вас минимум оригинальности, подумай еще!'
            )

        return text
