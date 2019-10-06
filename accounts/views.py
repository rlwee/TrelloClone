from .forms import UserCreationForm,SignUpForm
from trelloapp.models import BoardMembers
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User, Permission
from django.core.exceptions import PermissionDenied
from django.shortcuts import render,redirect
from django.views.generic.base import TemplateView
from django.shortcuts import render,redirect,get_object_or_404




# Create your views here.


class SignUp(TemplateView):

    template_name = 'accounts/signup.html'

    def get(self,request, **kwargs):
        form = SignUpForm()
        return render(request, self.template_name, {'form':form})

    def post(self,request, **kwargs):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # username = form.cleaned_data.get('username')
            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username = username, password = raw_password)
            # login(request, user)
            return redirect('login')
        return render(request,self.template_name,{'form':form})


class LogIn(TemplateView):

    template_name = 'accounts/login.html'

    def get(self,request,**kwargs):
        form = AuthenticationForm()
        return render(request, self.template_name, {'form':form})

    def post(self,request,**kwargs):
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

class LogOut(TemplateView):

    template_name = 'accounts/login.html'

    def get(self,request,**kwargs):
        logout(request)
        messages.info(request,"Logged out")
        return redirect('login')

class MembersViewList(TemplateView):

    template_name = 'accounts/members.html'
    
    def get(self, request, **kwargs):
        users = User.objects.all()
        return render(request, self.template_name,{'users':users})

class UserDetail(TemplateView):

    template_name = 'accounts/userdetail.html'

    def get(self, request, **kwargs):
        user_id = kwargs.get('user_id')
        users = User.objects.get(id=user_id)

        return render(request, self.template_name, {'users':users})


class AddUser(TemplateView):

    def get(self,request, **kwargs):
        user_id = kwargs.get('user_id')
        user = User.objects.get(id=user_id)
        user.has_perm()
        

class InviteMember(TemplateView):

    def dispatch(self,request, *args, **kwargs):
        pass