import argparse
import math
import turtle

import config
from simulation import Simulation


def draw_vector(t, start, vector, color="blue", scale=1.0):
    t.penup()
    t.goto(start)
    t.pendown()
    t.color(color)
    t.goto(start[0] + vector[0] * scale, start[1] + vector[1] * scale)
    t.penup()


def draw_flow_field(t, sim):
    step = config.FLOW_VECTOR_STEP
    w = config.SCREEN_WIDTH // 2
    h = config.SCREEN_HEIGHT // 2
    t.clear()
    t.color("lightblue")
    t.width(1)

    for x in range(-w, w + 1, step):
        for y in range(-h, h + 1, step):
            vector = sim.get_flow_force(x, y)
            draw_vector(t, (x, y), vector, "lightblue", config.FLOW_VECTOR_SCALE)


def draw_bot(t, bot, is_best=False):
    energy_ratio = max(0.0, min(1.0, bot.energy / config.STARTING_ENERGY))
    color = "blue" if is_best else (1.0 - energy_ratio, energy_ratio, 0.0)

    length = bot.traits["body_length"]
    width = bot.traits["body_width"]
    nose = (
        bot.pos[0] + math.cos(bot.angle) * length,
        bot.pos[1] + math.sin(bot.angle) * length,
    )
    left = (
        bot.pos[0] + math.cos(bot.angle + 2.45) * width,
        bot.pos[1] + math.sin(bot.angle + 2.45) * width,
    )
    right = (
        bot.pos[0] + math.cos(bot.angle - 2.45) * width,
        bot.pos[1] + math.sin(bot.angle - 2.45) * width,
    )

    t.color(color)
    t.goto(nose)
    t.pendown()
    t.goto(left)
    t.goto(right)
    t.goto(nose)
    t.penup()


def draw_sensors(t, bot):
    t.color("grey")
    sensor_range = bot.traits["sensor_range"]
    for j, reading in enumerate(bot.sensor_readings):
        ray_angle = bot.angle + bot.ray_angles[j]
        dist = (1.0 - reading) * sensor_range
        start_x, start_y = bot.pos
        end_x = start_x + math.cos(ray_angle) * dist
        end_y = start_y + math.sin(ray_angle) * dist

        t.goto(start_x, start_y)
        t.pendown()
        t.goto(end_x, end_y)
        t.penup()


def draw_nutrient_zones(t, sim):
    for zone in sim.nutrient_zones:
        t.color("aquamarine")
        t.goto(zone["pos"][0], zone["pos"][1] - zone["radius"])
        t.setheading(0)
        t.pendown()
        t.circle(zone["radius"])
        t.penup()
        t.goto(zone["pos"][0], zone["pos"][1])
        t.dot(4, "dark green")


def draw_overlay(t, sim, alive_count):
    stats = sim.last_stats
    best = stats.get("best_fitness", 0.0)
    avg = stats.get("avg_fitness", 0.0)
    archive = len(sim.archive)
    difficulty = sim.difficulty()
    t.color("black")
    t.goto(-config.SCREEN_WIDTH / 2 + 12, config.SCREEN_HEIGHT / 2 - 28)
    t.write(
        f"Gen {sim.generation}  Step {sim.step_count}  Alive {alive_count}  "
        f"Best {best:.1f}  Avg {avg:.1f}  Archive {archive}  Difficulty {difficulty:.2f}",
        align="left",
        font=("Arial", 10, "normal"),
    )


def draw_scene(bot_turtle, bg_turtle, sim, alive_count):
    if sim.step_count % config.FLOW_VISUAL_REFRESH_STEPS == 1:
        draw_flow_field(bg_turtle, sim)

    bot_turtle.clear()
    draw_nutrient_zones(bot_turtle, sim)

    bot_turtle.color("red")
    for obs in sim.obstacles:
        bot_turtle.goto(obs["pos"][0], obs["pos"][1] - obs["radius"])
        bot_turtle.setheading(0)
        bot_turtle.pendown()
        bot_turtle.circle(obs["radius"])
        bot_turtle.penup()

    bot_turtle.color("green")
    for food in sim.foods:
        bot_turtle.goto(food["pos"][0], food["pos"][1])
        bot_turtle.dot(5)

    bot_turtle.color("purple")
    bot_turtle.goto(sim.target_pos[0], sim.target_pos[1] - config.TARGET_RADIUS)
    bot_turtle.pendown()
    bot_turtle.circle(config.TARGET_RADIUS)
    bot_turtle.penup()

    for i, bot in enumerate(sim.population):
        if not bot.alive:
            continue
        is_best = i == 0
        draw_bot(bot_turtle, bot, is_best)
        if is_best:
            draw_sensors(bot_turtle, bot)

    draw_overlay(bot_turtle, sim, alive_count)


def run_headless(generations, steps, seed=None, initial_genome=None):
    sim = Simulation(seed=seed, initial_genome=initial_genome)
    for _ in range(generations):
        for _ in range(steps):
            alive_count = sim.update()
            if alive_count == 0:
                break
        sim.evolve()
    return sim


def run_visual(generations, steps, seed=None, initial_genome=None):
    window = turtle.Screen()
    window.title("Evolutionary Fluid Dynamics: Memory, Nutrients, Quality Diversity")
    window.setup(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    window.bgcolor("white")
    window.tracer(0)

    bot_turtle = turtle.Turtle()
    bot_turtle.hideturtle()
    bot_turtle.penup()

    bg_turtle = turtle.Turtle()
    bg_turtle.hideturtle()
    bg_turtle.penup()

    sim = Simulation(seed=seed, initial_genome=initial_genome)
    draw_flow_field(bg_turtle, sim)

    for _ in range(generations):
        for _ in range(steps):
            alive_count = sim.update()
            draw_scene(bot_turtle, bg_turtle, sim, alive_count)
            window.update()
            if alive_count == 0:
                break
        sim.evolve()

    turtle.done()
    return sim


def parse_args():
    parser = argparse.ArgumentParser(description="Evolve bots in a dynamic fluid field.")
    parser.add_argument("--headless", action="store_true", help="Run without turtle graphics.")
    parser.add_argument("--generations", type=int, default=config.GENERATIONS)
    parser.add_argument("--steps", type=int, default=config.SIMULATION_STEPS)
    parser.add_argument("--seed", type=int, default=config.RANDOM_SEED)
    parser.add_argument("--load-genome", help="Seed the population from a saved best genome JSON.")
    parser.add_argument("--save-best", help="Write the best genome from the run to JSON.")
    parser.add_argument("--history-csv", help="Write generation stats to a CSV file.")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        initial_genome = None
        if args.load_genome:
            initial_genome = Simulation.load_genome(args.load_genome)

        if args.headless:
            sim = run_headless(args.generations, args.steps, args.seed, initial_genome)
        else:
            sim = run_visual(args.generations, args.steps, args.seed, initial_genome)

        if args.save_best:
            sim.save_best_genome(args.save_best)
        if args.history_csv:
            sim.export_history_csv(args.history_csv)
    except turtle.Terminator:
        print("Simulation window closed.")


if __name__ == "__main__":
    main()
