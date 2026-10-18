# Instructions

This is meant to be an instruction guide to explain the order of processes for Plant Journal. Plant Journal was created using a full stack approach using Python, Gradio, and SQLite in order to have[...]

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

===

Hello, this is my plant_journal application. Its purpose is to provide a lightweight plant journaling system where you can add plants, record care events (watering, fertilizing, pruning), attach photos and notes, and view a history of care for each plant. The app uses a Django backend for data storage and API endpoints, and a Gradio UI for a simple local user interface.

The important commands you will need to know are:

- Clone the repository (get the code):

```bash
git clone https://github.com/NathanielWilcox/plant_journal
cd plant_journal
```

- Create and activate a Python virtual environment (macOS/Linux):

```bash
python3 -m venv venv
source venv/bin/activate
```

- Create and activate a Python virtual environment (Windows):

```bash
python -m venv venv
.\venv\Scripts\activate
```

- Install dependencies (installs required Python packages from requirements.txt):

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

- Generate secure environment secrets (creates SECRET_KEY and JWT_SECRET_KEY for `.env`):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

- Initialize and migrate the database (creates necessary SQLite schema):

```bash
python manage.py makemigrations
python manage.py migrate
```

- Run the Django development server (starts backend API):

```bash
python manage.py runserver
```

- Run the Gradio UI (starts the local UI that connects to the backend):

```bash
python gradio_ui.py
```

The main workflows you will need to know are as follows:

- Add a new plant

| Step | Action | Notes |
|------|--------|-------|
| 1 | Open the Gradio UI | Run `python gradio_ui.py` and open the shown URL in your browser |
| 2 | Fill in plant details | Name, species, notes, optional photo |
| 3 | Submit | Plant is stored in the Django backend (SQLite) |

- Record a care event (watering, fertilizing, pruning)

| Step | Action | Notes |
|------|--------|-------|
| 1 | Select a plant in the UI | Choose the plant you want to log care for |
| 2 | Choose event type and add details | Date, notes, amount, optional photo |
| 3 | Submit | Event saved to plant's history |

- View plant journal and history

| Step | Action | Notes |
|------|--------|-------|
| 1 | Open plant entry in UI | Lists plant details and events |
| 2 | Browse historical events | Filter or scroll through care records |
| 3 | Export or backup as needed | Copy the SQLite file or add an export feature |

Additional notes and tips:

- Environment: Create a `.env` file in the project root and set SECRET_KEY, JWT_SECRET_KEY, API_BASE_URL (e.g., `http://localhost:8000/api`), and DEBUG.
- Database: The project uses SQLite by default (no extra setup). Back up the `db.sqlite3` file to save data.
- Development & debugging: Keep `DEBUG=True` for local development, but set it to `False` in production.
- Contributing: Open an issue or PR with proposed changes; run tests (if any) before submitting.

If you'd like, I can further expand the README with example API calls, screenshots of the Gradio UI, or a quickstart script to automate setup.
