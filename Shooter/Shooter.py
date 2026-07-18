import arcade
import math
import random

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Space Shooter"

PLAYER_SCALE = 0.3
PLAYER_SPEED = 5
PLAYER_TURN_SPEED = 5
PLAYER_SHOOT_COOLDOWN = 0.2 

BULLET_SPEED =  5
BULLET_SCALE = 1

ENEMY_SPAWN_RATE = 1.5
ENEMY_SPEED_MIN = 1
ENEMY_SPEED_MAX = 3
ENEMY_SCALE = 0.3

class Enemy:
    def __init__(self):
        side = random.choice(["top","right","bottom","left"])
        if side == "top":
            self.x = random.uniform(0, SCREEN_WIDTH)
            self.y = SCREEN_HEIGHT + 20
        elif side == "right":
            self.x = SCREEN_WIDTH + 20
            self.y = random.uniform(0, SCREEN_HEIGHT)
        elif side == "bottom":
            self.x = random.uniform(0, SCREEN_WIDTH)
            self.y = -20 
        else:
            self.x = -20  
            self.y =random.uniform(0, SCREEN_HEIGHT)

        self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
        self.angle = 0
        self.radius = 50 * ENEMY_SCALE
        self.health = 2
        self.max_health = 2
        self.shoot_cooldown = 0
        self.is_shooter = random.random() < 0.35

    def update(self, player_x, player_y, enemy_bullets_list):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            self.angle = math.degrees(math.atan2(dy, dx))
            self.x +=math.cos(math.radians(self.angle)) * self.speed
            self.y +=math.sin(math.radians(self.angle)) * self.speed

        #shooting logic
        if self.is_shooter:
            self.shoot_cooldown -=1
            if self.shoot_cooldown<=0 and dist< 400:
                self.shoot(player_x, player_y, enemy_bullets_list)

    def shoot(self, player_x, player_y, enemy_bullets_list):
        angle = math.degrees(math.atan2(player_y - self.y, player_x - self.x))
        
        bullet_x = self.x + math.cos(math.radians(angle)) * self.radius
        bullet_y = self.y + math.sin(math.radians(angle)) * self.radius
        
        enemy_bullets_list.append(EnemyBullet(bullet_x, bullet_y, angle))
        self.shoot_cooldown = 60   # \~1 second cooldown at 60 FPS

    def draw(self):
        #choose color based on its a shooter or not
        if self.is_shooter:
            enemy_color = arcade.color.RED
            draw_radius = self.radius * 1.1

        else:
            enemy_color = arcade.color.YELLOW
            draw_radius = self.radius

        arcade.draw_triangle_filled(
            self.x + math.cos(math.radians(self.angle)) * self.radius * 2,
            self.y + math.sin(math.radians(self.angle)) * self.radius * 2,
            self.x + math.cos(math.radians(self.angle + 140)) * self.radius,
            self.y + math.sin(math.radians(self.angle + 140)) * self.radius,
            self.x + math.cos(math.radians(self.angle - 140)) * self.radius,
            self.y + math.sin(math.radians(self.angle - 140)) * self.radius,
            enemy_color
        )

        self.draw_health_bar()

    def is_off_screen(self):
        return(self.x < -50 or self.x > SCREEN_WIDTH or
               self.y < -50 or self.y > SCREEN_HEIGHT)
    
    def draw_health_bar(self):
        if self.health >= self.max_health or self.health <= 0:
            return
            
        bar_width = self.radius * 2.8
        bar_height = 7
        health_ratio = max(0, self.health / self.max_health)  # prevent negative
        
        center_x = self.x
        center_y = self.y + self.radius + 15
        
        # Background (red)
        arcade.draw_lrbt_rectangle_filled(
            center_x - bar_width/2,          # left
            center_x + bar_width/2,          # right
            center_y - bar_height/2,         # bottom
            center_y + bar_height/2,         # top
            arcade.color.DARK_RED
        )
        
        # Current health (green)
        current_width = bar_width * health_ratio
        arcade.draw_lrbt_rectangle_filled(
            center_x - bar_width/2,                    # left
            center_x - bar_width/2 + current_width,    # right
            center_y - bar_height/2,                   # bottom
            center_y + bar_height/2,                   # top
            arcade.color.LIME_GREEN
        )
        
        # Optional border
        arcade.draw_lrbt_rectangle_outline(
            center_x - bar_width/2,
            center_x + bar_width/2,
            center_y - bar_height/2,
            center_y + bar_height/2,
            arcade.color.WHITE, 1
        )
 

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.radius = 4 * BULLET_SCALE

    def update(self):
        #bullet move based on angle
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed

    def draw(self):
        arcade.draw_circle_filled(
            self.x, self.y, self.radius, arcade.color.YELLOW)
        
    def is_off_screen(self):
        return(self.x < 0 or self.x > SCREEN_WIDTH or
               self.y < 0 or self.y > SCREEN_HEIGHT)
    
class EnemyBullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 4          # Slightly slower than player bullets
        self.radius = 5

    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.radius, arcade.color.RED)

    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)

class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 45
        self.health = 2000
        self.max_health = 2000
        self.speed = 2.0
        self.angle = 0
        self.shoot_cooldown = 0
        self.phase = 1  # Can be used for different attack patterns later

    def update(self, player_x, player_y, enemy_bullets_list):
        # Move towards player slowly
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)
        

        if dist > 0:
            self.angle = math.degrees(math.atan2(dy, dx))
            self.x += math.cos(math.radians(self.angle)) * self.speed
            self.y += math.sin(math.radians(self.angle)) * self.speed

        # Boss shooting (faster and more bullets)
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0 and dist < 500:
            self.shoot(player_x, player_y, enemy_bullets_list)
            self.shoot_cooldown = 35   # shoots quite frequently

    def shoot(self, player_x, player_y, enemy_bullets_list):
        # Shoot 3 bullets in a spread
        base_angle = math.degrees(math.atan2(player_y - self.y, player_x - self.x))
        
        for offset in [-25, 0, 25]:
            angle = base_angle + offset
            bx = self.x + math.cos(math.radians(angle)) * self.radius
            by = self.y + math.sin(math.radians(angle)) * self.radius
            enemy_bullets_list.append(EnemyBullet(bx, by, angle))
    
    def draw(self):
        # Big red boss
        arcade.draw_triangle_filled(
            self.x + math.cos(math.radians(self.angle)) * self.radius * 2.2,
            self.y + math.sin(math.radians(self.angle)) * self.radius * 2.2,
            self.x + math.cos(math.radians(self.angle + 140)) * self.radius * 1.3,
            self.y + math.sin(math.radians(self.angle + 140)) * self.radius * 1.3,
            self.x + math.cos(math.radians(self.angle - 140)) * self.radius * 1.3,
            self.y + math.sin(math.radians(self.angle - 140)) * self.radius * 1.3,
            arcade.color.DARK_RED
        )
        
        # Extra detail (inner triangle)
        arcade.draw_triangle_filled(
            self.x, self.y,
            self.x + math.cos(math.radians(self.angle + 120)) * self.radius * 0.8,
            self.y + math.sin(math.radians(self.angle + 120)) * self.radius * 0.8,
            self.x + math.cos(math.radians(self.angle - 120)) * self.radius * 0.8,
            self.y + math.sin(math.radians(self.angle - 120)) * self.radius * 0.8,
            arcade.color.RED
        )
        
        self.draw_health_bar()

    def draw_health_bar(self):
        if self.health <= 0:
            return
        bar_width = self.radius * 3
        bar_height = 12
        ratio = self.health / self.max_health
        center_y = self.y + self.radius + 25
        
        arcade.draw_lrbt_rectangle_filled(
            self.x - bar_width/2, self.x + bar_width/2,
            center_y - bar_height/2, center_y + bar_height/2,
            arcade.color.DARK_RED
        )
        arcade.draw_lrbt_rectangle_filled(
            self.x - bar_width/2, self.x - bar_width/2 + bar_width * ratio,
            center_y - bar_height/2, center_y + bar_height/2,
            arcade.color.LIME_GREEN
        )

