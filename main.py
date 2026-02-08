
import turtle
import time
import math
import config
from simulation import Simulation

def draw_vector(t, start, vector, color="blue", scale=1.0):
    t.penup()
    t.goto(start)
    t.pendown()
    t.color(color)
    t.goto(start[0] + vector[0]*scale, start[1] + vector[1]*scale)

def draw_flow_field(t):
    # Draw a grid of arrows
    step = 100
    w = config.SCREEN_WIDTH // 2
    h = config.SCREEN_HEIGHT // 2
    t.color("lightblue")
    t.width(1)
    
    # We need a dummy sim to calc force or duplicate logic? 
    # Let's duplicate logic for visualization efficiency to avoid passing full sim
    scale = config.FLUID_SCALE
    strength = config.FLUID_STRENGTH
    
    for x in range(-w, w, step):
        for y in range(-h, h, step):
            fx = math.cos(y / scale) * strength + 0.2
            fy = math.sin(x / scale) * strength
            draw_vector(t, (x, y), (fx, fy), "lightblue", 40)

def main():
    # Setup Window (Using try-except to handle potential Tkinter errors if closed)
    try:
        window = turtle.Screen()
        window.title("Evolutionary Fluid Dynamics: Chaos & Metabolism")
        window.setup(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        window.bgcolor("white")
        window.tracer(0) 

        # Setup Turtles
        bot_turtle = turtle.Turtle()
        bot_turtle.hideturtle()
        bot_turtle.penup()
        
        bg_turtle = turtle.Turtle()
        bg_turtle.hideturtle()
        bg_turtle.penup()
        
        sim = Simulation()
        
        # Draw Background Flow once
        draw_flow_field(bg_turtle)
        
        # Simulation Loop
        for gen in range(config.GENERATIONS):
            
            # Run Steps
            for step in range(config.SIMULATION_STEPS):
                alive_count = sim.update()
                
                # Visualization
                bot_turtle.clear()
                
                # Draw Obstacles
                bot_turtle.color("red")
                for obs in sim.obstacles:
                    bot_turtle.goto(obs['pos'][0], obs['pos'][1] - obs['radius'])
                    bot_turtle.setheading(0)
                    bot_turtle.pendown()
                    bot_turtle.circle(obs['radius'])
                    bot_turtle.penup()
                
                # Draw Food
                bot_turtle.color("green")
                for food in sim.foods:
                    bot_turtle.goto(food['pos'][0], food['pos'][1])
                    bot_turtle.dot(5) # Draw food as dot
                
                # Draw Target
                bot_turtle.color("purple") # Change target color to distinct from food
                bot_turtle.goto(sim.target_pos[0], sim.target_pos[1]-10)
                bot_turtle.pendown()
                bot_turtle.circle(10)
                bot_turtle.penup()

                for i, bot in enumerate(sim.population):
                    if not bot.alive:
                        continue
                        
                    is_best = (i == 0)
                    
                    # Color based on energy?
                    # Full energy = Orange, Low = Black/Grey
                    energy_ratio = max(0, min(1, bot.energy / config.STARTING_ENERGY))
                    color = (1.0 - energy_ratio, energy_ratio, 0) # R->G gradient
                    if is_best: color = "blue" # Highlight best
                    
                    bot_turtle.goto(bot.pos)
                    bot_turtle.setheading(math.degrees(bot.angle))
                    bot_turtle.color(color)
                    
                    bot_turtle.pendown()
                    bot_turtle.forward(10)
                    bot_turtle.right(120)
                    bot_turtle.forward(10)
                    bot_turtle.right(120)
                    bot_turtle.forward(10)
                    bot_turtle.right(120)
                    bot_turtle.penup()
                    
                    # Draw Sensors for Best Bot
                    if is_best:
                        bot_turtle.color("grey")
                        for j, reading in enumerate(bot.sensor_readings):
                            ray_angle = bot.angle + bot.ray_angles[j]
                            dist = (1.0 - reading) * 200.0
                            start_x, start_y = bot.pos
                            end_x = start_x + math.cos(ray_angle) * dist
                            end_y = start_y + math.sin(ray_angle) * dist
                            
                            bot_turtle.goto(start_x, start_y)
                            bot_turtle.pendown()
                            bot_turtle.goto(end_x, end_y)
                            bot_turtle.penup()
                    
                window.update()
                if alive_count == 0:
                    break
                    
            sim.evolve()

        turtle.done()
    except turtle.Terminator:
        print("Simulation window closed.") 

if __name__ == "__main__":
    main()
