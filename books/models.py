from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from .utils import file_size_check, validate_pdf_check
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify



VISIBILITY_CHOICES = [
    ("public", "Public"),
    ("private", "Private"),
    ("unlisted", "Unlisted"),
]

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



class Books(models.Model):
    # book description
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    tag = models.ManyToManyField(Tag, blank=True)
    author = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    upload_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=100, unique=True)

    # file related data
    cover_page = models.ImageField(upload_to="cover_pages/", blank=True, null=True)
    book_file = models.FileField(
        upload_to="books/",
        blank=True,
        null=True,
        validators=[file_size_check, validate_pdf_check],
    )
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="public")
    
    # price related data
    price = models.IntegerField()

    # fucntions
    # for admin panel
    def __str__(self):
        return self.title

    # can view
    def can_view(self, user=None):
        if self.visibility == "public":
            return True
        elif self.visibility == "private":
            return user == self.uploader
        elif self.visibility == "unlisted":
            return True  # anyone with  link can access, logic handled in views
        return False
    
    # Total number of likes
    def total_favorites(self):
        return self.likes.count()

    # Average rating of the book
    def average_rating(self):
        from django.db.models import Avg
        result = self.ratings.aggregate(avg=Avg('rating'))
        return result['avg'] or 0  # returns 0 if no ratings yet

    # Total number of ratings
    def total_ratings(self):
        return self.ratings.count()
    
    # save function
    def save(self, *args, **kwargs):
        if not self.slug:
            # Automatically generate slug from title
            self.slug = slugify(self.title)
            
            # Ensure uniqueness
            counter = 1
            original_slug = self.slug
            while Books.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrowed_books")
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name="borrow_records")
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(blank=True, null=True)
    
    # Amount user pays to borrow the book
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def is_returned(self):
        return self.return_date is not None

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title} for {self.amount_paid} currency"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    anonymous_name = models.CharField(max_length=100)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.book.title}"


class BookRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name="ratings")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book")

class BookFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name="likes")
    favorited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book")



class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="playlists")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    books = models.ManyToManyField("Books", related_name="in_playlists", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


REPORT_CHOICES = [
    ('copyright', 'Copyright Violation'),
    ('adult', 'Adult Content'),
    ('spam', 'Spam / Misleading'),
    ('other', 'Other'),
]

class Report(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey("Books", on_delete=models.CASCADE, related_name="reports")
    reason = models.CharField(max_length=20, choices=REPORT_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report on {self.book.title} by {self.reporter.username}"