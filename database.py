import sqlite3
from pteams import teams
from simulation import generate_schedule
DATABASE = "premier_league.db"


def get_connection():
 connection = sqlite3.connect(DATABASE)
 connection.row_factory = sqlite3.Row
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
        gameweek INTEGER NOT NULL,
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
        current_gameweek INTEGER DEFAULT 0,
        season_complete INTEGER DEFAULT 0
    )
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
    initialize_database()
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

    for gameweek_number, gameweek in enumerate(schedule, start=1):
        for home_team, away_team in gameweek:
            cursor.execute("""
                INSERT INTO matches (
                    gameweek,
                    home_team_id,
                    away_team_id
                )
                VALUES (?, ?, ?)
            """, (
                gameweek_number,
                team_ids[home_team],
                team_ids[away_team]
            ))

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
def get_standings():
    pass

def get_next_gameweek():
    connection = get_connection()

    row = connection.execute("""
        SELECT MIN(gameweek) AS next_gameweek
        FROM matches
        WHERE played = 0
    """).fetchone()

    connection.close()
    return row["next_gameweek"]

def get_matches_for_gameweek(gameweek):
    connection=get_connection()
    matches=connection.execute("""
        SELECT
        matches.id
        matches.gameweek
        
        home.id AS home_team_id
        home.name AS home_team
        home.attack AS home_attack
        home.defense AS home_defense
        
        away.id AS away_team_id
        away.name AS away_team
        away.attack AS away_attack
        away.defense AS away_defense
        
        FROM matches
        
        JOIN teams as home
            ON matches.home_team_id=home.id
        JOIN teams as away
            ON matches.away_team_id=away.id
        WHERE matches.gameweek = ?
            AND matches.played=0
                           """,(gameweek)).fetchall()
    connection.close()
    return matches

def save_result_and_update_teams(match_id,home_team_id,away_team_id,home_goals,away_goal,):
    pass

def update_current_gameweek(gameweek):
    pass

def get_recent_results():
    pass

def reset_season():
    pass