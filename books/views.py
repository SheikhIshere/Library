# books/views.py
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import get_user_model  # ✅ added

from .models import (
    Books, Tag, BookFavorite, Comment, BookRating,
    Playlist, Report, FeaturedBooksModel
)
from .forms import (
    BooksForm, EditBooksForm, CommentForm, BookRatingForm,
    TagForm, PlaylistForm, ReportForm, FeaturedBooksForm
)

from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils.text import Truncator


# helper: check if Books model has a field (safe)
def _has_field(model, name):
    try:
        model._meta.get_field(name)
        return True
    except Exception:
        return False


# -------------------------
# Book List / Detail / CRUD
# -------------------------
class BookListView(ListView):
    """
    Public book listing with optional search (?q=...) and tag filter (?tag=...).
    Adds helpful context keys used by the templates:
      - search_suggestions: short list of titles for datalist fallback
      - featured_books: small queryset used in the featured carousel
      - recent_books: small queryset for the recent grid
      - trending_tags: list of {'name': tagname, 'count': n} dictionaries (safe)
    """
    model = Books
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12  # change to taste

    def get_queryset(self):
        qs = Books.objects.filter(visibility='public').distinct()
        q = (self.request.GET.get('q') or '').strip()
        tag = (self.request.GET.get('tag') or '').strip()

        if q:
            cond = Q()
            if _has_field(Books, 'title'):
                cond |= Q(title__icontains=q)
            if _has_field(Books, 'author'):
                cond |= Q(author__icontains=q)
            if _has_field(Books, 'isbn'):
                cond |= Q(isbn__icontains=q)
            if _has_field(Books, 'slug'):
                cond |= Q(slug__icontains=q)
            if _has_field(Books, 'tags'):
                cond |= Q(tags__name__icontains=q)
            # ✅ also allow searching uploader usernames
            if hasattr(Books, 'uploader'):
                cond |= Q(uploader__username__icontains=q)

            qs = qs.filter(cond).distinct()

        if tag and _has_field(Books, 'tags'):
            qs = qs.filter(tags__name__iexact=tag).distinct()

        if _has_field(Books, 'upload_date'):
            qs = qs.order_by('-upload_date')
        else:
            qs = qs.order_by('-pk')

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        q = (self.request.GET.get('q') or '').strip()

        try:
            sample_qs = Books.objects.filter(visibility='public')
            if q:
                sample_qs = sample_qs.filter(
                    Q(title__icontains=q) | Q(author__icontains=q)
                )
            sample_qs = sample_qs.order_by('-upload_date')[:8]
            ctx['search_suggestions'] = list(sample_qs.values_list('title', flat=True).distinct()[:8])
        except Exception:
            ctx['search_suggestions'] = []

        try:
            ctx.setdefault('featured_books', Books.objects.filter(visibility='public').order_by('-upload_date')[:6])
        except Exception:
            ctx.setdefault('featured_books', [])

        try:
            ctx.setdefault('recent_books', Books.objects.filter(visibility='public').order_by('-upload_date')[:9])
        except Exception:
            ctx.setdefault('recent_books', [])

        trending = []
        try:
            if _has_field(Books, 'tags'):
                tag_counts = (
                    Books.objects.filter(visibility='public')
                    .values('tags__name')
                    .annotate(count=Count('pk'))
                    .order_by('-count')[:8]
                )
                trending = [
                    {'name': t['tags__name'], 'count': t['count']}
                    for t in tag_counts
                    if t.get('tags__name')
                ]
        except Exception:
            trending = []

        ctx.setdefault('trending_tags', trending)
        return ctx


class BookDetailView(DetailView):
    model = Books
    template_name = 'books/book_details.html'
    context_object_name = 'book'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.can_view(request.user):
            return redirect('books:book_list')

        context = self.get_context_data(object=self.object)
        context['comment_form'] = CommentForm()
        context['rating_form'] = BookRatingForm()

        context['is_favorited'] = False
        if request.user.is_authenticated:
            context['is_favorited'] = BookFavorite.objects.filter(user=request.user, book=self.object).exists()

        if request.user.is_authenticated:
            context['user_playlists'] = Playlist.objects.filter(user=request.user).prefetch_related('books')
        else:
            context['user_playlists'] = Playlist.objects.none()

        return self.render_to_response(context)


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Books
    form_class = BooksForm
    template_name = 'books/book_form.html'

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('books:book_list')


class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Books
    form_class = EditBooksForm
    template_name = 'books/book_form_edit.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def test_func(self):
        book = self.get_object()
        return book.uploader == self.request.user

    def get_success_url(self):
        return reverse_lazy('books:book_detail', kwargs={'slug': self.object.slug})


# -------------------------
# Interactions
# -------------------------
class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        book = get_object_or_404(Books, slug=slug)
        favorite, created = BookFavorite.objects.get_or_create(user=request.user, book=book)
        if not created:
            favorite.delete()
            messages.success(request, "Removed from favorites")
        else:
            messages.success(request, "Added to favorites")
        return redirect('books:book_detail', slug=slug)


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        book = get_object_or_404(Books, slug=slug)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.book = book
            comment.save()
            messages.success(request, "Comment posted")
        else:
            messages.error(request, "Could not post comment")
        return redirect('books:book_detail', slug=slug)


