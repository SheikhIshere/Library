# Special/views.py
import re
from django.views import View
from django.shortcuts import render, redirect
from django.db import transaction
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse

from .forms import BulkUploadForm, BulkTagUploadForm
from books.models import Books, Tag

BRACE_RE = re.compile(r'\{([^}]*)\}')

def split_comma_separated(s):
    """Safely split comma-separated values."""
    if not s or not s.strip():
        return []
    return [x.strip() for x in re.split(r',\s*', s.strip()) if x.strip()]

def extract_brace_items(value_str):
    """Extract items from brace syntax or fallback to comma separation."""
    if not value_str or not value_str.strip():
        return []
    
    braced = BRACE_RE.findall(value_str)
    if braced:
        return [b.strip() for b in braced if b.strip()]
    
    if ',' in value_str:
        return split_comma_separated(value_str)
    
    if value_str.strip():
        return [value_str.strip()]
    
    return []

def safe_get_list_item(lst, index, default=None):
    """Safely get item from list by index with default fallback."""
    if not lst or index >= len(lst):
        return default
    return lst[index]

def parse_price(price_str):
    """Parse price string to integer, stripping non-digit characters."""
    if not price_str:
        return 0
    
    try:
        # Remove all non-digit characters except minus sign
        cleaned = re.sub(r'[^\d\-]', '', str(price_str))
        if not cleaned:
            return 0
        
        price_val = int(cleaned)
        return max(0, price_val)  # Ensure non-negative price
    except (ValueError, TypeError):
        return 0

def generate_slug(title, max_length=100):
    """Generate a slug from title, truncated to max_length."""
    if not title:
        return None
    
    slug = slugify(title)
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    return slug

def build_field_lists_from_text(bulk_text):
    """Parse bulk text input into organized field lists."""
    field_lists = {}
    numbered = {}
    max_index = 0

    for raw_line in bulk_text.splitlines():
        line = raw_line.strip()
        if not line or ':' not in line:
            continue
        
        key, val = line.split(':', 1)
        key = key.strip()
        val = val.strip()

        # Handle numbered keys (e.g., title_1, title_2)
        m = re.match(r'^(?P<base>.+?)_(?P<idx>\d+)$', key)
        if m:
            base = m.group('base').lower()
            idx = int(m.group('idx')) - 1  # Convert to 0-based index
            numbered.setdefault(base, {})[idx] = val
            max_index = max(max_index, idx + 1)
            continue

        # Handle regular field lists
        base = key.lower()
        items = extract_brace_items(val)
        if items:
            field_lists.setdefault(base, []).extend(items)
            max_index = max(max_index, len(items))

    # Process numbered fields
    for base, idx_map in numbered.items():
        existing = field_lists.get(base, [])
        required_len = max(max_index, len(existing))
        
        # Extend existing list to required length
        lst = existing + [None] * (required_len - len(existing))
        
        # Fill in numbered values
        for idx, val in idx_map.items():
            if idx >= len(lst):
                # Extend list if needed
                lst.extend([None] * (idx - len(lst) + 1))
            lst[idx] = val
        
        field_lists[base] = lst
        max_index = max(max_index, len(lst))

    return field_lists, max_index

def parse_tag_input(bulk_text):
    """
    Parse tag input text and return a list of unique tag names.
    Supports comma-separated values and newline-separated values.
    """
    tag_names = set()
    
    # Split by both commas and newlines
    lines = bulk_text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line contains comma-separated values
        if ',' in line:
            tags_in_line = split_comma_separated(line)
            tag_names.update(tags_in_line)
        else:
            # Single tag per line
            if line:
                tag_names.add(line)
    
    return list(tag_names)

