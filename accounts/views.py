# authentication 
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LogoutView

# urls
from django.urls import reverse_lazy
from django.shortcuts import redirect

from django.views.generic.edit import CreateView

# mixins
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# generic views
from django.views.generic import DetailView, UpdateView

# models and forms
from django.contrib.auth.models import User
from .models import ProfileModel
from .forms import SignupForm, SiginForm, EditProfileForm



# views main logic starts from here

class SignUpView(CreateView):
    template_name = 'registration/signup.html'
    model = User
    form_class = SignupForm

    def form_valid(self, form):
        user = form.save()

        if User.objects.filter(email=form.cleaned_data['email']).exists():
            form.add_error('email', 'Email already exists')
            return self.form_invalid(form)
        if User.objects.filter(username=form.cleaned_data['username'].lower()).exists():
            form.add_error('username', 'Username already taken')
            return self.form_invalid(form)
        else:            
            login(self.request, user)
            return redirect('accounts:profile', username=user.username)


class SigninView(LoginView):
    template_name = 'registration/signin.html'
    form_class = SiginForm

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(self.request, email=email, password=password)
        if user is not None:
            login(self.request, user)
            return redirect('accounts:profile', username=user.username)
        else:
            form.add_error(None, 'Invalid username or password')
            return self.form_invalid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('homepage')


class ProfileView(DetailView):
    template_name = 'profile/profile.html'
    model = ProfileModel
    context_object_name = 'profile'
    slug_field = 'user__username'   # fetch by username of related User
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        username = self.kwargs.get(self.slug_url_kwarg)
        user = User.objects.get(username=username)
        profile, created = ProfileModel.objects.get_or_create(user=user)
        return profile


class EditProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'profile/edit_profile.html'
    model = ProfileModel
    form_class = EditProfileForm
    context_object_name = 'profile'
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        username = self.kwargs.get(self.slug_url_kwarg)
        user = User.objects.get(username=username)
        profile, created = ProfileModel.objects.get_or_create(user=user)
        return profile

    def test_func(self):
        # Ensure only the owner can edit their profile
        profile = self.get_object()
        return self.request.user == profile.user

    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'username': self.object.user.username})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
