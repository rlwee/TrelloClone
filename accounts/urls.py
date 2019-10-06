from django.urls import path,include
from django.contrib.auth import views as auth_views
from accounts.views import (SignUp,
                            LogIn,
                            LogOut,
                            MembersViewList,
                            UserDetail,
                            AddUser,
                            InviteMember
                           )

urlpatterns = [

    path('signup/', SignUp.as_view(), name='signup'),
    path('login/', LogIn.as_view(), name='login'),
    path('logout/', LogOut.as_view(), name='logout'),
    path('board/<int:board_id>/', MembersViewList.as_view(), name='invite'),
    path('user/<int:user_id>/', UserDetail.as_view(), name='userdetail'),
    path('user/<int:user_id>/added/',InviteMember.as_view(), name='memberadd'),
    


    path('', include('django.contrib.auth.urls')),
] 