from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import *
from .forms import *
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin




# Book List View
class BookListView(ListView):
    model = Books
    template_name = 'books/book_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        return Books.objects.filter(visibility='public').order_by('-upload_date')


# Book Detail View
class BookDetailView(DetailView):
    model = Books
    template_name = 'books/book_details.html'
    context_object_name = 'book'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.can_view(request.user):
            return redirect('books:book_list')  # Or raise 403
        context = self.get_context_data(object=self.object)
        context['comment_form'] = CommentForm()
        context['rating_form'] = BookRatingForm()
        return self.render_to_response(context)


# Book Create View
class BookCreateView(LoginRequiredMixin, CreateView):
    model = Books
    form_class = BooksForm
    template_name = 'books/book_form.html'

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        response = super().form_valid(form)
        form.save()
        return response

    def get_success_url(self):
        return reverse_lazy('books:book_list')

# Book Update View
class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Books
    form_class = EditBooksForm
    template_name = 'books/book_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def test_func(self):
        book = self.get_object()
        return book.uploader == self.request.user

    def get_success_url(self):
        return self.object.get_absolute_url()


# Favorite / Like
class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        book = get_object_or_404(Books, slug=slug)
        favorite, created = BookFavorite.objects.get_or_create(user=request.user, book=book)
        if not created:
            favorite.delete()
        return redirect('books:book_detail', slug=slug)


# Add Comment
class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        book = get_object_or_404(Books, slug=slug)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.book = book
            comment.save()
        return redirect('books:book_detail', slug=slug)


# Rate Book
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
        return redirect('books:book_detail', slug=slug)


# adding tags for book
class AddTagView(LoginRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'books/add_tags.html'

    def form_valid(self, form):        
        tag_name = form.cleaned_data['name']
        Tag.objects.get_or_create(name=tag_name)
        return redirect('books:book_list')
