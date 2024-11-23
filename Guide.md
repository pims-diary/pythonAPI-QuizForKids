# Installations

## Virtual Environment

```python
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
pip install -r requirements.txt
```

## Project Structure

```python
project/
├── app.py                   # Main Flask app
├── sqlite_api.py            # SQLite API routes
├── pymongo_api.py           # MongoDB API routes
├── players.db               # SQLite database
├── requirements.txt         # List of dependencies
└── venv/                    # Virtual environment (optional)
```
