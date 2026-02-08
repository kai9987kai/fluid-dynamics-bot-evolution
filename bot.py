
import math
import config
from genome import Genome

class Bot:
    def __init__(self, pos_x=0, pos_y=0, genome=None):
        self.pos = [pos_x, pos_y]
        self.vel = [0.0, 0.0]
        self.acc = [0.0, 0.0]
        self.angle = 0.0  # Radians
        self.fitness = 0.0
        self.crashed = False
        self.energy = config.STARTING_ENERGY
        self.alive = True
        self.food_eaten = 0
        
        # Genome (Brain)
        self.genome = genome if genome else Genome()
        
        # Sensors
        # 3 rays: -45 deg, 0 deg, +45 deg
        self.ray_angles = [-math.pi/4, 0, math.pi/4]
        self.sensor_readings = [0.0] * len(self.ray_angles)

    def update(self, fluid_force, obstacles, foods):
        if not self.alive:
            return

        # 0. Check Energy
        self.energy -= config.ENERGY_CONSUMPTION_RATE
        if self.energy <= 0:
            self.alive = False
            return

        # 1. Physics: Add Fluid Force
        self.apply_force(fluid_force)
        
        # 2. Physics: Drag
        speed = math.hypot(self.vel[0], self.vel[1])
        if speed > 0:
            drag_mag = config.DRAG_COEFFICIENT * speed * speed
            drag_x = -self.vel[0] / speed * drag_mag
            drag_y = -self.vel[1] / speed * drag_mag
            self.apply_force((drag_x, drag_y))

        # 3. Sense Environment (Raycasting + Food sensing)
        self.sense(obstacles, foods)

        # 4. Think (Neural Network)
        # Inputs: 
        # - Sensors (3)
        # - Velocity (2)
        # - Local Fluid Force (2)
        # - Vector to Nearest Food (2)
        # - Energy Level (1)
        
        norm_vel_x = math.tanh(self.vel[0] * 0.1)
        norm_vel_y = math.tanh(self.vel[1] * 0.1)
        norm_ff_x = math.tanh(fluid_force[0] * 0.1)
        norm_ff_y = math.tanh(fluid_force[1] * 0.1)
        
        # Find nearest food vector
        shortest_dist = float('inf')
        nearest_food_vec = [0, 0]
        
        for food in foods:
             dx = food['pos'][0] - self.pos[0]
             dy = food['pos'][1] - self.pos[1]
             d = math.hypot(dx, dy)
             if d < shortest_dist:
                 shortest_dist = d
                 # Normalize vector
                 if d > 0:
                     nearest_food_vec = [dx/d, dy/d]
        
        norm_energy = self.energy / config.STARTING_ENERGY
        
        inputs = self.sensor_readings + \
                 [norm_vel_x, norm_vel_y] + \
                 [norm_ff_x, norm_ff_y] + \
                 nearest_food_vec + \
                 [norm_energy]
                 
        outputs = self.genome.feed_forward(inputs)
        
        # 5. Act (Thrust)
        steering = outputs[0] * 0.2  # Max turn rate
        thrust = max(0, outputs[1]) * config.THRUST_POWER
        
        # Energy Cost for Thrust
        self.energy -= thrust * config.THRUST_ENERGY_COST
        
        self.angle += steering
        
        thrust_x = math.cos(self.angle) * thrust
        thrust_y = math.sin(self.angle) * thrust
        self.apply_force((thrust_x, thrust_y))

        # 6. Integrate Physics
        self.vel[0] += self.acc[0]
        self.vel[1] += self.acc[1]
        
        # Limit speed
        speed = math.hypot(self.vel[0], self.vel[1])
        if speed > config.MAX_SPEED:
            scale = config.MAX_SPEED / speed
            self.vel[0] *= scale
            self.vel[1] *= scale
            
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        # Reset acceleration
        self.acc = [0.0, 0.0]

        # 7. Check Collisions & Food
        self.check_collisions(obstacles)
        self.check_food(foods)

    def apply_force(self, force):
        self.acc[0] += force[0]
        self.acc[1] += force[1]

    def sense(self, obstacles, foods):
        # Raycasting logic
        for i, ray_angle in enumerate(self.ray_angles):
            global_angle = self.angle + ray_angle
            rx = math.cos(global_angle)
            ry = math.sin(global_angle)
            
            closest_dist = 200.0  # Max sight range
            
            # Check against obstacles
            for obs in obstacles:
                ox = obs['pos'][0] - self.pos[0]
                oy = obs['pos'][1] - self.pos[1]
                
                projection = ox * rx + oy * ry
                if projection > 0:
                    closest_x = self.pos[0] + rx * projection
                    closest_y = self.pos[1] + ry * projection
                    
                    dist_to_ray = math.hypot(closest_x - obs['pos'][0], closest_y - obs['pos'][1])
                    if dist_to_ray < obs['radius']:
                        dist = projection - math.sqrt(obs['radius']**2 - dist_to_ray**2)
                        if dist < closest_dist:
                            closest_dist = dist
                            
            self.sensor_readings[i] = 1.0 - (max(0, closest_dist) / 200.0)

    def check_collisions(self, obstacles):
        if not self.alive: return
        
        w, h = config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT/2
        if self.pos[0] < -w or self.pos[0] > w or self.pos[1] < -h or self.pos[1] > h:
            self.crashed = True
            self.alive = False
            
        for obs in obstacles:
            dist = math.hypot(self.pos[0] - obs['pos'][0], self.pos[1] - obs['pos'][1])
            if dist < obs['radius'] + 5: 
                self.crashed = True
                self.alive = False

    def check_food(self, foods):
        if not self.alive: return
        
        # Iterate backwards to remove eaten food safely using manual index if needed
        # Or let simulation handle removal? 
        # Better: return list of eaten indices?
        # Actually, self.pos is float.
        pass # Handled in simulation to modify the shared food list

    def calculate_fitness(self, target_pos):
        if self.crashed:
            self.fitness = 1.0 # Minimal fitness
            return
            
        dist = math.hypot(self.pos[0] - target_pos[0], self.pos[1] - target_pos[1])
        
        # Fitness: Survival Time (implicit via energy management?) + Food + Distance
        # We don't track time alive explicitly yet, let's assume if alive at end = good.
        
        survival_bonus = 100.0 if self.alive else 0.0
        food_score = self.food_eaten * 50.0
        dist_score = 1000.0 / (dist + 1.0)
        
        self.fitness = survival_bonus + food_score + dist_score
