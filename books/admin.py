from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Books)
admin.site.register(Tag)
admin.site.register(BookFavorite)
admin.site.register(BookRating)
admin.site.register(Comment)
admin.site.register(Playlist)
admin.site.register(Report)
admin.site.register(FeaturedBooksModel)
