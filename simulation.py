import random
from pteams import teams


def simulate_game(home, away):
    """
    Simulates a single game between two teams using their strengths.

    Parameters:
        team1 (str): Name of the first team.
        team2 (str): Name of the second team.

    Returns:
        tuple: The name of the team that wins the game.
    """
    home_attack = teams[home]["attack"]
    home_defense = teams[home]["defense"]
    away_attack = teams[away]["attack"]
    away_defense = teams[away]["defense"]
