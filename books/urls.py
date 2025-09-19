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
    PlaylistListView,
    PlaylistCreateView,
    PlaylistDetailView,
    PlaylistUpdateView,
    AddBookToPlaylistView,
    ReportCreateView,
    SearchSuggestionsView,
    BookDeletView,
)

app_name = 'books'

urlpatterns = [
    # Book CRUD
    path('', BookListView.as_view(), name='book_list'),
    path('suggestions/', SearchSuggestionsView.as_view(), name='search_suggestions'),
    path('add/', BookCreateView.as_view(), name='add_book'),

    path('books_details/<str:slug>/', BookDetailView.as_view(), name='book_detail'),
    path('books_details/<str:slug>/edit/', BookUpdateView.as_view(), name='edit_book'),
    path('books/<str:slug>/delete/', BookDeletView.as_view(), name='delete_book'),

    # Interactions
    path('books_details/<str:slug>/favorite/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('books_details/<str:slug>/comment/', AddCommentView.as_view(), name='add_comment'),
    path('books_details/<str:slug>/rate/', RateBookView.as_view(), name='rate_book'),
    path('books_details/<str:slug>/add_to_playlist/', AddBookToPlaylistView.as_view(), name='add_to_playlist'),
    path('books_details/<str:slug>/report/', ReportCreateView.as_view(), name='report_book'),
    

    # Tagging
    path('tag/add/', AddTagView.as_view(), name='add_tag'),

    # Playlists
    path('playlists/', PlaylistListView.as_view(), name='playlist_list'),
    path('playlists/add/', PlaylistCreateView.as_view(), name='playlist_add'),
    path('playlists/<str:slug>/', PlaylistDetailView.as_view(), name='playlist_detail'),
    path('playlists/<str:slug>/edit/', PlaylistUpdateView.as_view(), name='playlist_edit'),

    # Report
    path('books_details/<str:slug>/report/', ReportCreateView.as_view(), name='report_book'),
]
