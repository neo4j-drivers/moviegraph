#!/usr/bin/env python
# coding: utf-8


from flask import Flask, abort, render_template, request
from neo4j.v1 import GraphDatabase


app = Flask(__name__)

# Set up a driver for the local graph database.
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))


def match_movies(tx, q):
    if q:
        return tx.run("MATCH (movie:Movie) WHERE toLower(movie.title) CONTAINS toLower($term) "
                      "RETURN movie ORDER BY movie.year DESCENDING, movie.title ASCENDING", term=q).value()
    else:
        return []


def match_movie(tx, title):
    return tx.run("MATCH (movie:Movie) WHERE movie.title = $title "
                  "OPTIONAL MATCH (person)-[:ACTED_IN]->(movie) "
                  "RETURN movie, collect(person) AS actors", title=title).single()


@app.route("/")
def get_index():
    """ Show the index page.
    """
    search_term = request.args.get("q", "")
    with driver.session() as session:
        movies = session.read_transaction(match_movies, q=search_term)
    return render_template("index.html", movies=movies, q=search_term)


@app.route("/movie/<title>")
def get_movie(title):
    """ Display details of a particular movie.
    """
    with driver.session() as session:
        record = session.read_transaction(match_movie, title)
    if record is None:
        abort(404, "Movie not found")
    return render_template("movie.html", movie=record["movie"], actors=record["actors"])


if __name__ == "__main__":
    app.run(debug=True)
