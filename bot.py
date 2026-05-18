import math

import config
from genome import Genome


class Bot:
    def __init__(self, pos_x=0, pos_y=0, genome=None):
        self.pos = [pos_x, pos_y]
        self.start_pos = [pos_x, pos_y]
        self.vel = [0.0, 0.0]
        self.acc = [0.0, 0.0]
        self.angle = 0.0
        self.fitness = 0.0
        self.behavior_score = 0.0
        self.novelty = 0.0
        self.crashed = False
        self.reached_target = False
        self.energy = config.STARTING_ENERGY
        self.alive = True
        self.food_eaten = 0
        self.nutrient_absorbed = 0.0
        self.age = 0
        self.closest_target_dist = float("inf")
        self.flow_alignment_sum = 0.0
        self.flow_alignment_samples = 0
        self.memory = [0.0] * config.MEMORY_SIZE

        self.genome = genome if genome else Genome()
        self.traits = self.genome.traits

        spread = self.traits["sensor_spread"]
        if config.SENSOR_RAY_COUNT == 1:
            self.ray_angles = [0.0]
        else:
            step = (spread * 2.0) / (config.SENSOR_RAY_COUNT - 1)
            self.ray_angles = [-spread + i * step for i in range(config.SENSOR_RAY_COUNT)]
        self.sensor_readings = [0.0] * len(self.ray_angles)

    @property
    def radius(self):
        return max(config.BOT_COLLISION_RADIUS, self.traits["body_width"] * 0.5)

    def update(self, fluid_force, obstacles, foods, nutrient_zones, target_pos):
        if not self.alive:
            return

        self.age += 1
        self.energy -= config.ENERGY_CONSUMPTION_RATE / self.traits["energy_efficiency"]
        if self.energy <= 0:
            self.alive = False
            return

        self.apply_force(fluid_force)

        speed = math.hypot(self.vel[0], self.vel[1])
        if speed > 0:
            drag_mag = (
                config.DRAG_COEFFICIENT
                * self.traits["drag_scale"]
                * speed
                * speed
            )
            drag_x = -self.vel[0] / speed * drag_mag
            drag_y = -self.vel[1] / speed * drag_mag
            self.apply_force((drag_x, drag_y))
            self.record_flow_alignment(fluid_force, speed)

        nearest_food_vec, nearest_food_dist = self.nearest_food_vector(foods)
        nutrient_vec, nutrient_dist = self.nearest_nutrient_vector(nutrient_zones)
        target_vec, target_dist = self.target_vector(target_pos)
        self.closest_target_dist = min(self.closest_target_dist, target_dist)
        boundary_warning = self.boundary_warning()
        self.sense(obstacles)

        norm_vel_x = math.tanh(self.vel[0] * 0.1)
        norm_vel_y = math.tanh(self.vel[1] * 0.1)
        norm_ff_x = math.tanh(fluid_force[0] * 0.1)
        norm_ff_y = math.tanh(fluid_force[1] * 0.1)
        norm_food_dist = self.normalize_distance(nearest_food_dist, config.SCREEN_WIDTH)
        norm_nutrient_dist = self.normalize_distance(nutrient_dist, config.SCREEN_WIDTH)
        norm_target_dist = self.normalize_distance(target_dist, config.SCREEN_WIDTH)
        norm_energy = max(0.0, min(1.5, self.energy / config.STARTING_ENERGY))
        flow_alignment = self.current_flow_alignment(fluid_force)

        inputs = (
            self.sensor_readings
            + [norm_vel_x, norm_vel_y]
            + [norm_ff_x, norm_ff_y]
            + nearest_food_vec
            + [norm_food_dist]
            + target_vec
            + [norm_target_dist, norm_energy, flow_alignment, boundary_warning]
            + nutrient_vec
            + [norm_nutrient_dist]
            + self.memory
        )

        outputs = self.genome.feed_forward(inputs)

        steering = outputs[0] * self.traits["turn_rate"]
        thrust = max(0.0, outputs[1]) * config.THRUST_POWER * self.traits["thrust_scale"]

        self.energy -= (
            thrust * config.THRUST_ENERGY_COST / self.traits["energy_efficiency"]
        )
        if self.energy <= 0:
            self.alive = False
            return

        self.angle += steering
        self.update_memory(outputs[2:])

        thrust_x = math.cos(self.angle) * thrust
        thrust_y = math.sin(self.angle) * thrust
        self.apply_force((thrust_x, thrust_y))

        self.vel[0] += self.acc[0]
        self.vel[1] += self.acc[1]

        speed = math.hypot(self.vel[0], self.vel[1])
        if speed > config.MAX_SPEED:
            scale = config.MAX_SPEED / speed
            self.vel[0] *= scale
            self.vel[1] *= scale

        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.acc = [0.0, 0.0]

        self.check_collisions(obstacles, target_pos)

    def apply_force(self, force):
        self.acc[0] += force[0]
        self.acc[1] += force[1]

    def sense(self, obstacles):
        sensor_range = self.traits["sensor_range"]
        for i, ray_angle in enumerate(self.ray_angles):
            global_angle = self.angle + ray_angle
            rx = math.cos(global_angle)
            ry = math.sin(global_angle)
            closest_dist = sensor_range

            for obs in obstacles:
                ox = obs["pos"][0] - self.pos[0]
                oy = obs["pos"][1] - self.pos[1]

                projection = ox * rx + oy * ry
                if projection <= 0:
                    continue

                closest_x = self.pos[0] + rx * projection
                closest_y = self.pos[1] + ry * projection

                dist_to_ray = math.hypot(closest_x - obs["pos"][0], closest_y - obs["pos"][1])
                hit_radius = obs["radius"] + self.radius
                if dist_to_ray < hit_radius:
                    dist = projection - math.sqrt(hit_radius**2 - dist_to_ray**2)
                    if dist < closest_dist:
                        closest_dist = dist

            self.sensor_readings[i] = 1.0 - (max(0.0, closest_dist) / sensor_range)

    def nearest_food_vector(self, foods):
        shortest_dist = float("inf")
        nearest_food_vec = [0.0, 0.0]

        for food in foods:
            dx = food["pos"][0] - self.pos[0]
            dy = food["pos"][1] - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist < shortest_dist:
                shortest_dist = dist
                if dist > 0:
                    nearest_food_vec = [dx / dist, dy / dist]

        return nearest_food_vec, shortest_dist

    def nearest_nutrient_vector(self, nutrient_zones):
        shortest_dist = float("inf")
        nearest_vec = [0.0, 0.0]

        for zone in nutrient_zones:
            dx = zone["pos"][0] - self.pos[0]
            dy = zone["pos"][1] - self.pos[1]
            dist = math.hypot(dx, dy)
            edge_dist = max(0.0, dist - zone["radius"])
            if edge_dist < shortest_dist:
                shortest_dist = edge_dist
                if dist > 0:
                    nearest_vec = [dx / dist, dy / dist]

        return nearest_vec, shortest_dist

    def target_vector(self, target_pos):
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            return [0.0, 0.0], 0.0
        return [dx / dist, dy / dist], dist

    def boundary_warning(self):
        half_w = config.SCREEN_WIDTH / 2
        half_h = config.SCREEN_HEIGHT / 2
        margin = config.BOUNDARY_MARGIN
        distances = [
            self.pos[0] + half_w,
            half_w - self.pos[0],
            self.pos[1] + half_h,
            half_h - self.pos[1],
        ]
        nearest = min(distances)
        return 1.0 - max(0.0, min(1.0, nearest / margin))

    def record_flow_alignment(self, fluid_force, speed):
        flow_speed = math.hypot(fluid_force[0], fluid_force[1])
        if flow_speed == 0:
            return
        dot = self.vel[0] * fluid_force[0] + self.vel[1] * fluid_force[1]
        alignment = dot / (speed * flow_speed)
        self.flow_alignment_sum += max(-1.0, min(1.0, alignment))
        self.flow_alignment_samples += 1

    def current_flow_alignment(self, fluid_force):
        speed = math.hypot(self.vel[0], self.vel[1])
        flow_speed = math.hypot(fluid_force[0], fluid_force[1])
        if speed == 0 or flow_speed == 0:
            return 0.0
        dot = self.vel[0] * fluid_force[0] + self.vel[1] * fluid_force[1]
        return max(-1.0, min(1.0, dot / (speed * flow_speed)))

    def average_flow_alignment(self):
        if self.flow_alignment_samples == 0:
            return 0.0
        return self.flow_alignment_sum / self.flow_alignment_samples

    def update_memory(self, memory_outputs):
        for i in range(config.MEMORY_SIZE):
            write = memory_outputs[i] if i < len(memory_outputs) else 0.0
            self.memory[i] = (
                self.memory[i] * config.MEMORY_DECAY
                + write * (1.0 - config.MEMORY_DECAY)
            )

    def normalize_distance(self, distance, max_distance):
        if distance == float("inf"):
            return 1.0
        return max(0.0, min(1.0, distance / max_distance))

    def check_collisions(self, obstacles, target_pos):
        if not self.alive:
            return

        w, h = config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2
        if (
            self.pos[0] < -w
            or self.pos[0] > w
            or self.pos[1] < -h
            or self.pos[1] > h
        ):
            self.crashed = True
            self.alive = False
            return

        for obs in obstacles:
            dist = math.hypot(self.pos[0] - obs["pos"][0], self.pos[1] - obs["pos"][1])
            if dist < obs["radius"] + self.radius:
                self.crashed = True
                self.alive = False
                return

        target_dist = math.hypot(self.pos[0] - target_pos[0], self.pos[1] - target_pos[1])
        if target_dist <= config.TARGET_RADIUS + self.radius:
            self.reached_target = True

    def calculate_fitness(self, target_pos):
        target_dist = math.hypot(self.pos[0] - target_pos[0], self.pos[1] - target_pos[1])
        self.closest_target_dist = min(self.closest_target_dist, target_dist)
        start_dist = math.hypot(self.start_pos[0] - target_pos[0], self.start_pos[1] - target_pos[1])
        progress = max(0.0, start_dist - self.closest_target_dist)

        survival_score = self.age * config.SURVIVAL_TIME_WEIGHT
        food_score = self.food_eaten * config.FOOD_SCORE
        nutrient_score = self.nutrient_absorbed * config.NUTRIENT_SCORE
        progress_score = (progress / max(1.0, start_dist)) * config.PROGRESS_SCORE
        flow_score = max(0.0, self.average_flow_alignment()) * config.FLOW_ALIGNMENT_SCORE
        energy_score = max(0.0, self.energy) * config.ENERGY_SCORE
        curriculum_score = self.reached_target * config.CURRICULUM_SCORE
        target_bonus = config.TARGET_REACHED_BONUS if self.reached_target else 0.0
        crash_penalty = 90.0 if self.crashed else 0.0

        self.behavior_score = (
            survival_score
            + food_score
            + nutrient_score
            + progress_score
            + flow_score
            + energy_score
            + curriculum_score
            + target_bonus
            - crash_penalty
        )
        self.fitness = max(1.0, self.behavior_score + self.novelty)

    def behavior_descriptor(self, target_pos):
        start_dist = math.hypot(self.start_pos[0] - target_pos[0], self.start_pos[1] - target_pos[1])
        closest = min(
            self.closest_target_dist,
            math.hypot(self.pos[0] - target_pos[0], self.pos[1] - target_pos[1]),
        )
        progress = max(0.0, start_dist - closest) / max(1.0, start_dist)
        survival = self.age / max(1.0, config.SIMULATION_STEPS)
        food = self.food_eaten / max(1.0, config.FOOD_COUNT)
        alignment = (self.average_flow_alignment() + 1.0) * 0.5
        return (
            max(0.0, min(1.0, progress)),
            max(0.0, min(1.0, survival)),
            max(0.0, min(1.0, food)),
            max(0.0, min(1.0, alignment)),
        )
