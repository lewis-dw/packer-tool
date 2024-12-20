# Packer tool thoughtpad

## Planning
Need to move from clunky tkinter to easy-to-update web based UI where functionality and interface are separate.

### Decided initial basic testing:
I will be using Flask with a postgreSQL db.

### UI Libraries (compare)
I have the most experience with Flask and it is probably the best for this project as it allows for compatibility with databases with libraries like
- Flask
- FastAPI
- Dash (Flask but fast)
- DJango
- NextJS


#### SQLAlchemy
Built in and allows for use with PostgreSQL (Flask-SQLAlchemy psycopg2-binary) and MySQL (Flask-SQLAlchemy mysqlclient).
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Configuration: Set the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # (optional)

sqlite_db = SQLAlchemy(app)
```
For more information on how to use read the full SQLAlchemy documentation or ask ChatGPT for a run down.

#### PyMongo
Alternatively with NoSQL databases we can use PyMongo (Flask-PyMongo) which is also compatible.
```python
from flask import Flask
from flask_pymongo import PyMongo

# Initialize Flask app
app = Flask(__name__)

# Configuration: Set the database URI
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'
mongo_db = PyMongo(app)
```
For more information on how to use read the full PyMongo documentation or ask ChatGPT for a run down.

### File struture

```plaintext
├── app
│   ├── shipping
│   │   ├── fedex.py
│   │   └── ups.py
│   ├── static
│   │   ├── css
│   │   └── js
│   ├── templates
│   │   └── *.html
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
├── .gitignore
├── README.md
├── config.py
└── run.py
```