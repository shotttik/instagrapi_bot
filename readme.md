# Instructions to run the project in Windows

### Install pip3

> python -m pip install --user --upgrade pip

### Installing virtualenv

> python -m pip install --user virtualenv

### Creating a virtual environment¶

> python -m venv venv

### Activating a virtual environment¶

> .venv\Scripts\activate.bat

### Installing packages

> python -m pip install -r requirements.txt

## `config.py`

#### Example searching with Location(cordinates) "top" post

```
LOGIN = "youruser"
PASSWORD = "yourpassword"
GOOGLE_DOC = "Crawling Instagram"
POSTS_SORT = "top"
TYPE = "location"
TARGET = (46.22, 2.21)
MAX_FOLLOWERS = 15000
MIN_FOLLOWERS = 500
LIMIT = 1000
```

#### Example searching with Tag from "recent" post

```
LOGIN = "youruser"
PASSWORD = "yourpassword"
GOOGLE_DOC = "Crawling Instagram"
POSTS_SORT = "recent"
TYPE = "hashtag"
TARGET = "nba"
MAX_FOLLOWERS = 15000
MIN_FOLLOWERS = 500
LIMIT = 1000
```

## `IMPORTANT!` export secrets json file from google sheets api place in this location and name like `client_secret.json`

## RUN PROJECT

> python main.py

# ATTENTION:

### Make sure you have `client_secret.json` from google sheets api

### Please delete example files what I have scraped yet, `log.txt`, `result.csv` and `rubbish.csv`, also update your credentials in `config.py` also
