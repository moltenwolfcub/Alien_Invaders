class Settings:
    """A class to store the game's settings."""

    def __init__(self):
        """Initialize the games settings."""
        #screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_colour = (30, 40, 70) #30 40 70

        #Ship settings

        self.ship_limit = 3
        self.ship_speed = 1.6

        #Bullet settings

        self.bullet_width = 5
        self.bullet_height = 15
        self.bullet_colour = (255, 100, 0)
        self.bullet_speed = 4

        #alien settings

        self.fleet_drop_speed = 10

        #how quickly the game speeds up
        self.speedup_scale = 1.3

        #how quickly the alien point values increase
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """initialize settings that change throughout the game."""
        self.alien_speed = 0.2
        self.bullets_allowed = 4

        self.fleet_direction = 1        #fleet_direction of 1 represents right; -1 represents left.
        self.alien_points = 50

    def increase_speed(self):
        """Increase speed settings and alien points."""
        self.alien_speed *= self.speedup_scale
        self.bullets_allowed +=1
        self.alien_points = int(self.alien_points * self.score_scale)