class RateBookView(LoginRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        book = get_object_or_404(Books, slug=slug)
        form = BookRatingForm(request.POST)
        if form.is_valid():
            BookRating.objects.update_or_create(
                user=request.user,
                book=book,
                defaults={'rating': form.cleaned_data['rating']}
            )
            messages.success(request, "Rating saved")
        else:
            messages.error(request, "Invalid rating")
        return redirect('books:book_detail', slug=slug)


# -------------------------
# Tagging
# -------------------------
class AddTagView(LoginRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'books/add_tags.html'

    def form_valid(self, form):
        tag_name = form.cleaned_data['name']
        Tag.objects.get_or_create(name=tag_name)
        messages.success(self.request, f"Tag '{tag_name}' added")
        return redirect('books:book_list')


# -------------------------
# Playlists
# -------------------------
class PlaylistListView(LoginRequiredMixin, ListView):
    model = Playlist
    template_name = 'books/playlist_list.html'
    context_object_name = 'playlists'

    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user).prefetch_related('books')


class PlaylistDetailView(LoginRequiredMixin, DetailView):
    model = Playlist
    template_name = 'books/playlist_detail.html'
    context_object_name = 'playlist'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user).prefetch_related('books')


class PlaylistCreateView(LoginRequiredMixin, CreateView):
    model = Playlist
    form_class = PlaylistForm
    template_name = 'books/playlist_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_form(self, form_class=None):
        """Limit the form 'books' field to current user's books."""
        form = super().get_form(form_class)
        form.fields['books'].queryset = Books.objects.filter(
            uploader=self.request.user
        ).order_by('-upload_date')   # 🔑 fixed here
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Provide the user_books list used by the template's visual grid & search
        ctx['user_books'] = Books.objects.filter(
            uploader=self.request.user
        ).order_by('-upload_date')

        return ctx

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Playlist created")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('books:playlist_list')

class PlaylistUpdateView(LoginRequiredMixin, UpdateView):
    model = Playlist
    form_class = PlaylistForm
    template_name = 'books/playlist_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        # ensure user can only edit their own playlists
        return Playlist.objects.filter(user=self.request.user)

    def get_form(self, form_class=None):
        """Limit the form 'books' field to current user's books."""
        form = super().get_form(form_class)
        form.fields['books'].queryset = Books.objects.filter(
            uploader=self.request.user
        ).order_by('-upload_date')   # 🔑 fixed here
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user_books'] = Books.objects.filter(
            uploader=self.request.user
        ).order_by('-upload_date')

        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Playlist updated")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('books:playlist_list')


class AddBookToPlaylistView(LoginRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        book = get_object_or_404(Books, slug=slug)
        playlist_id = request.POST.get('playlist_id')
        if not playlist_id:
            messages.error(request, "No playlist selected")
            return redirect('books:book_detail', slug=slug)

        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
        playlist.books.add(book)
        messages.success(request, f"Added '{book.title}' to '{playlist.name}'")
        return redirect('books:book_detail', slug=slug)


# -------------------------
# Reporting
# -------------------------
class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'books/report_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.book = get_object_or_404(Books, slug=kwargs.get('slug'))
        if not self.book.can_view(request.user):
            return redirect('books:book_list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['book'] = self.book
        return ctx

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        form.instance.book = self.book
        messages.success(self.request, "Report submitted — thank you")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('books:book_detail', kwargs={'slug': self.book.slug})


# -------------------------
# Suggestions endpoint
# -------------------------
class SearchSuggestionsView(View):
    """
    GET /books/suggestions/?q=term
    returns JSON: {"results": ["title 1", "author 2", "username", ...]}
    """
    def get(self, request):
        q = (request.GET.get('q') or '').strip()
        results = []
        if not q:
            return JsonResponse({'results': results})

        qs = Books.objects.filter(visibility='public')
        cond = Q()
        if _has_field(Books, 'title'):
            cond |= Q(title__icontains=q)
        if _has_field(Books, 'author'):
            cond |= Q(author__icontains=q)
        if _has_field(Books, 'isbn'):
            cond |= Q(isbn__icontains=q)
        if _has_field(Books, 'tags'):
            cond |= Q(tags__name__icontains=q)
        if _has_field(Books, 'slug'):
            cond |= Q(slug__icontains=q)
        if hasattr(Books, 'uploader'):  # ✅ include uploader usernames
            cond |= Q(uploader__username__icontains=q)

        qs = qs.filter(cond).distinct()[:40]

        seen = set()
        for b in qs:
            t = getattr(b, 'title', None)
            if t:
                key = t.strip()
                nl = key.lower()
                if nl not in seen:
                    results.append(Truncator(key).chars(80))
                    seen.add(nl)
            a = getattr(b, 'author', None)
            if a:
                an = a.strip()
                al = an.lower()
                if al not in seen:
                    results.append(Truncator(an).chars(60))
                    seen.add(al)
            if _has_field(Books, 'tags'):
                try:
                    for tag in getattr(b, 'tags').all():
                        tn = getattr(tag, 'name', '')
                        if tn:
                            tnl = tn.lower()
                            if tnl not in seen:
                                results.append(tn)
                                seen.add(tnl)
                except Exception:
                    pass
            if len(results) >= 12:
                break

        # ✅ add usernames too
        try:
            users = get_user_model().objects.filter(username__icontains=q).values_list("username", flat=True)[:5]
            for u in users:
                if u.lower() not in seen:
                    results.append(u)
                    seen.add(u.lower())
        except Exception:
            pass

        return JsonResponse({'results': results[:12]})


class FeaturedBooksView(LoginRequiredMixin, CreateView):
    model = FeaturedBooksModel
    form_class = FeaturedBooksForm
    context_object_name = "featured_books"
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)