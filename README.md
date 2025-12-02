# Instructions

This is meant to be an instruction guide to explain the order of processes for Plant Journal. Plant Journal was created using a full stack approach using Python, Gradio, and SQLite in order to have a robust yet lightweight modular application.

## Full stack

### Python + Gradio UI + SQLite

### Other Dependencies

## Setup Instructions

### Backend Setup (Python & Django)

Clone the repository:

``` git
git clone [<repository-url>](https://github.com/NathanielWilcox/plant_journal)
cd plant_journal
```

Create a virtual environment:

`python -m venv venv`

Now activate that environment:

### Windows

`.\venv\Scripts\activate`

### macOS/Linux

`source venv/bin/activate`

## Let's Get Started

Install Python dependencies:

`pip install -r requirements.txt`

Make migrations and migrate the database:

`python manage.py makemigrations`

`python manage.py migrate`

Run the backend server:

`python manage.py runserver`

Open Gradio UI

`python gradio_ui.py`

Project Structure

core/ - Django core application and settings

plants/ - Django app for plant journal models and views

venv/ - Python virtual environment

requirements.txt - Python dependencies

This guide assumes you have Python 3.8+ and Node.js installed on your system.
