from django import forms
from .models import Books, Comment, BookRating, Tag, Playlist, Report, FeaturedBooksModel

# Book Form
class BooksForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = [
            'title', 
            'author', 
            'description', 
            'tag', 
            'cover_page', 
            'book_file', 
            'visibility', 
            'price'
        ]

# Edit book form
class EditBooksForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = [
            'title', 
            'author', 
            'description', 
            'tag', 
            'cover_page',             
            'visibility', 
            'price'
        ]
        
    def clean_cover_page(self):
        file = self.cleaned_data.get('cover_page')
        if file:
            img_ext = ('.png', '.jpg', '.jpeg', '.webp')
            if not file.name.lower().endswith(img_ext):
                raise forms.ValidationError(f"Only image files are allowed: {', '.join(img_ext)}")
            if file.size > 1 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 1 MB.")
        return file



# Comment Form
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']



# Book Rating Form
class BookRatingForm(forms.ModelForm):
    class Meta:
        model = BookRating
        fields = ['rating']        


# Tag add
class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

# Playlist Form
class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name', 'description', 'books']

# Report Form
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']


class FeaturedBooksForm(forms.ModelForm):
    class Meta:
        model = FeaturedBooksModel
        fields = ['book']