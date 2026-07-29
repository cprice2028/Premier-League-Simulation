import sqlite3
from pteams import teams
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
                """)
 connection.commit()
 connection.close()
for team in teams.keys():
 add_team(team,teams[team]["attack"],teams[team]["defense"])