class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_angle = 0
        self.player_radius = 100 * PLAYER_SCALE

        self.player_sprite = arcade.Sprite(
            "Assets/Spc1.png",
            scale=0.04
            )
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.bullets = []
        self.enemy_bullets =[]
        self.shoot_cooldown = 0
        self.enemies = []
        self.enemy_spawn_time = 0
        self.key_pressed = set()

        self.player_health = 100
        self.max_player_health = 100
        self.game_over = False
        self.score = 0

        self.boss = None
        self.boss_spawned = False

    
    def on_draw(self):
        self.clear()

        if self.game_over:
            self.draw_game_over()
            return

       # arcade.draw_triangle_filled(
        #    self.player_x + math.cos(math.radians(self.player_angle)) * self.player_radius * 1.5,
         #   self.player_y + math.sin(math.radians(self.player_angle)) * self.player_radius * 1.5,
          #  self.player_x + math.cos(math.radians(self.player_angle + 150)) * self.player_radius,
           # self.player_y + math.sin(math.radians(self.player_angle + 150)) * self.player_radius,
           # self.player_x + math.cos(math.radians(self.player_angle - 150)) * self.player_radius,
           # self.player_y + math.sin(math.radians(self.player_angle - 150)) * self.player_radius,
           # arcade.color.WHITE
        #)

        self.player_list.draw()

        for bullet in self.bullets:
            bullet.draw()

        for enemy in self.enemies:
            enemy.draw()

        for bullet in self.enemy_bullets:
            bullet.draw()

        if self.boss:
            self.boss.draw()

        #live score
        arcade.draw_text(
            f"Score: {self.score}",
            20,
            SCREEN_HEIGHT - 80,
            arcade.color.WHITE,
            28,
            bold = True
        )

        self.draw_health_bar()

    def on_update(self, delta_time):
        self.shoot_cooldown -= delta_time

        self.player_sprite.center_x = self.player_x
        self.player_sprite.center_y = self.player_y
        self.player_sprite.angle = self.player_angle + 90

        if self.game_over:
            return #stops all gamelogic when game_over

        if arcade.key.SPACE in self.key_pressed:
            self.shoot()

        if self.enemy_spawn_time <=0:
            self.enemies.append(Enemy())
            self.enemy_spawn_time = ENEMY_SPAWN_RATE

        if arcade.key.W in self.key_pressed:
            self.player_y += PLAYER_SPEED 
        if arcade.key.S in self.key_pressed:
            self.player_y -= PLAYER_SPEED
        if arcade.key.A in self.key_pressed:
            self.player_x -= PLAYER_SPEED
        if arcade.key.D in self.key_pressed:
            self.player_x += PLAYER_SPEED

        # Spawn normal enemies (only if no boss is active)
        if self.boss is None:
            self.enemy_spawn_time -= delta_time
            
            if self.enemy_spawn_time <= 0:
                self.enemies.append(Enemy())
                self.enemy_spawn_time = ENEMY_SPAWN_RATE

        # Boss Spawning
        if not self.boss_spawned and self.score >= 500:   # Change 300 to whatever you like
            self.boss = Boss(SCREEN_WIDTH/2, -100)
            self.boss_spawned = True
            self.enemies.clear()          # ← Clear normal enemies when boss appears
            self.enemy_spawn_time = 4.0
            print("BOSS FIGHT STARTED!")
        
        # Boss Update & Death Check
        if self.boss:
            self.boss.update(self.player_x, self.player_y, self.enemy_bullets)
            
            # Player collision with boss
            if math.hypot(self.boss.x - self.player_x, self.boss.y - self.player_y) < self.boss.radius + self.player_radius:
                self.take_damage(40)
            
            # Boss defeated
            if self.boss.health <= 0:
                self.score += 200
                self.boss = None
                print("Boss Defeated! Normal enemies resume.")
                # Optional: Give player a small reward
                self.player_health = min(self.max_player_health, self.player_health + 30)
        
        self.player_x = max(self.player_radius, min(
            SCREEN_WIDTH - self.player_radius, self.player_x))
        self.player_y = max(self.player_radius, min(
            SCREEN_HEIGHT - self.player_radius, self.player_y))
        
        for bullet in self.bullets[:]:
            bullet.update()
            hit = False
            # Check collision with every enemy
            for enemy in self.enemies[:]:
                distance = math.hypot(bullet.x - enemy.x, bullet.y - enemy.y)
                
                if distance < bullet.radius + enemy.radius:
                    # Bullet hit enemy!
                    enemy.health -= 1
                    hit = True
                    # Remove bullet
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    
                    # Remove enemy if dead
                    if enemy.health <= 0:
                        self.score +=5
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                    
                    break  # exit inner loop after hit
              # === COLLISION WITH BOSS ===
            if self.boss and not hit:
                distance = math.hypot(bullet.x - self.boss.x, bullet.y - self.boss.y)
                if distance < bullet.radius + self.boss.radius:
                    self.boss.health -= 1          # ← Boss takes damage
                    hit = True
                    self.score += 1                # Small points for hitting boss

                    if bullet in self.bullets:
                        self.bullets.remove(bullet)

                    if self.boss.health <= 0:
                        self.score += 100
                        self.boss = None


        for enemy in self.enemies[:]:
            enemy.update(self.player_x, self.player_y, self.enemy_bullets)
               # Check if enemy touches player
            distance = math.hypot(enemy.x - self.player_x, enemy.y - self.player_y)
            
            if distance < self.player_radius + enemy.radius:
                self.take_damage(25)           # Reduce health
                self.enemies.remove(enemy)     # Remove enemy after hit
                
            elif enemy.is_off_screen():
                self.enemies.remove(enemy)

        # Update enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.enemy_bullets.remove(bullet)
            # Check collision with player
            elif math.hypot(bullet.x - self.player_x, bullet.y - self.player_y) < bullet.radius + self.player_radius:
                self.take_damage(15)
                self.enemy_bullets.remove(bullet)

    def shoot(self):
        if self.shoot_cooldown > 0:
            return
        bullet_x = self.player_x + math.cos(math.radians(self.player_angle)) * self.player_radius
        bullet_y = self.player_y + math.sin(math.radians(self.player_angle)) * self.player_radius
        self.bullets.append(Bullet(bullet_x, bullet_y, self.player_angle))
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
        
    def on_key_press(self, key, modifiers):
        self.key_pressed.add(key)
        if self.game_over:
            if self.game_over and key == arcade.key.R:
                self.restart_game()
            return
        
    def on_key_release(self, key, modifiers):
        if key in self.key_pressed:
            self.key_pressed.remove(key)

    def on_mouse_motion(self, x, y, dx, dy):
        dx = x - self.player_x
        dy = y - self.player_y
        self.player_angle = math.degrees(math.atan2(dy, dx))

    def draw_health_bar(self):
        bar_width = 300
        bar_height = 25
        x = 20
        y = SCREEN_HEIGHT - 40

        #background
        arcade.draw_lbwh_rectangle_filled(
            x + bar_width/2, y,
            bar_width, bar_height,
            arcade.color.DARK_RED
        )
        #current health green
        health_ratio = self.player_health / self.max_player_health
        current_width = bar_width * health_ratio

        arcade.draw_lbwh_rectangle_filled(
            x + current_width/2, y,
            current_width, bar_height,
            arcade.color.LIME_GREEN
        )
        #border
        arcade.draw_lbwh_rectangle_outline(
            x + bar_width/2, y,
            bar_width, bar_height,
            arcade.color.WHITE, 3
        )
        #health text
        arcade.draw_text(
            f"HP:{int(self.player_health)}/{self.max_player_health}",
            x + 10, y - 8,
            arcade.color.WHITE,
            14,
            bold=True
        )

    def take_damage(self, amount=20):
        self.player_health -= amount
        if self.player_health <= 0:
            self.player_health = 0
            self.game_over = True
            print("===GAME OVER TRIGGRED===")
            
    def draw_game_over(self):
        # Dark semi-transparent background
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH,           # left, right
            0, SCREEN_HEIGHT,          # bottom, top
            (0, 0, 0, 180)
        )
        
        # GAME OVER Text
        arcade.draw_text(
            "GAME OVER",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 80,
            arcade.color.RED,
            font_size=80,
            bold=True,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Score
        arcade.draw_text(
            f"Final Score: {self.score}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 10,
            arcade.color.WHITE,
            font_size=40,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Restart instruction
        arcade.draw_text(
            "Press R to Restart",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 60,
            arcade.color.YELLOW,
            font_size=30,
            anchor_x="center",
            anchor_y="center"
        )

    def restart_game(self):
        self.player_health = 100
        self.game_over = False
        self.score = 0
        self.bullets.clear()
        self.enemies.clear()
        self.enemy_bullets.clear()

        self.shoot_cooldown = 0
        self.enemy_spawn_time = 0

        self.boss = None
        self.boss_spawned = False


        # Reset player position if needed
        self.player_x = SCREEN_WIDTH / 2
        self.player_y = SCREEN_HEIGHT / 2
        print("Game Restarted")

def main():
    window = GameWindow()
    arcade.run()

if __name__ == "__main__":
    main()