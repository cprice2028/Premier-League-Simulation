import sqlite3
from pteams import teams
from simulation import generate_schedule
DATABASE = "premier_league.db"


def get_connection():
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
 """)

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
 """)

 cursor.execute("""
    CREATE TABLE IF NOT EXISTS season (
        id INTEGER PRIMARY KEY,
        current_matchweek INTEGER DEFAULT 0,
        season_complete INTEGER DEFAULT 0
    )
    
 """)
 
 cursor.execute("""
    INSERT OR IGNORE INTO season
    (id, current_matchweek, season_complete)
    VALUES (1, 0, 0)
""")

 connection.commit()
 connection.close()
 
def add_team(name, attack_rating, defense_rating):
 connection=get_connection()
 cursor=connection.cursor()
 
 cursor.execute("""
                INSERT or IGNORE INTO teams
                (name, attack_rating, defense_rating)
                VALUES (?,?,?)
                """,(name, attack_rating, defense_rating))
 connection.commit()
 connection.close()
def get_team_ids():
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
def add_all_teams():
    for team in teams.keys():
        add_team(
            team,
            teams[team]["attack"],
            teams[team]["defense"]
        )
        
def create_schedule():
    connection = get_connection()
    cursor = connection.cursor()

    existing_matches = cursor.execute("""
        SELECT COUNT(*) AS total
        FROM matches
    """).fetchone()["total"]

    if existing_matches > 0:
        connection.close()
        return

    team_ids = get_team_ids()
    schedule = generate_schedule(list(team_ids.keys()))

    for matchweek_number, matchweek in enumerate(schedule, start=1):
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
            ))

    connection.commit()
    connection.close()
def get_standings():
    connection=get_connection()
    standings=connection.execute("""
        SELECT *,
            goals_for - goals_against = goal_difference
            FROM teams
        ORDER by
            points DESC
            goal_difference DESC
            goals_for DESC
            name ASC
                                 """).fetchall()
    connection.close()
    return standings

def get_next_matchweek():
    connection = get_connection()

    row = connection.execute("""
        SELECT MIN(matchweek) AS next_matchweek
        FROM matches
        WHERE played = 0
    """).fetchone()

    connection.close()
    return row["next_matchweek"]

def get_matches_for_matchweek(matchweek):
    connection=get_connection()
    matches=connection.execute("""
        SELECT
            matches.id,
            matches.matchweek,
            
            home.id AS home_team_id,
            home.name AS home_team,
            home.attack_rating AS home_attack,
            home.defense_rating AS home_defense,
            
            away.id AS away_team_id,
            away.name AS away_team,
            away.attack_rating AS away_attack,
            away.defense_rating AS away_defense,
        
        FROM matches
        
        JOIN teams as home
            ON matches.home_team_id=home.id
        JOIN teams as away
            ON matches.away_team_id=away.id
        WHERE matches.matchweek = ?
            AND matches.played=0
                           """,(matchweek,)).fetchall()
    connection.close()
    return matches

def save_result_and_update_teams(match_id,home_team_id,away_team_id,home_goals,away_goals):
    if home_goals>away_goals:
        home_wins,home_draws,home_losses,home_points=1,0,0,3
        away_wins,away_draws,away_losses,away_points=0,0,1,0
    elif home_goals<away_goals:
        home_wins,home_draws,home_losses,home_points=0,0,1,0
        away_wins,away_draws,away_losses,away_points=1,0,0,3
    else:
        home_wins,home_draws,home_losses,home_points=0,1,0,1
        away_wins,away_draws,away_losses,away_points=0,1,0,1  
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE matches
        SET home_goals=?,
            away_goals=?,
            played=1
        WHERE id=?
            and played=0
        """,(home_goals,away_goals,match_id))
    if cursor.rowcount()==0:
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
        """,(home_goals,away_goals,home_wins,home_draws,home_losses,home_points,home_team_id,))
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
            """,(away_goals,home_goals,away_wins,away_draws,away_losses,away_points,away_team_id,))
    connection.commit()
    connection.close()

def update_current_matchweek(matchweek):
    '''Open a database connection and cursor.
        Update the row in season where id = 1.
        Set current_matchweek equal to the supplied matchweek.
        Check whether matchweek 38 has been completed.
        Set season_complete to 1 when no unplayed matches remain; otherwise leave it as 0.
        Commit the change and close the connection.'''
    connection=get_connection()
    cursor=connection.cursor()
    cursor.execute("""
                UPDATE season
                SET current_matchweek=?
                WHERE id=?
                """,(matchweek,1))
    matches=get_matches_for_matchweek(matchweek)
    if len(matches)==0:
        cursor.execute("""
                        UPDATE season
                        SET season_complete=1
                        WHERE id=?
                        """,(1,))
    connection.commit()
    connection.close()
            



def get_recent_results():
    '''Open a database connection.
        Select only matches where played = 1.
        Join the teams table twice:
        Once to obtain the home team’s name.
        Once to obtain the away team’s name.
        Retrieve the matchweek, team names, and both scores.
        Sort with the newest matchweek first.
        Use match ID as a secondary sort so the order is consistent.
        Limit the result to 10 matches if the homepage shows the 10 most recent games.
        Fetch the rows, close the connection, and return them.'''

def reset_season():
    '''Open one database connection and cursor.
        Reset every team’s statistics to zero:
        Played
        Wins
        Draws
        Losses
        Goals for
        Goals against
        Points
        Reset every match:
        Set home_goals to NULL.
        Set away_goals to NULL.
        Set played to 0.
        Reset the season row:
        Set current_matchweek to 0.
        Set season_complete to 0.
        Do not delete the teams or fixture schedule.
        Commit once after all reset operations.
        Close the connection.'''