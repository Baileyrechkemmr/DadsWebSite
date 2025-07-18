# ⚔️ OMIMI Swords - Artisan Sword Collection Website

A Django-powered website showcasing artisan sword craftsmanship, classes, and sales.

## ✨ Features

- 🖼️ **Gallery**: Professional sword showcase with S3 image storage
- 🏫 **Classes**: Sword-making class registration and information
- 🛒 **Sales**: Sword sales with detailed descriptions and pricing
- 📝 **Blog**: Rich-text blog posts with image support
- 🏨 **Travel**: Hotel recommendations for class attendees
- 🔧 **Admin**: Full Django admin interface with image thumbnails

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Baileyrechkemmr/DadsWebSite.git
   cd DadsWebSite
   ```

2. **Setup environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials (see SETUP_GUIDE.md)
   ```

4. **Setup database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run development server**
   ```bash
   python manage.py runserver
   ```

## 🔐 Environment Setup

**For complete setup instructions including credentials, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

⚠️ **Important**: This project requires AWS S3 credentials and email configuration. Contact the project maintainer for:
- AWS access keys for the `ominisword-images` bucket
- Email SMTP credentials for contact forms

## 🛠️ Tech Stack

- **Backend**: Django 4.2
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Storage**: AWS S3 with signed URLs
- **Email**: SMTP (Gmail)
- **Editor**: CKEditor 5 for rich text
- **Styling**: Custom CSS

## 📁 Project Structure

```
├── omimi/              # Django project settings
├── projects/           # Main Django app
│   ├── models.py      # Database models
│   ├── views.py       # View controllers
│   ├── admin.py       # Admin interface
│   └── templates/     # HTML templates
├── static/            # Static files (CSS, JS, images)
├── requirements.txt   # Python dependencies
└── .env.example      # Environment variables template
```

## 🌟 Key Features

### Image Management
- All images stored in AWS S3
- Automatic thumbnail generation in admin
- Signed URLs for secure access
- 68+ images already migrated

### Admin Interface
- Intuitive content management
- Image upload directly to S3
- Rich text editing for blog posts
- Comprehensive search and filtering

### Contact Forms
- Class registration
- Custom sword orders
- Sales inquiries
- Email notifications

## 🔧 Development

### Recent Updates
- ✅ S3 integration complete
- ✅ Admin interface enhanced
- ✅ Model fixes applied
- ✅ Image migration complete

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Contact

For access to credentials or questions about setup, contact the project maintainer.

---

**Status**: ✅ Production Ready | **Last Updated**: January 2025
