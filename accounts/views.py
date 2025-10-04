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

# accounts/views.py
from books.models import Books, Comment, Playlist  # ✅ import these at the top

# math
from django.db.models import Avg

# views main logic starts from here

# class SignUpView(CreateView):
#     template_name = 'registration/signup.html'
#     model = User
#     form_class = SignupForm
# 
#     def form_valid(self, form):
#         user = form.save()
# 
#         if User.objects.filter(email=form.cleaned_data['email']).exists():
#             form.add_error('email', 'Email already exists')
#             print('i am from view.py', form.add_error('email', 'Email already exists'))
#             return self.form_invalid(form)
#         if User.objects.filter(username=form.cleaned_data['username'].lower()).exists():
#             form.add_error('username', 'Username already taken')
#             print('i am from view.py', form.add_error('username', 'Username already taken'))
#             return self.form_invalid(form)
#         else:            
#             login(self.request, user)
#             return redirect('accounts:profile', username=user.username)

# testing SignUpView
# class SignUpView(CreateView):
#     template_name = 'registration/signup.html'
#     model = User
#     form_class = SignupForm

#     def form_valid(self, form):
#         email = form.cleaned_data.get('email', '').strip()
#         username = form.cleaned_data.get('username', '').strip().lower()

#         if User.objects.filter(email__iexact=email).exists():
#             form.add_error('email', 'Email already exists')
#             return self.form_invalid(form)

#         if User.objects.filter(username__iexact=username).exists():
#             form.add_error('username', 'Username already taken')
#             return self.form_invalid(form)

#         user = form.save()
#         login(self.request, user)
#         return redirect('accounts:profile', username=user.username)


# test2
class SignUpView(CreateView):
    template_name = 'registration/signup.html'
    model = User
    form_class = SignupForm

    def form_valid(self, form):
        # Save user first (form already validated usernames/emails)
        user = form.save()

        # Try to authenticate using email (your custom backend supports email).
        # Use the raw password the user entered in the form (password1).
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')

        user_auth = authenticate(self.request, email=email, password=password)

        # Fallback: try with username if your backend also supports that.
        if user_auth is None:
            username = form.cleaned_data.get('username')
            user_auth = authenticate(self.request, username=username, password=password)

        # If authenticate succeeded, login() will work because user_auth has backend attribute
        if user_auth:
            login(self.request, user_auth)
        else:
            # As a last-resort fallback (not ideal), specify backend explicitly.
            # Use the dotted path to your backend class.
            login(self.request, user, backend='accounts.backend.EmailBackend')

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
    next_page = reverse_lazy('accounts:signin')



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
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object().user

        uploaded_books = Books.objects.filter(uploader=user).order_by('-upload_date')
        recent_reviews = Comment.objects.filter(user=user).order_by('-created_at')[:10]
        user_playlists = Playlist.objects.filter(user=user).prefetch_related('books')

        # aggregate favorites & avg rating across user's books
        user_books_qs = Books.objects.filter(uploader=user)
        fav_count = 0
        avg_rating = None
        if user_books_qs.exists():
            fav_count = sum([b.total_favorites for b in user_books_qs])
            # compute avg rating across books (fallback safe)
            ratings = user_books_qs.aggregate(avg=Avg('ratings__rating'))
            avg_rating = ratings.get('avg') or 0

        context.update({
            'uploaded_books': uploaded_books,
            'recent_reviews': recent_reviews,
            'user_playlists': user_playlists,
            'user_books': uploaded_books,            # used in hero+activity
            'books_for_sale': uploaded_books.filter(visibility__in=['public','unlisted']),
            'related_stats': {
                'favorites_count': fav_count,
                'avg_rating': avg_rating
            }
        })
        return context



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
