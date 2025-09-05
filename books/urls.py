from django.urls import path
from .views import (
    BookListView,
    BookDetailView,
    BookCreateView,
    BookUpdateView,
    ToggleFavoriteView,
    AddCommentView,
    RateBookView,
    AddTagView,
)

app_name = 'books'

urlpatterns = [
    # Book CRUD
    path('', BookListView.as_view(), name='book_list'),
    path('add/', BookCreateView.as_view(), name='add_book'),
    path('books_details/<str:slug>/', BookDetailView.as_view(), name='book_detail'),
    # path('books_details/<str:slug>/edit/', BookUpdateView.as_view(), name='edit_book'),

    # Favorite toggle
    # path('books_details/<str:slug>/favorite/', ToggleFavoriteView.as_view(), name='toggle_favorite'),

    # Add comment
    # path('books_details/<str:slug>/comment/', AddCommentView.as_view(), name='add_comment'),

    # Rate book
    # path('books_details/<str:slug>/rate/', RateBookView.as_view(), name='rate_book'),

    # tag_adding
    path('tag/add/', AddTagView.as_view(), name='add_tag'),
]
