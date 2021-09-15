import sys
import json
from time import sleep

import pygame
from pygame.mixer import Sound
from os.path import dirname

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion!")

        #create an instance to store the games stats.
        #   and create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        #make the play button
        self.play_button = Button(self, "Play")

        #make sounds
        self.hit_sound = Sound('sounds/hit_sound.wav')
        self.shoot_sound = Sound('sounds/shoot_sound.wav')
        self.game_over_sound = Sound('sounds/game_over.wav')
        self.explode = Sound('sounds/explode.wav')
        self.start = Sound('sounds/start.wav')
        pygame.mixer.music.load("sounds/background.mp3")
        pygame.mixer.music.set_volume(0.2)

        #game_over file
        self.filename = 'high_score.json'
    
    def _check_events(self):
        """watch for keyboard and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                with open((dirname(__file__) + "/" + self.filename), 'w') as f:
                    json.dump(self.stats.high_score, f)
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
    
    def _check_keydown_events(self, event):
        """respond to key presses."""
        if event.key == pygame.K_d:
            self.ship.moving_right = True
        elif event.key == pygame.K_a:
            self.ship.moving_left = True
        elif event.key == pygame.K_ESCAPE:
            with open((dirname(__file__) + "/" + self.filename), 'w') as f:
                json.dump(self.stats.high_score, f)
            sys.exit()
        elif event.key == pygame.K_SPACE or event.key == pygame.K_w:
            self._fire_bullet()        

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            self.shoot_sound.play()
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _check_keyup_events(self, event):
        if event.key == pygame.K_d:
            self.ship.moving_right = False
        elif event.key == pygame.K_a:
            self.ship.moving_left = False
    
    def _update_screen(self):
        """Update the images on screen, and flip to a new screen."""
        self.screen.fill(self.settings.bg_colour)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        #Draw the scoreboard information
        self.sb.show_score()

        #Draw the button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collision"""
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            self.hit_sound.play()
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            #increase the level
            self.stats.level += 1
            self.sb.prep_level()

    def _update_bullets(self):
        """Update the positon of the bullets and delete old bullets."""
        #update bullet positions
        self.bullets.update()

        #Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()
    
    def _create_fleet(self):
        """Create the fleet of aliens."""
        #Create an alien and fine the number of aliens in a row.
        #spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        #Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        #create the full fleet of aliens
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
    
    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien_height * row_number
        self.aliens.add(alien)

    def _update_aliens(self):
        """check if the fleet are at the edge then update the position of all the aliens."""
        self._check_fleet_edges()
        self.aliens.update()

        #look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        #look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()
    
    def _check_fleet_edges(self):
        """respond appropriately if any aliens have reached the edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""

        self.stats.ships_left -= 1
        self.sb.prep_ships()
        pygame.mixer.music.stop()
        sleep(0.5)


        if self.stats.ships_left > 0:
            #play sound
            self.explode.play()
            pygame.mixer.music.play(-1) 

            # update the visuals.

            #get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            #create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            #pause.
            sleep(0.5)
        
        else:
            self.game_over_sound.play()
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """check if any aliens have reached the bottom."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #treat this the same as a ship getting hit
                self._ship_hit()
                break

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.start.play()
            sleep(0.5)
            pygame.mixer.music.play(-1)        
            self.settings.initialize_dynamic_settings()
            
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            self.aliens.empty()

            pygame.mouse.set_visible(False)

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

if __name__=='__main__':
    #make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
