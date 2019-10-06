import json
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.generic.base import TemplateView, View
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from trelloapp.models import Board,TrelloList,Card,BoardMembers,BoardInvite, Activity
from trelloapp.permissions import BoardPermissionMixin
from .forms import PostForm,TrelloListForm,TrelloCardForm,MemberInviteForm
from django.core.mail import send_mail
from django.conf import settings
from django.template import loader
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from braces.views._access import AccessMixin
from braces.views import AnonymousRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from django.dispatch import receiver
from django.db.models.signals import post_save  

# Create your views here.


class Dash(TemplateView):

    template_name = 'trelloapp/dashboard.html'

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return render(request, self.template_name, {})
        else:
            return redirect('login')

class Base(TemplateView):

    template_name = 'trelloapp/trellobase.html'
    #import pdb; pdb.set_trace()
    def get(self,request,**kwargs):
        boards = Board.objects.filter(owner=request.user)
        #owner = Board.objects.all()
        return render(request, self.template_name,{'boards':boards})


class BoardCreateView(TemplateView):

    template_name = 'trelloapp/createboard.html'
    form = PostForm

    def get(self, request, **kwargs):

        form = self.form()
       # boards = Board.objects.filter(owner=request.user)
        return render(request, self.template_name, {'form':form,})

    def post(self, request, ** kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = request.user
            board.save()
            return redirect('listofboards')
        return render(request, self.template_name,{'form':form,'board':board})


class BoardView(BoardPermissionMixin, TemplateView):
    #BoardPermissionMixin, 
    template_name = 'trelloapp/currentboard.html'
    form = TrelloListForm
    
    def get(self, request, **kwargs):
        
        id = kwargs.get('board_id')
        board = get_object_or_404(Board, pk=id)
        boardlist = TrelloList.objects.filter(board=board)
        
        dragged = Activity.objects.filter(user=request.user, activity_type=Activity.DRAGGED)

        #import pdb; pdb.set_trace()
        form = self.form()
        context = {
            'board':board,
            'boardlist':boardlist,
            'form':form,
            'dragged':dragged,
        }
        return render(request, self.template_name, context)
       


    def post(self,request,**kwargs):
      
        id = kwargs.get('board_id')
        board = get_object_or_404(Board, pk=id)
        form = self.form(request.POST)
        if form.is_valid():
            tlist = form.save(commit=False)
            tlist.board = board
            tlist.save()
            return redirect('board', board_id=board.id)
       
        return render(request, self.template_name, {'form':form,'board':board})



class InvitedBoard(TemplateView):
    
    template_name = 'trelloapp/invitedboard.html'
    form  = TrelloListForm

    def get(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        board = get_object_or_404(Board, id=board_id)
        boardlist = TrelloList.objects.filter(board=board)
        
        form = self.form()
        context = {
            'board':board,
            'boardlist':boardlist,
            'form':form
        }
        return render(request, self.template_name, context)
       


    def post(self,request,**kwargs):
      
        id = kwargs.get('board_id')
        board = get_object_or_404(Board, pk=id)
        form = self.form(request.POST)
        if form.is_valid():
            tlist = form.save(commit=False)
            tlist.board = board
            tlist.save()
            return redirect('board', board_id=board.id)
       
        return render(request, self.template_name, {'form':form,'board':board})





class ListCreate(View):

    form = TrelloListForm

    def post(self, request, **kwargs):
        board_id = kwargs.get('pk')
        board = get_object_or_404(Board, pk=board_id)
        form = self.form(request.POST)

        if form.is_valid():
            lists = form.save(commit=False)
            lists.board = board
            lists.save()
            return JsonResponse({'board_id':board.id,'list_id':lists.id, 'list_title':lists.title})
        return JsonResponse({}, status=400)



class BoardViewTrelloBase(TemplateView):

    template_name = 'trelloapp/trellobase.html'
    form = TrelloListForm
    
    def get(self, request, **kwargs):
        id = kwargs.get('board_id')
        board = get_object_or_404(Board, pk=id)
        boardlist = TrelloList.objects.filter(board=board)
        form = self.form()
        context = {
            'board':board,
            'boardlist':boardlist,
            'form':form
        }
        return render(request, self.template_name, context)
    Dash



class ListOfBoards(TemplateView):   
    """ Board list page
    """
    template_name = 'trelloapp/boards.html'

    def get(self,request,**kwargs):
        boards = Board.objects.filter(owner=request.user, archive=False)
        #import pdb; pdb.set_trace()
        
        invitedBoards = BoardInvite.objects.filter(email=request.user.email)
        
        return render(request, self.template_name,{'boards':boards,'board':invitedBoards})




class BoardDetailView(TemplateView):
    """To Edit or Deleting a board
    """
    template_name = 'trelloapp/boarddetail.html'
    
    def get(self,request, **kwargs):
        id = kwargs.get('pk')
        boards = get_object_or_404(Board, pk=id)
        archived_boards = Board.objects.filter(owner=request.user, archive=True)
        return render(request,self.template_name,{'boards':boards,'archived_boards':archived_boards})

class EditBoard(TemplateView):

    template_name = 'trelloapp/boardedit.html'
    form = PostForm

    def get(self,request, **kwargs):
        id = kwargs.get('board_id')
        boards = get_object_or_404(Board, pk=id)
        form = self.form(instance=boards)
        if not request.user.is_authenticated:
            return redirect('listofboards')
        return render(request,self.template_name,{'form':form,'boards':boards})

    def post(self,request,**kwargs):
        id = kwargs.get('board_id')
        boards = get_object_or_404(Board, pk=id)
        form = self.form(request.POST, instance=boards)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = request.user
            board.save()
            return redirect('detail', pk=board.pk)
        return render(request, self.template_name, {'form':form,'boards':boards})


class DeleteBoard(View):

    def get(self,request,**kwargs):
        id = kwargs.get('board_id')
        boards = Board.objects.get(pk=id, owner=request.user)
        boardID = Board.objects.get(pk=id, owner=request.user)
        if request.user.is_authenticated:
            boards.delete()
            return JsonResponse({'boards_id':boards.id,'boardID':boardID.id})

class DeleteBoardNew(TemplateView):
    pass



class EditList(TemplateView):

    template_name = 'trelloapp/editlist.html'
    form = TrelloListForm

    def get(self,request, **kwargs):
        id = kwargs.get('pk')
        # board = Board.objects.get(pk=id)
        lists = TrelloList.objects.get(pk=id)
        form = self.form(instance=lists)
        return render(request, self.template_name, {'lists':lists,'form':form})

    def post(self,request, **kwargs):
        id = kwargs.get('pk')
        board_id = kwargs.get('board_id')
        boards = get_object_or_404(Board, pk=board_id)
        lists = TrelloList.objects.get(pk=id)
        form = self.form(request.POST, instance=lists)
        if form.is_valid():
            listss = form.save(commit=False)
            listss.board = boards
            listss.save()
            return redirect('board', pk=board_id)
        return render(request, self.template_name, {'form':form})


class MyAjaxView(TemplateView):
    """ Render boards template through ajax
    """

    template_name = 'trelloapp/ajax.html'


class ListView(TemplateView):
    """ Retrieve all List in a Board
    """
    template_name = 'trelloapp/lists.html'

    def get(self,request,**kwargs):
        id = kwargs.get('pk')
        board = get_object_or_404(Board, pk=id)
        lists = TrelloList.objects.filter(board=board,archive=False)
        return render(request, self.template_name, {'board': board, 'lists':lists})


class ArchiveBoard(TemplateView):

    template_name = 'trelloapp/boardlists.html'

    def get(self, request, **kwargs):
        invitedBoards = BoardInvite.objects.filter(email=request.user.email)
        boardlist = Board.objects.filter(owner=request.user, archive=False)
        board_id = kwargs.get('board_id')
        archive_board = get_object_or_404(Board, id=board_id)
        archive_board.archive = True
        archive_board.save()
        return render(request, self.template_name, {'boardlist':boardlist,'board':invitedBoards})


class RetrieveBoard(View):

    def get(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        retrieve_board = get_object_or_404(Board, id=board_id)
        retrieve_board.archive = False
        retrieve_board.save()
        return JsonResponse({'board_id':retrieve_board.id})



class ArchiveList(TemplateView):

    template_name = 'trelloapp/archivedlists.html'

    def get(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        board = get_object_or_404(Board, id=board_id)
        list_id = kwargs.get('list_id')
        archive_list = get_object_or_404(TrelloList, board_id=board_id, id=list_id)
        archive_list.archive = True
        archive_list.save()
        archived = TrelloList.objects.filter(board=board_id, archive=True)
        return redirect('board', board_id = board_id)


class RetrieveList(View):

    def get(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        list_id = kwargs.get('list_id')
        board = get_object_or_404(Board, id=board_id)
        blist = get_object_or_404(TrelloList, board_id=board_id, id=list_id)
        blist.archive = False
        blist.save()
        return JsonResponse({'board_id':board.id, 'blist':blist.title, 'blist_id':blist.id})


class ListSetting(TemplateView):

    template_name = 'trelloapp/listviewsetting.html'

    def get(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        list_id = kwargs.get('list_id')
        archived_list = TrelloList.objects.filter(board=board_id, archive=True)
        board = get_object_or_404(Board, id=board_id)
        blist = get_object_or_404(TrelloList, board_id=board_id, id=list_id)
        context = {

                'blist_title':blist.title,
                'board':board,
                'list':blist,
                'archived_list':archived_list,

        }
        return render(request, self.template_name, context)




class DeleteArchivedList(TemplateView):
    
    def get(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        list_id = kwargs.get('list_id')
        board = get_object_or_404(Board, id=board_id)
        blist = get_object_or_404(TrelloList, id=list_id, board_id=board_id)
        listID = get_object_or_404(TrelloList, id=list_id, board_id=board_id)
        if request.user.is_authenticated:
            blist.delete()
            return JsonResponse({'blist_id':listID.id,'list_id':blist.id,'board_id':board.id})

class CardCreateView(TemplateView):

    template_name = 'trelloapp/addcard.html'
    form = TrelloCardForm

    def get(self, request, **kwargs):
        # import pdb; pdb.set_trace()
        id = kwargs.get('list_id')
        board_id = kwargs.get('pk')
        board = get_object_or_404(Board, pk = board_id)
        lists = get_object_or_404(TrelloList, pk=id)
        card = Card.objects.filter(trello_list=lists)
        form = self.form()
        context = {
            'board':board,
            'lists':lists,
            'card':card,
            'form':form,
        }
        return render(request, self.template_name, context)
    
    def post(self,request,**kwargs):
  
        board_id = kwargs.get('pk')
        list_id = kwargs.get('list_id')
        lists = get_object_or_404(TrelloList, pk=list_id)
        card = Card.objects.filter(trello_list=lists)
        form = self.form(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.trello_list = lists
            card.save()
            return redirect('cardviews', board_id=board_id, list_id=list_id)
        return render(request, self.template_name, {'form':form})


class CardList(TemplateView):

    template_name = 'trelloapp/cards.html'

    def get(self,request,**kwargs):
        board_id = kwargs.get('board_id')
        list_id = kwargs.get('list_id')
        board_list = get_object_or_404(TrelloList, pk=list_id)
        cards = Card.objects.filter(trello_list=board_list, archive=False)
        context = {
            'cards':cards,
            'board_id': board_id,
            'list_id': list_id,
            'board_list':board_list,
        }
        return render(request, self.template_name, context)
        
        #return JsonResponse(context)

class UpdateListView(View):

    def post(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        list_id = kwargs.get('list_id')
        blist = get_object_or_404(TrelloList, id=list_id, board__id=board_id)
        blist.title =  request.POST.get('title')
        blist.save()
        return JsonResponse({'title': blist.title})

class UpdateCardView(View):

    def post(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        list_id = kwargs.get('list_id')
        card_id = kwargs.get('card_id')
        bcard = get_object_or_404(Card, id=card_id, trello_list__id=list_id)
        bcard.title = request.POST.get('title')
        bcard.save()
        return JsonResponse({'title': bcard.title})

class CreateCardView(View):

    form = TrelloCardForm

    def post(self, request, **kwargs):
        board_id = kwargs.get('pk')
        list_id = kwargs.get('list_id')
        lists = get_object_or_404(TrelloList, pk=list_id)
        card = Card.objects.filter(trello_list=lists)
        form = self.form(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.trello_list = lists
            card.save()
            return JsonResponse({'title':card.title, 'id':card.id,'list_id':lists.id, 'board_id':board_id})

        return JsonResponse({}, status=400)

class BoardEdit(View):

    form = PostForm

    def post(self,request,**kwargs):
        id = kwargs.get('board_id')
        boards = get_object_or_404(Board, pk=id)
        form = self.form(request.POST, instance=boards)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = request.user
            board.save()
            return JsonResponse({'title':board.title,'board_id':boards.id})
        return JsonResponse({}, status=400)

class BoardCreate(View):

    form = PostForm

    def post(self, request, **kwargs):

        form = self.form(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = request.user
            board.save()
            return JsonResponse({'board_owner':board.owner, 'title':board.title, 'board_id':board.id})
        return JsonResponse({}, status=400)


from django.core import serializers

class DragCard(View):

    def post(self, request, **kwargs):
        
        user = request.user
        usr = User.objects.get(username=request.user)
        card = get_object_or_404(Card, id=kwargs.get('card_id'), trello_list__id= kwargs.get('list_id'))
        blist = get_object_or_404(TrelloList, id=kwargs.get('list_id'), board_id=kwargs.get('board_id'))
        card.trello_list = get_object_or_404(TrelloList, id=request.POST.get('list_id'))
        activity = Activity.objects.create(content_object=card, activity_type=Activity.DRAGGED, user=request.user)
        #activity = Activity.objects.create(content_object=blist, ac)
        card.save()
        #import pdb; pdb.set_trace()
        return JsonResponse({'user':usr.username,
                             'list_title': card.trello_list.title, 
                             'card_title': card.title,
                             'card_id': card.id,
                             'activity_type': activity.activity_type,
                             'list_id': card.trello_list.id,
                             }, safe=False)

class CardView(TemplateView):

    template_name = 'trelloapp/card.html'

    def get(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        list_id = kwargs.get('list_id')
        blist = TrelloList.objects.get(pk=list_id)
        card_id = kwargs.get('card_id')
        card = Card.objects.get(pk=card_id)
        archived_card = Card.objects.filter(trello_list_id=list_id, archive=True)
        context = {
            'board_id':board_id,
            'card_id':card_id,
            'card':card,
            'list_id':list_id,
            'blist':blist,
            'archived_card':archived_card,
        }
        return render(request, self.template_name, context)


class RetrieveCard(View):

    def get(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        list_id = kwargs.get('list_id')
        card_id = kwargs.get('card_id')
        card = get_object_or_404(Card, trello_list_id = list_id, id = card_id)
        card.archive=False
        card.save()
        return JsonResponse({'card_title':card.title,'card_id':card.id,'board_id':board_id})


class DeleteCard(View):

    def get(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        list_id = kwargs.get('list_id')
        card_id = kwargs.get('card_id')
        card = get_object_or_404(Card, trello_list_id = list_id, id = card_id)
        cardID = get_object_or_404(Card, trello_list_id = list_id, id = card_id)
        if request.user.is_authenticated:
            card.delete()
            return JsonResponse({'cardID':cardID.id})



class CardTitleUpdate(View):

    def post(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        list_id = kwargs.get('list_id')
        card_id = kwargs.get('card_id')
        bcard = get_object_or_404(Card, id=card_id, trello_list__id=list_id)
        bcard.title = request.POST.get('title')
        bcard.save()
        return JsonResponse({'title': bcard.title,'card_id':bcard.id})

class CardLabelUpdate(View):

    def post(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        list_id = kwargs.get('list_id')
        card_id = kwargs.get('card_id')
        bcard = get_object_or_404(Card, id=card_id, trello_list__id=list_id)
        bcard.labels = request.POST.get('labels')
        bcard.save()
        return JsonResponse({'labels':bcard.labels})

class InviteMember(TemplateView):

    template_name = 'trelloapp/invite.html'
    form = MemberInviteForm

    def get(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        board = get_object_or_404(Board, pk=board_id)
        form = self.form()
        form.fields['board'].initial=board
        
        
        return render(request, self.template_name, {'form':form,'board':board,})


class Email(View):

    form = MemberInviteForm

    def post(self,request,**kwargs):
        board_id = kwargs.get('board_id')
        board = get_object_or_404(Board, pk=board_id)
        form = self.form(request.POST)
        userEmail = request.user.email
        domain = request.META['HTTP_HOST']

        
        if form.is_valid():
            invite = form.save(commit=False)
            invite.board = board
            member = BoardInvite.objects.filter(board=board, email=invite.email)
            
            #if invite.board.owner == board.owner:
             #   return JsonResponse({}, status=400)

            if not member.exists():
                invite.save()
                receiver = request.POST.get('email')
                subject = 'Trello Board Invitation'
                message = 'You have received an invitation to a board!'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [receiver,]
                
                html_message = loader.render_to_string(
                                'trelloapp/invitation.html',
                                {
                                'uid':invite.member,
                                'domain':domain,
                                'board_id':board.id,
                                'board':board}
                                                        )
                
                send_mail(subject, message, email_from, recipient_list,fail_silently=True, html_message=html_message)

            

            return JsonResponse({'receiver':receiver}) 
        return JsonResponse({}, status=400)


class LoginInvite(TemplateView):

    template_name = 'accounts/logininvitaion.html'
    
    
    def get(self, request, **kwargs):
        form = AuthenticationForm()
        board_id = kwargs.get('board_id')
        board = get_object_or_404(Board, id=board_id)
        invite = get_object_or_404(BoardInvite, member=kwargs.get('uid'))
        user_email = User.objects.get(email=invite.email)
        newMember = BoardMembers.objects.create(board=invite.board,member=user_email,owner=True)

        return render(request, self.template_name, {'form':form})

    def post(self,request,**kwargs):
        invite = get_object_or_404(BoardInvite, member=kwargs.get('uid'))
        user_email = User.objects.get(email=invite.email)
        newMember = BoardMembers.objects.create(board=invite.board,member=user_email,owner=True)
        

        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request,user)
                messages.info(request, f"you are logged in as{username}")
                return redirect('dashboard')
            else:
                messages.error(request, f"Invalid username or password")
        return render(request, self.template_name, {'form':form})
        

class ArchiveCard(TemplateView):
    
    def get(self, request, **kwargs):
        board_id = kwargs.get('board_id')
        list_id = kwargs.get('list_id')
        card_id = kwargs.get('card_id')
        archive_card = get_object_or_404(Card, trello_list__id=list_id, id=card_id)
        archive_card.archive = True
        archive_card.save()
        return redirect('board', board_id=board_id)

class LeaveBoard(TemplateView):

    def get(self, request, **kwargs):
        #import pdb; pdb.set_trace()
        board_id = kwargs.get('board_id')
        board = get_object_or_404(Board, id=board_id)
        mem = request.user
        member = BoardMembers.objects.filter(member=mem)
        invited = BoardInvite.objects.get(board=board)
        if request.user.is_authenticated:
            member.delete()
            invited.delete()
            return redirect('dashboard')

