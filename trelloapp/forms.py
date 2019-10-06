from django import forms
from .models import Board,TrelloList,Card,BoardInvite


class PostForm(forms.ModelForm):

    class Meta:
        model = Board
        fields = ('title',)

class TrelloListForm(forms.ModelForm):

    class Meta:
        model = TrelloList
        fields = ('title',)

class TrelloCardForm(forms.ModelForm):

    class Meta:
        model = Card
        fields = ('title','labels',)


class MemberInviteForm(forms.ModelForm):

    email = forms.CharField(label='email',widget=forms.EmailInput(attrs={'placeholder':'Enter email'})) 

    class Meta:
        model = BoardInvite
        fields = ('email','board',)

       