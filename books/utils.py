from django.core.exceptions import ValidationError

def file_size_check(value):
    if value.size > 25 * 1024 * 1024:  # 25 MB limit
        raise ValidationError("File size cannot exceed 25MB.")

def validate_pdf_check(value):
    if not value.name.lower().endswith(".pdf"):
        raise ValidationError("Only PDF files are allowed.")
