# Moviegraph

Moviegraph is a demo and training application for Python and Neo4j.


## 1. Setup: Install Neo4j
```
wget http://dist.neo4j.org/neo4j-community-3.4.1-unix.tar.gz
tar xf neo4j-community-3.4.1-unix.tar.gz
cd neo4j-community-3.4.1
bin/neo4j-admin set-initial-password password
bin/neo4j start|console
```


## 2. Setup: Install a data set
```
Browser to
http://localhost:7474/
:play movies
call db.schema
(explore a bit)
```


## 3. Setup: Install application skeleton
```
git clone ...
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_DEBUG=1
export FLASK_ENV=development
FLASK_APP=moviegraph flask run
```
If you want to use a different language, feel free to convert the code.


## 4. Setup: Application in browser
```
http://127.0.0.1:5000
```


## 5. Code: Project structure

- `answers/` - all the answers!!
- `static/` - static files (css)
- `templates/` - HTML template files (Jinja format)
- `venv` - virtual environment (if setup as above)
- `moviegraph.py` - main application module
- `requirements.txt` - project requirements


### 6. Code: Flask setup code
```python
from flask import Flask, abort, render_template, request
app = Flask(__name__)
```

### 7. Code: Neo4j driver setup code
```python
from neo4j.v1 import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
```


### 8. Code: GET index page
```python
@app.route("/")
def get_index():
    """ Show the index page.
    """
    search_term = request.args.get("q", "")
    with driver.session() as session:
        movies = session.read_transaction(match_movies, q=search_term)
    return render_template("index.html", movies=movies, q=search_term)
```


### 9. Code: `match_movies` transaction function
```python
def match_movies(tx, q):
    if q:
        return tx.run("MATCH (movie:Movie) WHERE toLower(movie.title) CONTAINS toLower($term) "
                      "RETURN movie ORDER BY movie.year DESCENDING, movie.title ASCENDING", term=q).value()
    else:
        return []
```


### 10. Code: GET movie page
```python
@app.route("/movie/<title>")
def get_movie(title):
    """ Display details of a particular movie.
    """
    with driver.session() as session:
        record = session.read_transaction(match_movie, title)
    if record is None:
        abort(404, "Movie not found")
    return render_template("movie.html", movie=record["movie"], actors=record["actors"])
```


### 11. Code: `match_movie` transaction function
```python
def match_movie(tx, title):
    return tx.run("MATCH (movie:Movie) WHERE movie.title = $title "
                  "OPTIONAL MATCH (person)-[:ACTED_IN]->(movie) "
                  "RETURN movie, collect(person) AS actors", title=title).single()
```


### 12. Exercise: Add `person` pages
- Add links behind the movie cast list
- Add a new page for `/person/<name>`
- Add a new `person.html` template

```bash
FLASK_APP=answers/12/moviegraph flask run
```
