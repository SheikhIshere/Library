# core/views.py (or your app/views.py)
from django.views.generic import TemplateView
from books.models import Books, Tag

class HomeView(TemplateView):
    template_name = 'index.html'   # adjust if your template path differs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # recommended: evaluate small querysets to lists so template loops are safe
        ctx['featured_books'] = list(
            Books.objects.filter(visibility='public').order_by('-upload_date')[:8]
        )
        ctx['recent_books'] = list(
            Books.objects.filter(visibility='public').order_by('-upload_date')[:9]
        )
        ctx['trending_tags'] = list(Tag.objects.all()[:8])
        ctx['search_suggestions'] = [b.title for b in ctx['featured_books'][:6]]

        return ctx
