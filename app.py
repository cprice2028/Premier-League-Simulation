from flask import *
from database import *
from simulation import *
import sqlite3
import os

app = Flask(__name__)
connection=get_connection()
initialize_database(connection)
add_all_teams(connection)
create_schedule(connection)
@app.route("/")
def home(): #home route renders index.html with current standings, results, current matchweek, and passes the name of the winner
    standings = get_standings(connection)
    recent_results = get_recent_results(connection)
    matchweek = get_current_matchweek(connection)
    winner=None
    if get_next_matchweek(connection) is None and len(standings) > 0:
        winner = standings[0]["name"]
    return render_template("index.html", standings=standings, recent_results=recent_results, matchweek=matchweek,winner=winner)
@app.route("/results")
def results(): #displays all matches in every matchweek, if the matchweek hasnt been played, just simply get the unplayed matches
    matchweek = get_current_matchweek(connection)
    all_matches = {}
    for x in range(1, matchweek + 1):
        all_matches[x] = get_completed_matches_for_matchweek(connection,x)
    for y in range(matchweek + 1, 39):
        all_matches[y] = get_matches_for_matchweek(connection,y)
    return render_template("results.html", all_matches=all_matches)

@app.route("/team/<team_name>")
def team(team_name): #this displays data for each specific team
    matches = get_team_matches(connection,team_name)
    standings = get_standings(connection)
    team_info = None
    team_rank = None

    for rank, team in enumerate(standings, start=1): #gets team info from standings, like their place in the table and the amount of games won, lost, or drawn
        if team["name"] == team_name:
            team_info = team
            team_rank = rank
            break
    
    return render_template("team.html", team_name=team_name, matches=matches, team_info=team_info, team_rank=team_rank)
@app.route("/simulate_next_matchweek",methods=["POST"])
def simulate_next_matchweek(): #simulates one matchweek only, calling simulate_one_matchweek once
    simulate_one_matchweek()
    return redirect(url_for("home"))
def simulate_one_matchweek(): #simulates the next unplayed matchweek
    next_matchweek=get_next_matchweek(connection)
    if next_matchweek is None: #if the season is complete, dont continue
        return
    matches_for_matchweek=get_matches_for_matchweek(connection,next_matchweek) #get unplayed matches for matchweek
    for match in matches_for_matchweek: 
        home_goals_scored,away_goals_scored=simulate_game(match["home_team"],match["away_team"]) #simulates each game in the specific matchweek
        save_result_and_update_teams(connection,match["id"],match["home_team_id"],match["away_team_id"],home_goals_scored,away_goals_scored) #updates the database
    update_current_matchweek(connection,next_matchweek) #updates season table
@app.route("/simulate_rest_of_season",methods=["POST"])
def simulate_rest_of_season():
    while get_next_matchweek(connection) is not None: #loops until season has ended
        simulate_one_matchweek()
    return redirect(url_for("home"))
@app.route("/reset_season",methods=["POST"])
def reset_season_route(): #calls reset season method in database.py
    reset_season(connection)
    return redirect(url_for("home"))
@app.route("/history/<int:selected_matchweek>")
def history(selected_matchweek): 
    matchweek = get_current_matchweek(connection)
    if selected_matchweek <= matchweek: #if the matchweek has already been played
        matches=get_completed_matches_for_matchweek(connection,selected_matchweek) #get the played matches
    else:
        matches=get_matches_for_matchweek(connection,selected_matchweek) #get the unplayed matches
    return render_template("history.html",selected_matchweek=selected_matchweek,matches=matches)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000)) #accept incoming connections from any network interface
    app.run(host="0.0.0.0", port=port)
