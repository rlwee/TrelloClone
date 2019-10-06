from trelloapp.models import Board, BoardInvite, BoardMembers
from django.contrib.auth import login,logout,authenticate
from django.http import Http404
from django.shortcuts import render,redirect,get_object_or_404
from trelloapp.models import Board


class BoardPermissionMixin():
    
    def dispatch(self, *args, **kwargs):
        board = get_object_or_404(Board, id=kwargs.get('board_id'))
        members = BoardMembers.objects.filter(board=board, member=self.request.user)
        
        if members.exists():
            return super().dispatch(*args, **kwargs)
        raise Http404
        
        
        
        
        

        

