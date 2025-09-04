from django.urls import path
from .views import SignUpView, SigninView, ProfileView

apps_name = 'accounts'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    # path('profile/', ProfileView.as_view(), name='profile'),
]
