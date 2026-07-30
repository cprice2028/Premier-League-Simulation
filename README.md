# Premier League Season Simulator

A web application built with Python, Flask, SQLite, HTML, CSS, and JavaScript that simulates an entire Premier League season. Users can simulate one gameweek at a time, view the updated league table, browse match results week by week or as a whole, and explore each team's season.

## Features

- Live Premier League standings
- Simulate the next gameweek with realistic score generation
- Standings sorted by Premier League tiebreakers (points, goal difference, goals scored)
- View results from the latest gameweek
- Individual pages for all 20 Premier League clubs
- SQLite database stores season progress even after the server is restarted
- Reset the season and start a new simulation

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript

## How It Works

Each team is assigned attack and defensive ratings. When a gameweek is simulated, match scores are generated using these ratings along with random probability to create realistic outcomes.

After every match, the application updates:

- Games Played
- Wins, Draws, Losses
- Goals For and Against
- Goal Difference
- Points

The standings are then reordered according to the official Premier League rules.

## Running the Project

Note: Some commands may differ baced on the machine in use.

1. Open your browser and visit:

https://premier-league-simulation-production.up.railway.app/

Or

1. Clone the repository:

```
git clone <repository-url>
```
You might need to install git before doing this if you haven't already

2. Navigate into the project folder:

```
cd Premier-League-Simulation
```
3. Install Flask:

```
python -m pip install -r requirements.txt
```

4. Run the application:

```
python app.py
```

5. Open your browser and visit:

http://127.0.0.1:5000/

## Screenshots

### Home Page

![Home Page top](images/home1.png)
![Home Page bottom](images/home2.png)
Has the league table with all the basic statistics: points, wins, loses, draws, goals for, goals against, and goal differential. Also inludes the match scores for the current week of play.

### Team Page

![Team Page](images/team.png)
Provides all the teams match results aswell as their overall record and rank in the league.

### Latest Results

![Results](images/results.png)
Lists all the matches played in the season week by week.

### Matchweek History

![History](images/history.png)
Provides the match results for any match that you specify.

## Future Improvements

- Column in main table showing results from the teams last 5 games
- Player statistics
- Top scorers and assists tables
- Multiple seasons
- Injury and suspension simulation
- Adjustable team strength ratings

## Authors

- Charles Price
- Vihaan Madhavan