import flask

import main

app = flask.Flask(__name__)

@app.route('/')
def main_page():
    return flask.render_template("main.html")

@app.route('/less', methods=['POST'])
def less_page():
    query = flask.request.form['query']
    results = main.the_output_is_less_than_price(query)
    return flask.render_template("index.html", name = "Товары, цена которых меньше: " + query + " рублей", result = results)

@app.route('/all')
def all_page():
    results = main.print_all()
    return flask.render_template("index.html", name = "Все товары", result = results)


@app.route('/search', methods=['POST'])
def search():
    query = flask.request.form['query']
    results = main.searchfunc(query)
    return flask.render_template('index.html',name = "Результаты поиска по запросу: " + query, result = results)