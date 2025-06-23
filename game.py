import pygame
import random
import math

from sprite_handler.spriteHandler import SpriteHandler
from resource_manager.resourceManager import ResourceManager
from towers.main_tower import MainTower
from towers.fire_tower import FireTower
from towers.archer_tower import ArcherTower
from path_finder import Pathfinder, matrix
from enemies.orc import Orc
from enemies.head import HeadMonster
from enemies.skeleton_monster import SkeletonMonster
from enemies.stone_monster import StoneMonster
from tower_selection_panel import TowerSelectionPanel

class Game:
    def __init__(self) -> None:
        pygame.init()

        # Initialize the mixer for audio
        pygame.mixer.init()
        pygame.mixer.music.load('the-hermit-nostalgic-ancient-harp-259286.mp3')
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)

        pygame.display.set_caption("Werian - Tower Defense")
        self.screen_info = pygame.display.Info()
        self.width, self.height = self.screen_info.current_w, self.screen_info.current_h
        #self.win = pygame.display.set_mode((self.width, self.height))
        self.win = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)

        # Cell sizes (for your pathfinder matrix)
        self.cell_width = math.ceil((self.width / 1920) * 40)
        self.cell_height = math.ceil((self.height / 1080) * 40)

        # Init pathfinder
        self.pathfinder = Pathfinder(
            matrix=matrix,
            cell_width=self.cell_width,
            cell_height=self.cell_height
        )

        # Load and scale the background
        self.bg = pygame.image.load("assets/td-tilesets1-2/tower-defense-game-tilesets/PNG/game_background_3/game_background_3.png")
        self.bg = pygame.transform.scale(self.bg, (self.width, self.height))

        # Enemies
        self.enemies = []

        # Towers
        self.ma_sw = 1440
        self.ma_sh = 900
        self.towers = [
            MainTower(
                int((830 / self.ma_sw) * self.width), 
                int((370 / self.ma_sh) * self.height),
                int((166 / self.ma_sw) * self.width), 
                int((181 / self.ma_sh) * self.height)
            )
        ]
        
        # Initialize resource manager
        self.points_manager = ResourceManager(initial_points=0)
        self.gold_manager = ResourceManager(initial_points=100)
        
        # Initialize enemy sprites
        enemy_sprites = SpriteHandler.load_sprites(
            ["assets/2d-monster-sprites/PNG/1/1_enemies_1_run_{:03}.png".format(i) for i in range(20)],
            50, 50
        )

        # Spawn timing variables
        self.last_spawn_time = 0
        self.spawn_interval = 4000

        # Tower placement variables
        self.placing_tower = False
        self.tower_preview = None
        self.tower_type = None

        # State machine
        self.state = 'start'
        
        self.last_check_new_path = None
        self.new_path_interval = 2000
        self.last_wave = 0
        self.wave_interval = 40000

        # Create the selection panel
        self.tower_panel = TowerSelectionPanel(self.width, self.height)
        self.selected_tower = None
        # Wave counter
        self.wave_count = 1

    def display_start_menu(self):
        # Fonts
        title_font = pygame.font.SysFont(None, 240)
        button_font = pygame.font.SysFont(None, 64)

        # Render texts
        title_text = title_font.render("Werian", True, (255, 255, 255))
        start_text = button_font.render("Start", True, (255, 255, 255))
        quit_text = button_font.render("Quit", True, (255, 255, 255))

        # Button dimensions
        button_width, button_height = 200, 80
        start_button_x = self.width // 2 - button_width // 2
        start_button_y = int(self.height * 0.6)
        quit_button_x = self.width // 2 - button_width // 2
        quit_button_y = int(self.height * 0.72)

        # Title positioning
        title_x = self.width // 2 - title_text.get_width() // 2
        title_y = self.height // 2 - title_text.get_height() // 2 - 100  # Slightly above center

        while self.state == 'start':
            # Draw background
            self.win.blit(self.bg, (0, 0))

            # Blit the "Werian" text on top of its rectangle
            self.win.blit(title_text, (title_x, title_y))

            # Start button
            pygame.draw.rect(self.win, (139, 69, 19), (start_button_x, start_button_y, button_width, button_height))
            pygame.draw.rect(self.win, (0, 0, 0), (start_button_x, start_button_y, button_width, button_height), 3)
            self.win.blit(start_text, (
                start_button_x + button_width // 2 - start_text.get_width() // 2,
                start_button_y + button_height // 2 - start_text.get_height() // 2)
            )

            # Quit button
            pygame.draw.rect(self.win, (139, 69, 19), (quit_button_x, quit_button_y, button_width, button_height))
            pygame.draw.rect(self.win, (0, 0, 0), (quit_button_x, quit_button_y, button_width, button_height), 3)
            self.win.blit(quit_text, (
                quit_button_x + button_width // 2 - quit_text.get_width() // 2,
                quit_button_y + button_height // 2 - quit_text.get_height() // 2)
            )

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    # Start button click
                    if (start_button_x <= mx <= start_button_x + button_width and
                        start_button_y <= my <= start_button_y + button_height):
                        self.state = 'running'
                    # Quit button click
                    elif (quit_button_x <= mx <= quit_button_x + button_width and
                        quit_button_y <= my <= quit_button_y + button_height):
                        pygame.mixer.music.stop()
                        pygame.quit()
                        exit()

    def spawn_enemy(self):
        current_time = pygame.time.get_ticks()

        # Check if enough time has passed to start a new wave
        if current_time - self.last_wave >= self.wave_interval:
            # -------------------------------
            # NEW: increment wave count
            # -------------------------------
            self.wave_count += 1  # <--- Increase wave counter
            
            self.spawn_interval = max(self.spawn_interval - 100, 100)
            x, y = random.choice([(50, 2), (0, 20)])
            self.enemies.append(StoneMonster(x, y, self.cell_width, self.cell_height))
            self.last_wave = current_time
            self.wave_interval = max(self.wave_interval - 1000, 2000)

            if current_time >= 60000:
                x, y = random.choice([(40, 26), (0, 20)])
                self.enemies.append(SkeletonMonster(x, y, self.cell_width, self.cell_height)) 

        spawn_points = [(0, 20), (0, 16), (50, 22), (50, 25)]
        x, y = random.choice(spawn_points)
        possible_enemies = [
            Orc(x, y, self.cell_width, self.cell_height),
            HeadMonster(x, y, self.cell_width, self.cell_height),
        ]
        self.enemies.append(random.choice(possible_enemies))

    def display_pause_menu(self):
        paused = True
        font = pygame.font.SysFont(None, 128)
        pause_text = font.render("Paused", True, (255, 255, 255))
        pause_text_outline = font.render("Paused", True, (0, 0, 0))
        button_font = pygame.font.SysFont(None, 64)

        button_width, button_height = 200, 80
        button_x = self.width // 2 - button_width - 10
        button_y = self.height // 2 + pause_text.get_height() // 2 + 20
        retry_text = button_font.render("Retry", True, (255, 255, 255))

        button2_x = self.width // 2 + 10
        quit_text = button_font.render("Quit", True, (255, 255, 255))

        while paused:
            self.win.blit(self.bg, (0, 0))
            text_x = self.width // 2 - pause_text.get_width() // 2
            text_y = self.height // 2 - pause_text.get_height()
            offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -2), (-2, 0), (2, 0), (0, 2)]
            for dx, dy in offsets:
                self.win.blit(pause_text_outline, (text_x + dx, text_y + dy))

            self.win.blit(pause_text, (text_x, text_y))

            pygame.draw.rect(self.win, (139, 69, 19), (button_x, button_y, button_width, button_height))
            pygame.draw.rect(self.win, (0, 0, 0), (button_x, button_y, button_width, button_height), 3)
            self.win.blit(retry_text, (
                button_x + button_width // 2 - retry_text.get_width() // 2,
                button_y + button_height // 2 - retry_text.get_height() // 2)
            )

            pygame.draw.rect(self.win, (139, 69, 19), (button2_x, button_y, button_width, button_height))
            pygame.draw.rect(self.win, (0, 0, 0), (button2_x, button_y, button_width, button_height), 3)
            self.win.blit(quit_text, (
                button2_x + button_width // 2 - quit_text.get_width() // 2,
                button_y + button_height // 2 - quit_text.get_height() // 2)
            )

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                        self.state = 'running'
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    # Retry
                    if button_x <= mx <= button_x + button_width and button_y <= my <= button_y + button_height:
                        print("Retry button clicked! Restarting the game...")
                        self.__init__()  # Reinitialize
                        self.run()
                        return
                    # Quit
                    elif button2_x <= mx <= button2_x + button_width and button_y <= my <= button_y + button_height:
                        print("Quit button clicked! Exiting the game...")
                        pygame.mixer.music.stop()
                        pygame.quit()
                        exit()

    def can_place_tower(self, x, y):
        grid_x = x // self.cell_width
        grid_y = y // self.cell_height

        # Must be a cell=1 in matrix to place
        if matrix[grid_y][grid_x] != 1:
            return False

        # Check collisions with existing towers
        for tower in self.towers:
            tower_rect = pygame.Rect(tower.x, tower.y, tower.width, tower.height)
            placement_rect = pygame.Rect(
                x - self.cell_width // 2, 
                y - self.cell_height // 2, 
                self.cell_width, 
                self.cell_height
            )
            if tower_rect.colliderect(placement_rect):
                return False

        return True

    def run(self):
        clock = pygame.time.Clock()
        while True:
            if self.state == 'start':
                self.display_start_menu()

            if self.state == 'running':
                clock.tick(30)
                self.update()
                self.draw()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.mixer.music.stop()
                        pygame.quit()
                        exit()

                    # -- Let the panel handle the event first
                    panel_handled, selected_tower_cls, tower_price = self.tower_panel.handle_event(event)
                    if panel_handled:
                        # We clicked inside the panel
                        if selected_tower_cls:
                            # The user clicked on a specific tower icon
                            self.placing_tower = True
                            self.tower_type = selected_tower_cls
                            self.tower_price = tower_price  # store the price if needed

                            # Create the preview tower object
                            pos = pygame.mouse.get_pos()
                            self.tower_preview = self.tower_type(
                                pos[0], pos[1],
                                int((166 / self.ma_sw) * self.width),
                                int((181 / self.ma_sh) * self.height),
                                attack_range=int(self.width * 0.4)
                            )
                        # IMPORTANT: skip further checks for this same click
                        continue

                    # -- If we get here, the click was NOT inside the panel => check map
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.state = 'paused'

                    # If we are in placement mode
                    if self.placing_tower:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pos = pygame.mouse.get_pos()
                            if event.button == 1:  # Left-click => place
                                if self.can_place_tower(pos[0], pos[1]):
                                    # Check if we can afford it
                                    if self.gold_manager.get_points() >= self.tower_preview.price:
                                        self.gold_manager.deduct_points(self.tower_preview.price)
                                        # Actually place it
                                        new_tower = self.tower_type(
                                            pos[0] - self.tower_preview.width // 2,
                                            pos[1] - self.tower_preview.height // 2,
                                            self.tower_preview.width,
                                            self.tower_preview.height,
                                            attack_range=self.tower_preview.attack_range
                                        )
                                        self.towers.append(new_tower)
                                # Either way, stop placing
                                self.placing_tower = False
                                self.tower_preview = None
                                self.tower_type = None

                            elif event.button == 3:  # Right-click => cancel
                                self.placing_tower = False
                                self.tower_preview = None
                                self.tower_type = None

                current_time = pygame.time.get_ticks()
                if current_time - self.last_spawn_time >= self.spawn_interval:
                    self.spawn_enemy()
                    self.last_spawn_time = current_time

            elif self.state == 'paused':
                self.display_pause_menu()

            elif self.state == 'game over':
                self.display_game_over()
                return
 
    def update(self):
        current_time = pygame.time.get_ticks()

        if not self.last_check_new_path or current_time - self.last_check_new_path >= self.new_path_interval:
            for enemy in self.enemies[:]:
                nearest_tower, _ = self.find_nearest_tower(enemy)
                self.pathfinder.set_groups(enemy, nearest_tower)
                enemy.path = self.pathfinder.create_path()
                enemy.nearest_target = nearest_tower
            self.last_check_new_path = current_time

        for enemy in self.enemies[:]:
            enemy.move_towards()
        
        # Update towers
        for tower in self.towers[:]:
            if tower.life > 0:
                tower.attack(self.enemies, current_time)
                if hasattr(tower, "arrows"):
                    tower.arrows.update(self.enemies)
            else:
                if not isinstance(tower, MainTower):
                    self.towers.remove(tower)
                else:
                    print("Game Over! The Main Tower has been destroyed.")
                    self.towers.remove(tower)
                    self.state = 'game over'
                    return

    def draw(self):
        self.win.blit(self.bg, (0, 0))

        # Draw enemies
        for enemy in self.enemies[:]:
            if enemy.life > 0:
                enemy.draw(self.win)
            else:
                self.points_manager.add_points(enemy.points)
                self.gold_manager.add_points(enemy.points)
                self.enemies.remove(enemy)

        # Draw towers
        for tower in self.towers:
            if tower.life > 0:
                if isinstance(tower, ArcherTower):
                    tower.draw(self.win, pygame.time.get_ticks(), self.enemies)
                else:
                    tower.draw(self.win, pygame.time.get_ticks())

                # Check if the user clicked on this tower
                if tower.clicked_for_upgrade():
                    if self.gold_manager.get_points() >= tower.price:
                        tower.draw_upgrade_button(self.win)
                        if tower.clicked_plus_rect_upgrade_button():
                            tower.upgrade()
                            tower.hide_display_upgrade_button()
                            self.gold_manager.deduct_points(tower.price)
                
                if not tower.clicked_for_upgrade():
                    tower.hide_display_upgrade_button()

        # Draw tower preview if we are placing
        if self.placing_tower and self.tower_preview:
            mx, my = pygame.mouse.get_pos()
            self.tower_preview.x = mx - self.tower_preview.width // 2
            self.tower_preview.y = my - self.tower_preview.height // 2
            if isinstance(self.tower_preview, ArcherTower):
                self.tower_preview.draw(self.win, pygame.time.get_ticks(), self.enemies)
            else:
                self.tower_preview.draw(self.win, pygame.time.get_ticks())

        # Display resource points
        font = pygame.font.SysFont(None, int(self.width * 0.035))
        points_text = font.render(f"Score: {self.points_manager.get_points()}", True, (158, 201, 0))
        self.win.blit(points_text, (self.width * 0.01, self.height * 0.01))

        gold_text = font.render(f"  Gold: {self.gold_manager.get_points()}", True, (250, 250, 0))
        self.win.blit(gold_text, (self.width * 0.01, self.height * 0.06))

        # -------------------------------
        # NEW: Display wave counter
        # -------------------------------
        wave_text = font.render(f" Wave: {self.wave_count}", True, (255, 255, 255))
        self.win.blit(wave_text, (self.width * 0.01, self.height * 0.11))

        # Draw the selection panel
        self.tower_panel.draw(self.win)

        pygame.display.update()

    def find_nearest_tower(self, enemy):
        nearest_tower = None
        min_distance = float('inf')
        
        for tower in self.towers:
            distance = math.dist(enemy.pos, (tower.x, tower.y))
            if distance < min_distance:
                min_distance = distance
                nearest_tower = tower
        return nearest_tower, min_distance
    
    def display_game_over(self):
        font = pygame.font.SysFont(None, 128)
        game_over_text = font.render("Game Over", True, (0, 255, 0))
        game_over_outline = font.render("Game Over", True, (0, 0, 0))
        button_font = pygame.font.SysFont(None, 64)
        button_width, button_height = 200, 80
        button_y = self.height // 2 + game_over_text.get_height() // 2 + 20
        button_x = self.width // 2 - button_width - 10
        button2_x = self.width // 2 + 10
        retry_text = button_font.render("Retry", True, (255, 255, 255))
        quit_text = button_font.render("Quit", True, (255, 255, 255))
        in_game_over = True

        while in_game_over:
            self.win.blit(self.bg, (0, 0))
            text_x = self.width // 2 - game_over_text.get_width() // 2
            text_y = self.height // 2 - game_over_text.get_height()
            offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -2), (-2, 0), (2, 0), (0, 2)]
            for dx, dy in offsets:
                self.win.blit(game_over_outline, (text_x + dx, text_y + dy))
            self.win.blit(game_over_text, (text_x, text_y))

            pygame.draw.rect(self.win, (139, 69, 19), (button_x, button_y, button_width, button_height))
            pygame.draw.rect(self.win, (0, 0, 0), (button_x, button_y, button_width, button_height), 3)
            self.win.blit(retry_text, (
                button_x + button_width // 2 - retry_text.get_width() // 2,
                button_y + button_height // 2 - retry_text.get_height() // 2)
            )
            pygame.draw.rect(self.win, (139, 69, 19), (button2_x, button_y, button_width, button_height))
            pygame.draw.rect(self.win, (0, 0, 0), (button2_x, button_y, button_width, button_height), 3)
            self.win.blit(quit_text, (
                button2_x + button_width // 2 - quit_text.get_width() // 2,
                button_y + button_height // 2 - quit_text.get_height() // 2)
            )

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    # Retry
                    if button_x <= mx <= button_x + button_width and button_y <= my <= button_y + button_height:
                        print("Retry button clicked! Restarting the game...")
                        self.__init__()
                        self.run()
                        return
                    # Quit
                    elif button2_x <= mx <= button2_x + button_width and button_y <= my <= button_y + button_height:
                        print("Quit button clicked! Exiting the game...")
                        pygame.mixer.music.stop()
                        pygame.quit()
                        exit()

if __name__ == "__main__":
    g = Game()
    g.run()