class BulkUploadView(PermissionRequiredMixin, LoginRequiredMixin, View):
    template_name = "special/bulk_books.html"
    permission_required = "books.can_Bulk_upload_books"

    def get(self, request, *args, **kwargs):
        form = BulkUploadForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = BulkUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        text = form.cleaned_data["bulk_text"]
        uploaded_files = request.FILES.getlist("files")
        
        try:
            field_lists, max_items = build_field_lists_from_text(text)
        except Exception as e:
            messages.error(request, f"Error parsing input text: {str(e)}")
            return render(request, self.template_name, {"form": form})

        # Calculate the number of items to process
        candidate_counts = [max_items]
        
        # Check all relevant fields for content
        for key in ('title', 'author', 'description', 'price', 'tags', 'visibility'):
            if key in field_lists:
                non_empty_count = len([x for x in field_lists[key] if x is not None and str(x).strip()])
                candidate_counts.append(non_empty_count)
        
        if uploaded_files:
            candidate_counts.append(len(uploaded_files))
            
        final_n = max(candidate_counts) if candidate_counts else 0
        
        if final_n == 0:
            messages.error(request, "No items detected. Provide titles, files, or other field data.")
            return render(request, self.template_name, {"form": form})

        results = []
        errors = []
        created = 0

        # Create mapping for file name matching
        uploaded_name_map = {}
        for f in uploaded_files:
            basename = f.name.rsplit('.', 1)[0].lower().strip()
            uploaded_name_map.setdefault(basename, []).append(f)

        with transaction.atomic():
            for i in range(final_n):
                row_errors = []
                
                # Safely gather all field values with defaults
                title = safe_get_list_item(field_lists.get('title'), i)
                author = safe_get_list_item(field_lists.get('author'), i, "")
                description = safe_get_list_item(field_lists.get('description'), i, "")
                
                # Parse price safely
                price_raw = safe_get_list_item(field_lists.get('price'), i)
                price_val = parse_price(price_raw)
                
                # Handle visibility with validation
                visibility_raw = safe_get_list_item(field_lists.get('visibility'), i, 'public')
                visibility = visibility_raw.lower() if visibility_raw else 'public'
                if visibility not in ['public', 'private']:
                    visibility = 'public'
                
                # Process tags
                tags_raw = safe_get_list_item(field_lists.get('tags'), i)
                tags_list = split_comma_separated(tags_raw) if tags_raw else []
                
                # Generate slug from title
                slug = generate_slug(title)
                
                # File matching logic
                matched_file = None
                input_file_names = field_lists.get('files', [])
                filename_from_input = safe_get_list_item(input_file_names, i)
                
                if filename_from_input:
                    # Try to match by filename
                    want_name = filename_from_input.split('.')[0].strip().lower()
                    if want_name in uploaded_name_map and uploaded_name_map[want_name]:
                        matched_file = uploaded_name_map[want_name].pop(0)
                
                # Fallback to sequential assignment
                if not matched_file and i < len(uploaded_files):
                    matched_file = uploaded_files[i]
                
                # Validate required fields
                if not title:
                    row_errors.append("Title is required")
                
                # Create book instance
                book = Books(
                    uploader=request.user,
                    title=title or f"Untitled-{i+1}",
                    author=author,
                    description=description,
                    price=price_val,
                    visibility=visibility,
                    slug=slug
                )
                
                if matched_file:
                    book.book_file = matched_file

                # Save and process if no validation errors
                if not row_errors:
                    try:
                        book.full_clean()
                        book.save()
                        
                        # Handle tags
                        if tags_list:
                            tag_objs = []
                            for tag_name in tags_list:
                                try:
                                    tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                                    tag_objs.append(tag_obj)
                                except Exception as e:
                                    row_errors.append(f"Tag error '{tag_name}': {str(e)}")
                            
                            if tag_objs and not row_errors:
                                book.tag.set(tag_objs)
                        
                        if not row_errors:
                            created += 1
                            results.append({
                                "index": i, 
                                "title": book.title, 
                                "status": "created"
                            })
                            continue  # Skip error collection for successful items
                            
                    except Exception as e:
                        row_errors.append(f"Validation/save error: {str(e)}")
                
                # Collect errors for this row
                if row_errors:
                    error_msg = "; ".join(row_errors)
                    errors.append({
                        "index": i, 
                        "title": book.title, 
                        "error": error_msg
                    })
                    results.append({
                        "index": i, 
                        "title": book.title, 
                        "status": "error", 
                        "error": error_msg
                    })

        # Report results to user
        if created:
            messages.success(request, f"Successfully created {created} book(s).")
        
        if errors:
            messages.warning(request, f"Encountered {len(errors)} error(s) during processing.")
            # Show first few errors in messages
            for error in errors[:5]:
                messages.error(request, f"Row {error['index'] + 1} ({error['title']}): {error['error']}")
            if len(errors) > 5:
                messages.info(request, f"... and {len(errors) - 5} more errors.")

        return render(request, self.template_name, {
            "form": BulkUploadForm(),
            "results": results,
            "errors": errors,
            "created": created
        })


class BulkTagUploadView(PermissionRequiredMixin, LoginRequiredMixin, View):
    template_name = "special/bulk_tags.html"
    permission_required = "books.can_Bulk_upload_books"  # Or create a specific permission for tags



    def get(self, request, *args, **kwargs):
       form = BulkTagUploadForm()
       existing_tags = Tag.objects.all()
       context = {
           "form": form,
           "existing_tags": existing_tags
       }
       return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        form = BulkTagUploadForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        text = form.cleaned_data["bulk_text"]
        
        try:
            tag_names = parse_tag_input(text)
        except Exception as e:
            messages.error(request, f"Error parsing tag input: {str(e)}")
            return render(request, self.template_name, {"form": form})

        if not tag_names:
            messages.error(request, "No valid tag names found in the input.")
            return render(request, self.template_name, {"form": form})

        created = 0
        skipped = 0
        errors = []
        results = []

        with transaction.atomic():
            for tag_name in tag_names:
                # Validate tag name
                if not tag_name or not tag_name.strip():
                    skipped += 1
                    continue
                
                tag_name = tag_name.strip()
                
                # Check if tag already exists
                if Tag.objects.filter(name=tag_name).exists():
                    skipped += 1
                    results.append({
                        "name": tag_name,
                        "status": "skipped",
                        "message": "Tag already exists"
                    })
                    continue
                
                # Create new tag
                try:
                    tag = Tag(name=tag_name)
                    tag.full_clean()
                    tag.save()
                    created += 1
                    results.append({
                        "name": tag_name,
                        "status": "created"
                    })
                except Exception as e:
                    errors.append({
                        "name": tag_name,
                        "error": str(e)
                    })
                    results.append({
                        "name": tag_name,
                        "status": "error",
                        "error": str(e)
                    })

        # Report results to user
        if created:
            messages.success(request, f"Successfully created {created} new tag(s).")
        
        if skipped:
            messages.info(request, f"Skipped {skipped} tag(s) that already exist.")
        
        if errors:
            messages.warning(request, f"Encountered {len(errors)} error(s) during processing.")
            for error in errors[:5]:
                messages.error(request, f"Tag '{error['name']}': {error['error']}")
            if len(errors) > 5:
                messages.info(request, f"... and {len(errors) - 5} more errors.")

        return render(request, self.template_name, {
            "form": BulkTagUploadForm(),
            "results": results,
            "created": created,
            "skipped": skipped,
            "errors": errors
        })