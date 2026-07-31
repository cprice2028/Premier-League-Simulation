import sqlite3
from pteams import teams
from simulation import generate_schedule
DATABASE = "premier_league.db"


def get_connection(): #gets connection to database
 connection = sqlite3.connect(DATABASE)
 connection.row_factory = sqlite3.Row
 connection.execute("PRAGMA foreign_keys = ON")
 return connection
def initialize_database():
 connection = get_connection()
 cursor = connection.cursor()

 cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        attack_rating REAL NOT NULL,
        defense_rating REAL NOT NULL,
        played INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        draws INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        goals_for INTEGER DEFAULT 0,
        goals_against INTEGER DEFAULT 0,
        points INTEGER DEFAULT 0
    )
 """)#creates a table that tracks data for each team

 cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matchweek INTEGER NOT NULL,
        home_team_id INTEGER NOT NULL,
        away_team_id INTEGER NOT NULL,
        home_goals INTEGER,
        away_goals INTEGER,
        played INTEGER DEFAULT 0,
        FOREIGN KEY (home_team_id) REFERENCES teams(id),
        FOREIGN KEY (away_team_id) REFERENCES teams(id)
    ) 
 """)#creates a table that tracks data for each match

 cursor.execute("""
    CREATE TABLE IF NOT EXISTS season (
        id INTEGER PRIMARY KEY,
        current_matchweek INTEGER DEFAULT 0,
        season_complete INTEGER DEFAULT 0
    )
    
 """) #tracks the seasons matchweek and if it has completed
 
 cursor.execute("""
    INSERT OR IGNORE INTO season
    (id, current_matchweek, season_complete)
    VALUES (1, 0, 0)
""") #creates a row with an empty season

 connection.commit()
 connection.close()
 
def add_team(name, attack_rating, defense_rating): #adds team to team table
 connection=get_connection()
 cursor=connection.cursor()
 
 cursor.execute("""
                INSERT or IGNORE INTO teams
                (name, attack_rating, defense_rating)
                VALUES (?,?,?)
                """,(name, attack_rating, defense_rating))
 connection.commit()
 connection.close()
def get_team_ids(): #gets the team id from the teams table
    connection = get_connection()
    rows = connection.execute("""
        SELECT id, name
        FROM teams
    """).fetchall()

    connection.close()

    return {
        row["name"]: row["id"]
        for row in rows
    }
def add_all_teams(): #adds every team to the team table, calling the add team method
    for team in teams.keys():
        add_team(
            team,
            teams[team]["attack"],
            teams[team]["defense"]
        )
        
def create_schedule(): # creates the schedule in matches, 380 matches to be exact, 38 for each team
    connection = get_connection()
    cursor = connection.cursor()

    existing_matches = cursor.execute("""
        SELECT COUNT(*) AS total
        FROM matches
    """).fetchone()["total"]

    if existing_matches > 0: #if matches already exist, do not add more
        connection.close()
        return

    team_ids = get_team_ids()
    schedule = generate_schedule(list(team_ids.keys())) #calls the generate schedule method in simulation.py

    for matchweek_number, matchweek in enumerate(schedule, start=1): #loops over all matches, starting at 1 up until 38
        for home_team, away_team in matchweek:
            cursor.execute("""
                INSERT INTO matches (
                    matchweek,
                    home_team_id,
                    away_team_id
                )
                VALUES (?, ?, ?)
            """, (
                matchweek_number,
                team_ids[home_team],
                team_ids[away_team]
            ))#inserts each match into matches

    connection.commit()
    connection.close()
def get_standings(): #gets current standings, ordering by the premier league table rules
    connection=get_connection()
    standings=connection.execute("""
        SELECT *,
            goals_for - goals_against AS goal_difference
        FROM teams
        ORDER by
            points DESC,
            goal_difference DESC,
            goals_for DESC,
            name ASC
        """).fetchall()
    connection.close()
    return standings

def get_next_matchweek(): #gets next unplayed matchweek number
    connection = get_connection()

    row = connection.execute("""
        SELECT MIN(matchweek) AS next_matchweek
        FROM matches
        WHERE played = 0
    """).fetchone()

    connection.close()
    return row["next_matchweek"]

def get_matches_for_matchweek(matchweek): #gets unplayed matches for matchweek
    connection=get_connection()
    matches=connection.execute("""
        SELECT
            matches.id,
            matches.matchweek,
            home.id AS home_team_id,
            home.name AS home_team,
            away.id AS away_team_id,
            away.name AS away_team,
            matches.home_goals,
            matches.away_goals
        FROM matches
        JOIN teams as home
            ON matches.home_team_id=home.id
        JOIN teams as away
            ON matches.away_team_id=away.id
        WHERE matches.matchweek = ?
            AND matches.played=0
                           """,(matchweek,)).fetchall()#joins team id from matches table and teams table
    connection.close()
    return matches
