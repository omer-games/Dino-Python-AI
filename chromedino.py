import datetime
import os
import random
import pygame
import neat
import pickle

pygame.init()

# Global Constants

use_pickle = True
checkpoint_name = "" # if you dont want to use a checkpoint leave this empty!

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Chrome Dino Runner")

Ico = pygame.image.load("assets/DinoWallpaper.png")
pygame.display.set_icon(Ico)

RUNNING = [
    pygame.image.load(os.path.join("assets/Dino", "DinoRun1.png")),
    pygame.image.load(os.path.join("assets/Dino", "DinoRun2.png")),
]
JUMPING = pygame.image.load(os.path.join("assets/Dino", "DinoJump.png"))
DUCKING = [
    pygame.image.load(os.path.join("assets/Dino", "DinoDuck1.png")),
    pygame.image.load(os.path.join("assets/Dino", "DinoDuck2.png")),
]

SMALL_CACTUS = [
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus1.png")),
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus2.png")),
    pygame.image.load(os.path.join("assets/Cactus", "SmallCactus3.png")),
]
LARGE_CACTUS = [
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus1.png")),
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus2.png")),
    pygame.image.load(os.path.join("assets/Cactus", "LargeCactus3.png")),
]

BIRD = [
    pygame.image.load(os.path.join("assets/Bird", "Bird1.png")),
    pygame.image.load(os.path.join("assets/Bird", "Bird2.png")),
]

CLOUD = pygame.image.load(os.path.join("assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("assets/Other", "Track.png"))

FONT_COLOR=(150,150,150)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt") 
    
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    max_fitness = config.fitness_threshold
    if use_pickle:
        population_size = 1
    else:
        population_size = config.pop_size
    
class Dinosaur:

    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        
        self.is_alive = True

    def update(self, userInput, neatAction):
        if self.dino_duck and self.dino_rect.y:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump and self.dino_rect.y:
            self.jump()
        if self.step_index >= 10:
            self.step_index = 0

        if (userInput[pygame.K_UP] or userInput[pygame.K_SPACE] or neatAction == "jump") and not self.dino_jump and self.dino_rect.y > 300:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif (userInput[pygame.K_DOWN] or neatAction == "duck") and not self.dino_jump and self.dino_rect.y < 320:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or (userInput[pygame.K_DOWN]  or neatAction == "duck")):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        try:
            self.image = self.run_img[self.step_index // 5]
        except:
            pass
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.x *=1.5

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    BIRD_HEIGHTS = [250, 290, 320]

    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = random.choice(self.BIRD_HEIGHTS)
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1


def main(config, genomes):
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, max_fitness
    run = True
    clock = pygame.time.Clock()
    dinos = []
    for _ in range(population_size):
        dinos.append(Dinosaur())
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font("freesansbold.ttf", 20)
    obstacles = []
    death_count = 0
    pause = False

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        text = font.render("  Points: " + str(points), True, FONT_COLOR)
        SCREEN.blit(text, (900, 40))

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed
        
    nets = []
    if use_pickle:
        for genome in genomes:
            nets.append(neat.nn.FeedForwardNetwork.create(genome, config))
    else:
        for (genomeid, genome) in genomes:
            nets.append(neat.nn.FeedForwardNetwork.create(genome, config))
        
    while run:
        if use_pickle and any(genome for genome in genomes if genome.fitness > max_fitness):
            run = False
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                pygame.quit()
                run = False

        if not use_pickle:
            for i, (genomeid, genome) in enumerate(genomes):
                if dinos[i].is_alive:
                    genome.fitness += 0.1
    
        userInput = pygame.key.get_pressed()   
        for i, net in enumerate(nets):      
            output = net.activate(input_info(dinos[i]))
            decisiton = output.index(max(output))
            if decisiton == 1 and dinos[i].is_alive:
                dinos[i].update(userInput, "jump")
            elif decisiton == 2 and dinos[i].is_alive:
                dinos[i].update(userInput, "duck")
            else:
                dinos[i].update(userInput, "thing")
            
            
        current_time = datetime.datetime.now().hour
        if 7 < current_time < 19:
            SCREEN.fill((255, 255, 255))
        else:
            SCREEN.fill((0, 0, 0))
        userInput = pygame.key.get_pressed()
        for player in dinos:
            if player.is_alive:
                player.draw(SCREEN)

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            for player in dinos:
                if player.dino_rect.colliderect(obstacle.rect): 
                    player.is_alive = False
                    
                    
        if not any(x.is_alive for x in dinos):
            break

        background()

        cloud.draw(SCREEN)
        cloud.update()

        score()

        clock.tick(30)
        pygame.display.update()


def eval_genomes(genomes, config):
    for (genomeid, genome) in genomes:
        genome.fitness = 0
    main(config, genomes)
    pass

def run_neat(config, checkpoint):
    if checkpoint != "":
        p = neat.Checkpointer.restore_checkpoint(checkpoint)
    else:
        p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))
    
    best = p.run(eval_genomes, 10)
    with open("best.pickle", "wb") as f:
        pickle.dump(best, f)
        
def input_info(dino):
    global obstacles
    closest_x = 10000
    closest_y = 10000
    try:
        if len(obstacles) > 0:
            closest_obstacle = sorted((obs for obs in obstacles if obs.rect.x > dino.dino_rect.x - 100), key=lambda x: x.rect.x)[0]
            closest_x = closest_obstacle.rect.x
            closest_y = closest_obstacle.rect.y
    except:
        pass
    
    return [dino.dino_rect.y, dino.dino_rect.y-closest_y, dino.dino_rect.x-closest_x, game_speed]
    
def use_ai(config):
    with open("best.pickle", "rb") as f:
        best = [pickle.load(f)]
    main(config, best)

if __name__ == "__main__":
    if use_pickle:
        use_ai(config)
    else:
        run_neat(config, checkpoint_name)