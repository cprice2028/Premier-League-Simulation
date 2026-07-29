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
    matchweek = get_current_matchweek()
    return render_template("index.html", standings=standings, recent_results=recent_results, matchweek=matchweek)

@app.route("/results")
def results():
    matchweek = get_current_matchweek()
    all_matches = {}
    for x in range(1, matchweek + 1):
        all_matches[x] = get_matches_for_matchweek(x)
    return render_template("results.html", all_matches=all_matches)

@app.route("/team/<team_name>")
def team(team_name):
    matches = get_team_matches(team_name)
    standings = get_standings()
    team_info = None
    team_rank = None

    for rank, team in enumerate(standings, start=1):
        if team["name"] == team_name:
            team_info = team
            team_rank = rank
            break
    
    return render_template("team.html", team_name=team_name, matches=matches, team_info=team_info, team_rank=team_rank)

@app.route("/history")
def history():
    return render_template("history.html")

if __name__ == "__main__":
    setup_database()
    app.run(debug=True)
