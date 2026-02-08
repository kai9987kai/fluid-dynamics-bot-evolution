
import config
from bot import Bot
import random
import math

class Simulation:
    def __init__(self):
        self.population = [Bot(pos_x=-300, pos_y=random.uniform(-100, 100)) for _ in range(config.POPULATION_SIZE)]
        self.generation = 0
        self.obstacles = self.generate_obstacles()
        self.foods = self.generate_food()
        self.target_pos = (350, 0)
        
    def generate_obstacles(self):
        obs = []
        for _ in range(5):
            angle = random.uniform(0, 2*math.pi)
            speed = config.OBSTACLE_SPEED
            obs.append({
                'pos': [random.uniform(-100, 200), random.uniform(-200, 200)],
                'radius': random.uniform(15, 30),
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed]
            })
        return obs

    def generate_food(self):
        foods = []
        for _ in range(config.FOOD_COUNT):
            foods.append(self.create_one_food())
        return foods

    def create_one_food(self):
        return {
            'pos': [random.uniform(-350, 350), random.uniform(-250, 250)],
            'energy': config.FOOD_ENERGY_VALUE
        }
        
    def get_flow_force(self, x, y):
        # Chaotic Flow Field: Sine/Cosine based on position
        # Flow(x,y) = (cos(y/scale), sin(x/scale)) * strength
        scale = config.FLUID_SCALE
        strength = config.FLUID_STRENGTH
        
        fx = math.cos(y / scale) * strength
        fy = math.sin(x / scale) * strength
        
        # Add a constant drift to the right so they don't just get stuck in loops forever
        fx += 0.2
        
        return (fx, fy)
        
    def update(self):
        self.update_obstacles()
        
        alive_count = 0
        for bot in self.population:
            if not bot.alive:
                continue
                
            # Calculate local fluid force
            fluid_force = self.get_flow_force(bot.pos[0], bot.pos[1])
            
            bot.update(fluid_force, self.obstacles, self.foods)
            
            # Check Food Collision (handled here to sync with shared list)
            # Iterate copy to modify original
            for i in range(len(self.foods) - 1, -1, -1):
                food = self.foods[i]
                dist = math.hypot(bot.pos[0] - food['pos'][0], bot.pos[1] - food['pos'][1])
                if dist < 15: # Bot radius ~5 + Food radius ~10
                    bot.energy += food['energy']
                    bot.food_eaten += 1
                    # Respawn food immediately elsewhere
                    self.foods[i] = self.create_one_food()

            if bot.alive:
                alive_count += 1
                
        return alive_count

    def update_obstacles(self):
        w, h = config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT/2
        for obs in self.obstacles:
            obs['pos'][0] += obs['vel'][0]
            obs['pos'][1] += obs['vel'][1]
            if obs['pos'][0] < -w + obs['radius'] or obs['pos'][0] > w - obs['radius']: obs['vel'][0] *= -1
            if obs['pos'][1] < -h + obs['radius'] or obs['pos'][1] > h - obs['radius']: obs['vel'][1] *= -1

    def calculate_fitness(self):
        for bot in self.population:
            bot.calculate_fitness(self.target_pos)

    def evolve(self):
        self.calculate_fitness()
        self.population.sort(key=lambda b: b.fitness, reverse=True)
        
        print(f"Gen {self.generation}: Best Fitness={self.population[0].fitness:.1f}, Food Eaten={self.population[0].food_eaten}")
        
        new_pop = []
        for i in range(config.ELITISM_COUNT):
            child = Bot(pos_x=-300, pos_y=random.uniform(-100, 100), genome=self.population[i].genome)
            new_pop.append(child)
            
        while len(new_pop) < config.POPULATION_SIZE:
            p1 = self.select_parent()
            p2 = self.select_parent()
            child_genome = p1.genome.crossover(p2.genome)
            child_genome.mutate()
            new_pop.append(Bot(pos_x=-300, pos_y=random.uniform(-100, 100), genome=child_genome))
            
        self.population = new_pop
        self.generation += 1
        # self.obstacles = self.generate_obstacles() # Keep dynamic or reset?
        self.foods = self.generate_food() # Reset food distribution

    def select_parent(self):
        tournament = random.sample(self.population, 3)
        tournament.sort(key=lambda b: b.fitness, reverse=True)
        return tournament[0]
