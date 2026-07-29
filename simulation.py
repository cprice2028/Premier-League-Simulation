import random
import math
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
    home_expected_goals=home_ex(home_attack,away_defense)
    away_expected_goals=home_ex(home_defense,away_attack)
    home_goals=poisson_goals(home_expected_goals)
    away_goals=poisson_goals(away_expected_goals)
    return (home_goals,away_goals)
    
def home_ex(home,away):
    return 1.4*home*away*1.15
def away_ex(home,away):
    return 1.4*home*away
def poisson_goals(expected_goals):
    attempts=0
    probability=1
    limit=math.exp(-expected_goals)
    while probability>limit:
        attempts+=1
        probability*=random.random()
    return attempts-1
def generate_schedule(team):
    team_copy=team.copy()
    if len(team_copy)%2==1:
        team_copy.append(None)
    matchweeks_first_half=[]
    for matchweek in range(len(team)-1):
        matches=[]
        for index in range(len(team)//2):
            home_team=team_copy[index]
            away_team=team_copy[len(team)-1-index]
            if home_team is not None and away_team is not None:
                if matchweek%2==0:
                    matches.append(home_team,away_team)
                else:
                    matches.append(away_team,home_team)
        matchweeks_first_half.append(matches)
        team_copy = [team_copy[0]] + [team_copy[-1]] + team_copy[1:-1]
    matchweeks_second_half=[]
    for matchweek in matchweeks_first_half:
        reversed_matches=[]
        for home_team, away_team in matchweek:
            reversed_matches.append(away_team,home_team)
        matchweeks_second_half.append(reversed_matches)
    return matchweeks_first_half+matchweeks_second_half
