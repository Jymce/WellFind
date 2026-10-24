# WellFind

An e-commerce web application built with Django and Tailwind CSS.

<!-- TODO: add a screenshot or GIF of the storefront here -->

## Features

- Product catalog with featured products, categories, and search
- User registration, login, and profile management
- Shopping cart and checkout flow
- PayPal payment integration
- Order history
- Password reset via email (Gmail SMTP)
- Custom admin dashboard for managing products and orders

## Tech Stack

- **Backend:** Django 5.2, SQLite
- **Frontend:** Django templates, Tailwind CSS (via django-tailwind)
- **Payments:** PayPal (sandbox)
- **Email:** Gmail SMTP

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js + npm (only needed if you want to rebuild the Tailwind CSS)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/Jymce/WellFind.git
cd WellFind

# 2. Create a virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env         # then fill in the values

# 4. Run migrations and start the server
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

### Rebuilding Tailwind CSS (optional)

```bash
cd theme/static_src
npm install
python manage.py tailwind install   # from project root
python manage.py tailwind start     # watch mode
python manage.py tailwind build     # production build
```

## Deployment

The app was previously deployed on PythonAnywhere. Set `DEBUG=False` and
configure `ALLOWED_HOSTS`, `SECRET_KEY`, email, and PayPal credentials as
environment variables on your host, then run `collectstatic`.

<!-- TODO: add live demo link once redeployed -->

## Environment Variables

See `.env.example` for the full list.
