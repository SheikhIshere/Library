# core/views.py (or your app/views.py)
from django.views.generic import TemplateView
from books.models import Books, Tag, FeaturedBooksModel

class HomeView(TemplateView):
    template_name = 'index.html'   # adjust if your template path differs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # recommended: evaluate small querysets to lists so template loops are safe
        # this is for the featured books
        context['featured_books'] = FeaturedBooksModel.objects.filter(
            book__visibility="public"
        ).order_by("-featured_at")[:4]

        # this is for recent books
        context['recent_books'] = list(
            Books.objects.filter(visibility='public').order_by('-upload_date')[:6]
        )

        context['trending_tags'] = list(Tag.objects.all()[:8])
        
        context['search_suggestions'] = [b.book.title for b in context['featured_books'][:6]]

        return context
