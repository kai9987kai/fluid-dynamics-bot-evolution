import csv
import json
import math
import random

import config
from bot import Bot
from genome import Genome


class Simulation:
    def __init__(self, seed=None, initial_genome=None):
        if seed is None:
            seed = config.RANDOM_SEED
        if seed is not None:
            random.seed(seed)

        self.generation = 0
        self.step_count = 0
        self.base_target_pos = (350, 0)
        self.target_pos = self.base_target_pos
        self.population = self.create_population(initial_genome)
        self.obstacles = self.generate_obstacles()
        self.foods = self.generate_food()
        self.nutrient_zones = self.generate_nutrient_zones()
        self.archive = {}
        self.history = []
        self.last_stats = {}
        self.best_genome = None

    def create_population(self, initial_genome=None):
        if initial_genome is None:
            return [
                Bot(pos_x=-300, pos_y=random.uniform(-100, 100))
                for _ in range(config.POPULATION_SIZE)
            ]

        population = [self.spawn_bot(initial_genome.clone())]
        while len(population) < config.POPULATION_SIZE:
            genome = initial_genome.clone()
            genome.mutate()
            population.append(self.spawn_bot(genome))
        return population

    def difficulty(self):
        if not config.CURRICULUM_ENABLED:
            return 1.0
        return min(
            config.MAX_CURRICULUM_DIFFICULTY,
            1.0 + self.generation * config.CURRICULUM_STEP,
        )

    def generate_obstacles(self):
        obstacles = []
        for _ in range(config.OBSTACLE_COUNT):
            angle = random.uniform(0, 2 * math.pi)
            speed = config.OBSTACLE_SPEED
            obstacles.append({
                "pos": [random.uniform(-100, 200), random.uniform(-200, 200)],
                "radius": random.uniform(15, 30),
                "vel": [math.cos(angle) * speed, math.sin(angle) * speed],
            })
        return obstacles

    def generate_food(self):
        return [self.create_one_food() for _ in range(config.FOOD_COUNT)]

    def create_one_food(self):
        return {
            "pos": [random.uniform(-350, 350), random.uniform(-250, 250)],
            "energy": config.FOOD_ENERGY_VALUE,
        }

    def generate_nutrient_zones(self):
        zones = []
        for index in range(config.NUTRIENT_ZONE_COUNT):
            zones.append({
                "pos": [random.uniform(-250, 250), random.uniform(-190, 190)],
                "radius": config.NUTRIENT_ZONE_RADIUS,
                "phase": random.uniform(0, 2 * math.pi),
                "index": index,
            })
        return zones

    def get_flow_force(self, x, y, step=None):
        if step is None:
            step = self.step_count

        scale = config.FLUID_SCALE
        strength = config.FLUID_STRENGTH
        t = step * config.FLOW_TIME_SCALE

        wave_x = math.cos((y / scale) + t) * strength
        wave_y = math.sin((x / scale) - t * 0.7) * strength

        vortex_x = 0.0
        vortex_y = 0.0
        centers = [(-120.0, -80.0), (120.0, 90.0)]
        for index, (cx, cy) in enumerate(centers):
            dx = x - cx
            dy = y - cy
            radius_sq = dx * dx + dy * dy + 1.0
            envelope = math.exp(-radius_sq / (config.FLOW_VORTEX_RADIUS**2))
            direction = 1.0 if index % 2 == 0 else -1.0
            swirl = direction * config.FLOW_VORTEX_STRENGTH * envelope
            vortex_x += -dy / config.FLOW_VORTEX_RADIUS * swirl
            vortex_y += dx / config.FLOW_VORTEX_RADIUS * swirl

        fx = wave_x + vortex_x + config.FLOW_DRIFT
        fy = wave_y + vortex_y
        return (fx, fy)

    def update(self):
        self.step_count += 1
        self.update_target()
        self.update_obstacles()
        self.update_nutrient_zones()

        alive_count = 0
        for bot in self.population:
            if not bot.alive:
                continue

            fluid_force = self.get_flow_force(bot.pos[0], bot.pos[1])
            bot.update(
                fluid_force,
                self.obstacles,
                self.foods,
                self.nutrient_zones,
                self.target_pos,
            )

            self.handle_food_collisions(bot)
            self.handle_nutrient_absorption(bot)

            if bot.alive:
                alive_count += 1

        return alive_count

    def update_target(self):
        if self.generation < config.TARGET_DRIFT_START_GENERATION:
            self.target_pos = self.base_target_pos
            return

        denominator = max(0.001, config.MAX_CURRICULUM_DIFFICULTY - 1.0)
        difficulty_ratio = max(0.0, min(1.0, (self.difficulty() - 1.0) / denominator))
        radius = config.TARGET_DRIFT_RADIUS * difficulty_ratio
        t = self.step_count * config.TARGET_DRIFT_RATE
        self.target_pos = (
            self.base_target_pos[0] + math.cos(t) * radius,
            self.base_target_pos[1] + math.sin(t * 0.7) * radius,
        )

    def update_nutrient_zones(self):
        w, h = config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2
        for zone in self.nutrient_zones:
            x, y = zone["pos"]
            flow_x, flow_y = self.get_flow_force(x, y)
            pulse = math.sin(self.step_count * 0.02 + zone["phase"]) * 0.5 + 0.5
            zone["radius"] = config.NUTRIENT_ZONE_RADIUS * (0.75 + pulse * 0.5)
            zone["pos"][0] += flow_x * config.NUTRIENT_ZONE_DRIFT
            zone["pos"][1] += flow_y * config.NUTRIENT_ZONE_DRIFT

            if zone["pos"][0] < -w:
                zone["pos"][0] = w
            elif zone["pos"][0] > w:
                zone["pos"][0] = -w
            if zone["pos"][1] < -h:
                zone["pos"][1] = h
            elif zone["pos"][1] > h:
                zone["pos"][1] = -h

    def handle_food_collisions(self, bot):
        if not bot.alive:
            return

        for i in range(len(self.foods) - 1, -1, -1):
            food = self.foods[i]
            dist = math.hypot(bot.pos[0] - food["pos"][0], bot.pos[1] - food["pos"][1])
            if dist < bot.radius + 10:
                bot.energy += food["energy"]
                bot.food_eaten += 1
                self.foods[i] = self.create_one_food()

    def handle_nutrient_absorption(self, bot):
        if not bot.alive:
            return

        for zone in self.nutrient_zones:
            dist = math.hypot(bot.pos[0] - zone["pos"][0], bot.pos[1] - zone["pos"][1])
            if dist < zone["radius"] + bot.radius:
                overlap = 1.0 - max(0.0, dist - bot.radius) / zone["radius"]
                gained = config.NUTRIENT_ENERGY_RATE * max(0.0, overlap)
                bot.energy += gained
                bot.nutrient_absorbed += gained

    def update_obstacles(self):
        w, h = config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2
        difficulty = self.difficulty()
        for obs in self.obstacles:
            obs["pos"][0] += obs["vel"][0] * difficulty
            obs["pos"][1] += obs["vel"][1] * difficulty
            if obs["pos"][0] < -w + obs["radius"] or obs["pos"][0] > w - obs["radius"]:
                obs["vel"][0] *= -1
            if obs["pos"][1] < -h + obs["radius"] or obs["pos"][1] > h - obs["radius"]:
                obs["vel"][1] *= -1

    def calculate_fitness(self):
        descriptors = [bot.behavior_descriptor(self.target_pos) for bot in self.population]
        for bot, descriptor in zip(self.population, descriptors):
            bot.novelty = self.calculate_novelty(descriptor, descriptors)
            bot.calculate_fitness(self.target_pos)
            self.update_archive(bot, descriptor)

    def calculate_novelty(self, descriptor, generation_descriptors):
        references = list(generation_descriptors)
        references.extend(record["descriptor"] for record in self.archive.values())
        distances = [
            self.descriptor_distance(descriptor, other)
            for other in references
            if other is not descriptor
        ]
        if not distances:
            return 0.0
        distances.sort()
        neighbors = distances[:config.NOVELTY_NEIGHBORS]
        return (sum(neighbors) / len(neighbors)) * config.NOVELTY_WEIGHT

    def descriptor_distance(self, a, b):
        return math.sqrt(sum((av - bv) ** 2 for av, bv in zip(a, b)))

    def update_archive(self, bot, descriptor):
        key = self.archive_key(descriptor)
        record = self.archive.get(key)
        if record is None or bot.behavior_score > record["score"]:
            self.archive[key] = {
                "score": bot.behavior_score,
                "fitness": bot.fitness,
                "descriptor": descriptor,
                "genome": bot.genome.clone(),
                "generation": self.generation,
            }

    def archive_key(self, descriptor):
        progress, survival, food, alignment = descriptor
        return (
            min(config.ARCHIVE_PROGRESS_BINS - 1, int(progress * config.ARCHIVE_PROGRESS_BINS)),
            min(config.ARCHIVE_SURVIVAL_BINS - 1, int(survival * config.ARCHIVE_SURVIVAL_BINS)),
            min(config.ARCHIVE_FOOD_BINS - 1, int(food * config.ARCHIVE_FOOD_BINS)),
            min(config.ARCHIVE_ALIGNMENT_BINS - 1, int(alignment * config.ARCHIVE_ALIGNMENT_BINS)),
        )

    def evolve(self):
        self.calculate_fitness()
        self.population.sort(key=lambda b: b.fitness, reverse=True)
        self.best_genome = self.population[0].genome.clone()
        self.last_stats = self.generation_stats()
        self.history.append(self.last_stats.copy())

        print(
            f"Gen {self.generation}: "
            f"Best={self.last_stats['best_fitness']:.1f}, "
            f"Avg={self.last_stats['avg_fitness']:.1f}, "
            f"Food={self.last_stats['best_food']}, "
            f"Archive={self.last_stats['archive_size']}, "
            f"Difficulty={self.last_stats['difficulty']:.2f}"
        )

        new_pop = []
        elite_count = min(config.ELITISM_COUNT, len(self.population))
        for i in range(elite_count):
            new_pop.append(self.spawn_bot(self.population[i].genome.clone()))

        while len(new_pop) < config.POPULATION_SIZE:
            p1 = self.select_parent()
            p2 = self.select_parent()
            child_genome = p1.genome.crossover(p2.genome)
            child_genome.mutate()
            new_pop.append(self.spawn_bot(child_genome))

        self.population = new_pop
        self.generation += 1
        self.step_count = 0
        self.foods = self.generate_food()
        self.nutrient_zones = self.generate_nutrient_zones()

    def spawn_bot(self, genome):
        return Bot(pos_x=-300, pos_y=random.uniform(-100, 100), genome=genome)

    def select_parent(self):
        if self.archive and random.random() < config.ARCHIVE_PARENT_RATE:
            record = random.choice(list(self.archive.values()))
            return self.spawn_bot(record["genome"].clone())

        size = min(config.TOURNAMENT_SIZE, len(self.population))
        tournament = random.sample(self.population, size)
        tournament.sort(key=lambda b: b.fitness, reverse=True)
        return tournament[0]

    def generation_stats(self):
        fitnesses = [bot.fitness for bot in self.population]
        best = self.population[0]
        return {
            "generation": self.generation,
            "best_fitness": best.fitness,
            "avg_fitness": sum(fitnesses) / len(fitnesses),
            "best_food": best.food_eaten,
            "best_nutrient": best.nutrient_absorbed,
            "best_age": best.age,
            "best_reached_target": best.reached_target,
            "reached_count": sum(1 for bot in self.population if bot.reached_target),
            "archive_size": len(self.archive),
            "difficulty": self.difficulty(),
            "best_traits": best.traits.copy(),
        }

    def save_best_genome(self, path):
        if self.best_genome is None:
            if not self.population:
                raise ValueError("No population available to save.")
            self.population.sort(key=lambda b: b.fitness, reverse=True)
            self.best_genome = self.population[0].genome.clone()

        data = {
            "generation": self.generation,
            "stats": self.last_stats,
            "genome": self.best_genome.to_dict(),
        }
        with open(path, "w", encoding="utf-8") as output:
            json.dump(data, output, indent=2)

    def export_history_csv(self, path):
        fields = [
            "generation",
            "best_fitness",
            "avg_fitness",
            "best_food",
            "best_nutrient",
            "best_age",
            "best_reached_target",
            "reached_count",
            "archive_size",
            "difficulty",
        ]
        with open(path, "w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            for row in self.history:
                writer.writerow({field: row.get(field) for field in fields})

    @staticmethod
    def load_genome(path):
        with open(path, "r", encoding="utf-8") as source:
            data = json.load(source)
        return Genome.from_dict(data["genome"])
