from django.contrib import admin
from .models import Board,TrelloList,Card,BoardMembers,BoardInvite,Activity

# Register your models here.

admin.site.register(Board)
admin.site.register(TrelloList)
admin.site.register(Card)
admin.site.register(BoardMembers)
admin.site.register(BoardInvite)
admin.site.register(Activity)