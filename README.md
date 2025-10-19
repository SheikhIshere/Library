# 📚 Genu Library - Digital Library Platform

![Django](https://img.shields.io/badge/Django-4.2-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tailwind](https://img.shields.io/badge/Tailwind-CSS-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

A modern, feature-rich digital library platform where users can discover, share, and manage books. Built with Django and Tailwind CSS.

---

## ✨ Features

### 📖 Core Functionality
- **Book Upload & Management** - Upload PDFs with automatic cover generation
- **Smart Search** - Search by title, author, tags, or uploader
- **User Profiles** - Custom profiles with avatars and social links
- **Rating System** - 1-5 star ratings with averages
- **Favorites & Playlists** - Bookmark books and create reading lists
- **Comments & Reviews** - Community engagement system

### 🎨 User Experience
- **Responsive Design** - Mobile-first with dark/light themes
- **Interactive UI** - Carousels, hover effects, smooth animations
- **Real-time Search** - AJAX-powered search suggestions
- **File Handling** - PDF validation and automatic thumbnail generation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- SQLite (default) or PostgreSQL

### Installation
```bash
# Clone and setup
git clone <repository-url>
cd Library

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit `http://localhost:8000` and start exploring!

---

## 🏗️ Project Structure

```
Library/
├── accounts/          # User authentication & profiles
├── books/            # Core book functionality
├── special/          # Admin tools (bulk uploads)
├── templates/        # Base templates
├── static/           # CSS, JS, images
├── media/            # Uploaded files (books, covers, profiles)
└── library/          # Project settings
```

### Key Apps
- **accounts** - User registration, profiles, authentication
- **books** - Book management, search, reviews, playlists
- **special** - Administrative features (bulk operations)

---

## 📊 Database Models

### Books
```python
class Books(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    uploader = models.ForeignKey(User)
    price = models.IntegerField()  # Free/paid books
    visibility = models.CharField(choices=['public', 'private', 'unlisted'])
    tags = models.ManyToManyField(Tag)
    # Automated: slug, upload_date, cover_page generation
```

### User Profiles
```python
class ProfileModel(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to="profiles/")
    balance = models.IntegerField(default=0)
    social_link = models.URLField(blank=True)
```

### Social Features
- **BookRating** - User ratings (1-5 stars)
- **BookFavorite** - Favorite books tracking
- **Comment** - User reviews and discussions
- **Playlist** - Custom book collections
- **Report** - Content moderation system

---

## 🎯 Key Features

### Book Management
- Upload PDF books (25MB max, PDF only)
- Automatic cover generation from PDF first page
- Public/Private/Unlisted visibility options
- Free and paid book options

### Search & Discovery
```python
# Multi-field search
Books.objects.filter(
    Q(title__icontains=query) |
    Q(author__icontains=query) |
    Q(tags__name__icontains=query) |
    Q(uploader__username__icontains=query)
)
```

### User Interaction
- Rate books (1-5 stars with averages)
- Add to favorites
- Create and manage playlists
- Comment and review books
- Follow other users

---

## ⚙️ Configuration

### Environment Setup
Create a `.env` file:
```python
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database (SQLite by default)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

## 🎨 UI Components

### Responsive Design
- Tailwind CSS with custom components
- Dark/light theme toggle
- Mobile-optimized navigation
- Accessible form controls

### Interactive Elements
- Featured books carousel with auto-play
- Real-time search suggestions
- Toast notifications
- Hover effects and smooth transitions

### Template Structure
- `base.html` - Main layout with navigation
- `index.html` - Homepage with featured content
- App-specific templates in each app's `templates/` directory

---

## 🔧 Admin Features

### Special Permissions
```python
class Meta:
    permissions = [
        ("can_bulk_upload", "Can bulk upload books"),
    ]
```

### Bulk Operations
- Bulk book uploads (`/special/bulk-upload/`)
- Bulk tag management (`/special/bulk-tags/`)
- Featured books management

---

## 🚀 Deployment

### Production Setup
```bash
# Collect static files
python manage.py collectstatic

# Database setup
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run with production server
python manage.py runserver 0.0.0.0:8000
```

### Docker Support
```bash
docker-compose up -d
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- 📧 **Email**: thesheikh255@gmail.com
- 🐛 **Issues**: [GitHub Issues](thesheikh255@gmail.com)

---

**Ready to start?** Run `python manage.py runserver` and visit `http://localhost:8000`!

*Happy reading! 📖✨*
