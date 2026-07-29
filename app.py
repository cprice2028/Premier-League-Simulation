from flask import Flask, render_template
from database import *
from simulation import *
from pteams import teams

app = Flask(__name__)

teams_copy = teams.copy()

@app.route("/")
def home():
    standings = get_standings()
    recent_results = get_recent_results()
    return render_template("index.html", standings=standings, recent_results=recent_results)

@app.route("/results")
def results():
    return render_template("results.html")

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/team/<team_name>")
def team(team_name):
    return render_template("team.html", team_name=team_name)

if __name__ == "__main__":
    app.run(debug=True)
