import random
import math
from pteams import teams

def simulate_game(home, away): #simulates a single game and returns the score of the home team followed by the away team
    home_attack = teams[home]["attack"]
    home_defense = teams[home]["defense"]
    away_attack = teams[away]["attack"]
    away_defense = teams[away]["defense"]
    home_expected_goals=home_ex(home_attack,away_defense)
    away_expected_goals=away_ex(home_defense,away_attack)
    home_goals=actual_goals(home_expected_goals)
    away_goals=actual_goals(away_expected_goals)
    return (home_goals,away_goals)

#calculates home and away expected goals, giving a slight home game advantage
def home_ex(home,away): 
    return 1.4*home*away*1.15
def away_ex(home,away):
    return 1.4*home*away

def actual_goals(expected_goals):
    attempts=0
    probability=1
    limit=math.exp(-expected_goals) #if the team has a high xg, then hitting the limit will be very hard, inverse for a low xg
    # keeps multiplying probability down until it drops below the limit
    while probability>limit:
        attempts+=1 #increases attempts
        probability*=random.random()*.75   #makes the probability smaller reducing by a random amount, trying to reach the limit. multiplying by 0.75reduces amount of attempts, as the probability reduces faster, makes games center around 1-1, 2-1. more realistic soccer games
    return attempts-1 #returns the number of attempts needed to reach the limit, which we use as the actual amount of goals scored
def generate_schedule(team): #generates a master premier league schedule
    team_copy=team.copy() #creates a shallow copy of the teams dictionary
    if len(team_copy)%2==1: #if the amount of teams is odd, make it even, just for safety
        team_copy.append(None)
    matchweeks_first_half=[]
    for matchweek in range(len(team_copy)-1):
        matches=[] #creates the first half of the schedule, until matchweek 19
        for index in range(len(team_copy)//2):
            #ensures that each team doesnt play itself
            home_team=team_copy[index] 
            away_team=team_copy[len(team_copy)-1-index]
            #make sure teams exist
            if home_team is not None and away_team is not None:
                if matchweek%2==0: #every other matchweek switch the home and away team, make sure teams alternate playing home or away
                    #adds the match to the match list
                    matches.append((home_team,away_team))
                else:
                    matches.append((away_team,home_team))
        matchweeks_first_half.append(matches)
        team_copy = [team_copy[0]] + [team_copy[-1]] + team_copy[1:-1] #moves the last team to the second index
    matchweeks_second_half=[]
    for matchweek in matchweeks_first_half:
        reversed_matches=[]
        for home_team, away_team in matchweek:
            reversed_matches.append((away_team,home_team)) #reverses each game, so each fixture is played both home and away
        matchweeks_second_half.append(reversed_matches)
    return matchweeks_first_half+matchweeks_second_half #combine both halves of the season to create one schedule
