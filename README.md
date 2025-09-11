Here’s a corrected and cleaned up version:

# SWeasy Backend

Django REST Framework backend for SWeasy.

## Installation

Clone the repository and navigate to root folder:

```bash
git clone https://github.com/gianlucaromeo/sweasy-backend.git
cd sweasy-backend
```

## Run on localhost

Create a virtual environment:
```
python -m venv venv
```

Activate it:

- Linux/macOS:
```
source venv/bin/activate
```

- Windows (PowerShell):
```
venv\Scripts\Activate
```

Install dependencies:
```
pip install -r requirements.txt
```

Apply migrations:
```
python manage.py migrate
```

Start the server:
```
python manage.py runserver
```

Server runs by default at http://127.0.0.1:8000/