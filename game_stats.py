import json
from os.path import dirname

filename = 'high_score.json'

class GameStats:
    """Track statistics for Alien Invasion."""
    
    def __init__(self, ai_game):
        """Initialize the stats."""
        self.settings = ai_game.settings
        self.reset_stats()
        
        #start the game in an inactive state..
        self.game_active = False

        #High score should never be reset.
        with open(dirname(__file__) + "/" + filename) as f:
            self.high_score = json.load(f)
    
    def reset_stats(self):
        """Initialize the stats that can be changed during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1