def get_completed_matches_for_matchweek(matchweek): #gets played matches for matchweek
    connection=get_connection()
    matches=connection.execute("""
        SELECT
            matches.id,
            matches.matchweek,
            home.id AS home_team_id,
            home.name AS home_team,
            away.id AS away_team_id,
            away.name AS away_team,
            matches.home_goals,
            matches.away_goals
        FROM matches
        JOIN teams as home
            ON matches.home_team_id=home.id
        JOIN teams as away
            ON matches.away_team_id=away.id
        WHERE matches.matchweek = ?
            AND matches.played=1
                            """,(matchweek,)).fetchall()#joins team id from matches table and teams table
    connection.close()
    return matches
def save_result_and_update_teams(match_id,home_team_id,away_team_id,home_goals,away_goals): #updates the match associated with match id
    if home_goals>away_goals:
        home_wins,home_draws,home_losses,home_points=1,0,0,3
        away_wins,away_draws,away_losses,away_points=0,0,1,0
    elif home_goals<away_goals:
        home_wins,home_draws,home_losses,home_points=0,0,1,0
        away_wins,away_draws,away_losses,away_points=1,0,0,3
    else:
        home_wins,home_draws,home_losses,home_points=0,1,0,1
        away_wins,away_draws,away_losses,away_points=0,1,0,1  #creates a tuple for the match state based on home and away scores
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE matches
        SET home_goals=?,
            away_goals=?,
            played=1
        WHERE id=?
            and played=0
        """,(home_goals,away_goals,match_id)) #updates the match in match table
    if cursor.rowcount==0:
        connection.close()
        return
    cursor.execute("""
        UPDATE teams
        SET goals_for=goals_for+?,
            played=played+1,
            goals_against=goals_against+?,
            wins=wins+?,
            draws=draws+?,
            losses=losses+?,
            points=points+?
        WHERE id=?
        """,(home_goals,away_goals,home_wins,home_draws,home_losses,home_points,home_team_id,)) #updates home team data in teams table
    cursor.execute("""
            UPDATE teams
            SET goals_for=goals_for+?,
                played=played+1,
                goals_against=goals_against+?,
                wins=wins+?,
                draws=draws+?,
                losses=losses+?,
                points=points+?
            WHERE id=?
            """,(away_goals,home_goals,away_wins,away_draws,away_losses,away_points,away_team_id,)) #updates away team data in teams table
    connection.commit()
    connection.close()

def update_current_matchweek(matchweek): #updates current matchweek in the season
    connection=get_connection()
    cursor=connection.cursor()
    remaining=cursor.execute("""
        SELECT COUNT(*) AS total
        FROM matches
        WHERE played=0
        """).fetchone()
    remaining_matches=remaining["total"] #if there are any unplayed matches, then the season is complete
    season_complete=0
    if remaining_matches==0:
        season_complete=1
    cursor.execute("""
                    UPDATE season
                    SET current_matchweek=?,
                        season_complete=?
                    WHERE id=? 
                    """,(matchweek,season_complete,1)) #updates the current matchweek in seasons table, if the season is complete, update that column
    connection.commit()
    connection.close()
            

def get_current_matchweek(): #gets current matchweek from seasons table
    connection=get_connection()
    row = connection.execute("""
            SELECT current_matchweek as current_matchweek
            FROM season
            WHERE id=1
            """).fetchone()
    connection.close()
    return row["current_matchweek"]

def get_recent_results(): #gets the last 10 played matches, last matchweek
    connection=get_connection()
    row=connection.execute("""
        SELECT 
            matches.id,
            matches.matchweek,
            home.name AS home_team,
            away.name AS away_team,
            matches.home_goals,
            matches.away_goals
        FROM matches
        JOIN teams as home
            ON matches.home_team_id = home.id
        JOIN teams as away
            ON matches.away_team_id = away.id
        WHERE matches.played=1
        ORDER by
            matches.matchweek DESC, matches.id DESC
        LIMIT 10    
        """).fetchall() #gets data from matches table, orders them by decreasing order in terms of matchweek, then limits the games to the last 10
    connection.close()
    return row
    

def get_team_matches(team_name): #gets matches for each team
    connection = get_connection()
    matches = connection.execute("""
        SELECT
            matches.id,
            matches.matchweek,
            home.name AS home_team,
            away.name AS away_team,
            matches.home_goals,
            matches.away_goals,
            matches.played
        FROM matches
        JOIN teams as home
            ON matches.home_team_id = home.id
        JOIN teams as away
            ON matches.away_team_id = away.id
        WHERE home.name = ?
            OR away.name = ?
        ORDER BY matches.matchweek
    """, (team_name, team_name)).fetchall() #gets match data for every home and away game with the specified team
    connection.close()
    return matches

def reset_season(): #sets all season data to 0 or null, except for the team data needed to create schedule and determine a single matches score
    connection=get_connection()
    cursor=connection.cursor()
    cursor.execute("""
        UPDATE teams
        SET played=0,
            wins=0,
            draws=0,
            losses=0,
            goals_for=0,
            goals_against=0,
            points=0
        """)
    cursor.execute("""
        UPDATE matches
        SET home_goals=NULL,
            away_goals=NULL,
            played=0
        """)
    cursor.execute("""
        UPDATE season
        SET current_matchweek=0,
            season_complete=0
        WHERE id=1
        """)
    connection.commit()
    connection.close()