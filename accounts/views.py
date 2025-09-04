from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from .forms import SignupForm
# Create your views here.


class SignUpView(CreateView):
    template_name = 'signup.html'
    model = User
    form_class = SignupForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('https://www.youtube.com')

class SigninView(LoginView):
    template_name = 'signin.html'

    def get_success_url(self):
        return redirect('https://www.youtube.com')

class ProfileView:
    pass        
    