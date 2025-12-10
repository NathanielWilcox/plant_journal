# Instructions

This is meant to be an instruction guide to explain the order of processes for Plant Journal. Plant Journal was created using a full stack approach using Python, Gradio, and SQLite in order to have a robust yet lightweight modular application.

## Full stack

### Python + Gradio UI + SQLite

### Other Dependencies

## Setup Instructions

### Prerequisites

- Python 3.8+ installed
- pip package manager

### Backend Setup (Python & Django)

#### 1. Clone the repository

```bash
git clone https://github.com/NathanielWilcox/plant_journal
cd plant_journal
```

#### 2. Create and activate a virtual environment

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

#### 3. Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Environment configuration

Create a `.env` file in the project root with the following variables:

``` markdown
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
API_BASE_URL=http://localhost:8000/api
DEBUG=True
```

**Generating secure secret keys:**

For `SECRET_KEY` (Django), run this Python command:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

For `JWT_SECRET_KEY`, run this Python command:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Or, generate both at once with this script:

```bash
python << 'EOF'
from django.core.management.utils import get_random_secret_key
import secrets

print("SECRET_KEY=" + get_random_secret_key())
print("JWT_SECRET_KEY=" + secrets.token_urlsafe(32))
EOF
```

Copy the output into your `.env` file. For development, `DEBUG=True` is fine, but always set it to `False` in production.

#### 5. Initialize the database

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Run the development server

In one terminal window, start the Django backend:

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

#### 7. Run the Gradio UI

In a separate terminal window (with venv activated), start Gradio:

```bash
python gradio_ui.py
```

The UI will be accessible in your browser at the URL displayed in the terminal output.

Project Structure

core/ - Django core application and settings

plants/ - Django app for plant journal models and views

venv/ - Python virtual environment

requirements.txt - Python dependencies

This guide assumes you have Python 3.8+ and Node.js installed on your system.
