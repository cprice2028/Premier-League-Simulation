from flask import *
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
        all_matches[x] = get_completed_matches_for_matchweek(x)
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
@app.route("/simulate_next_matchweek",methods=["POST"])
def simulate_next_matchweek():
    next_matchweek=get_next_matchweek()
    if next_matchweek==None:
        standings = get_standings()
        recent_results = get_recent_results()
        matchweek = get_current_matchweek()
        return render_template("index.html", standings=standings, recent_results=recent_results, matchweek=matchweek)
    matches_for_matchweek=get_matches_for_matchweek(next_matchweek)
    for match in matches_for_matchweek:
        home_goals_scored,away_goals_scored=simulate_game(match["home_team"],match["away_team"])
        save_result_and_update_teams(match["id"],match["home_team_id"],match["away_team_id"],home_goals_scored,away_goals_scored)
    update_current_matchweek(next_matchweek)
    standings = get_standings()
    recent_results = get_recent_results()
    matchweek = get_current_matchweek()
    return render_template("index.html", standings=standings, recent_results=recent_results, matchweek=matchweek)
@app.route("/simulate_rest_of_season",methods=["POST"])
def simulate_rest_of_season():
    while get_next_matchweek() is not None:
        simulate_next_matchweek()
    standings = get_standings()
    recent_results = get_recent_results()
    matchweek = get_current_matchweek()
    return render_template("index.html", standings=standings, recent_results=recent_results, matchweek=matchweek)
@app.route("/reset_season",methods=["POST"])
def reset_season_route():
    reset_season()
    standings = get_standings()
    recent_results = get_recent_results()
    matchweek = get_current_matchweek()
    return render_template("index.html", standings=standings, recent_results=recent_results, matchweek=matchweek)
@app.route("/history/<int:selected_matchweek>")
def history(selected_matchweek):
    matches=get_completed_matches_for_matchweek(selected_matchweek)
    return render_template("history.html",selected_matchweek=selected_matchweek,matches=matches)

if __name__ == "__main__":
    app.run(debug=True,port=5001)
