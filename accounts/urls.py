from django.urls import path
from .views import SignUpView, SigninView, UserLogoutView, ProfileView, EditProfileView

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # profile urls
    path('profile/<str:username>', ProfileView.as_view(), name='profile'),
    path("profile_edit/<str:username>/", EditProfileView.as_view(), name="profile_edit"),
]
