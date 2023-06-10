import turtle
import random
import math
import threading
import queue
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Set up the window
window = turtle.Screen()
window.title("Fluid Dynamics Bot Simulation")
window.bgcolor("white")

# Set up the turtle
bot_turtle = turtle.Turtle()
bot_turtle.penup()

# Set up the genetic algorithm parameters
population_size = 10
mutation_rate = 0.1

# Set up the neural network parameters
num_inputs = 2
num_hidden = 20
num_outputs = 2

# Define the fluid dynamics simulation
def simulate_fluid_dynamics(bot_shape):
    fluid_force = (0, 0)  # Placeholder, you can implement the actual fluid forces here
    return fluid_force

# Define the bot's movement behavior
def move(bot):
    # Calculate fluid forces
    fluid_force = simulate_fluid_dynamics(bot['shape'])

    # Update bot's position and shape based on the fluid forces
    x_avg = sum([vertex[0] for vertex in bot['shape']]) / len(bot['shape'])
    y_avg = sum([vertex[1] for vertex in bot['shape']]) / len(bot['shape'])
    x_avg += fluid_force[0]
    y_avg += fluid_force[1]
    bot['shape'] = [(vertex[0] + fluid_force[0], vertex[1] + fluid_force[1]) for vertex in bot['shape']]

    # Calculate inputs for neural network
    inputs = [x_avg, y_avg]

    # Feed-forward neural network
    hidden = [sum([inputs[i] * bot['weights_ih'][i][j] for i in range(num_inputs)]) for j in range(num_hidden)]
    hidden = [math.tanh(value) for value in hidden]
    outputs = [sum([hidden[i] * bot['weights_ho'][i][j] for i in range(num_hidden)]) for j in range(num_outputs)]
    outputs = [math.tanh(value) for value in outputs]

    # Choose the action based on the outputs
    if outputs[0] > 0:
        bot['shape'][0] = (bot['shape'][0][0] + 0.1, bot['shape'][0][1])
    if outputs[1] > 0:
        bot['shape'][1] = (bot['shape'][1][0] - 0.1, bot['shape'][1][1])
    else:
        bot['shape'][2] = (bot['shape'][2][0] + 0.1, bot['shape'][2][1])

# Set up the evolution loop
generations = 100

# Thread function to run a single generation
def run_generation(gen, output_queue):
    # Generate initial population
    population = [{
        'shape': [(0, -10), (-5, 10), (5, 10)],
        'weights_ih': [[random.uniform(-1, 1) for _ in range(num_hidden)] for _ in range(num_inputs)],
        'weights_ho': [[random.uniform(-1, 1) for _ in range(num_outputs)] for _ in range(num_hidden)]
    } for _ in range(population_size)]

    # Run simulations for the current generation
    for bot_num, bot in enumerate(population):
        logging.info(f"Generation: {gen + 1}, Bot: {bot_num + 1}")

        # Play the game with the current bot's shape
        bot_shape = bot['shape']
        for _ in range(100):
            # Move the bot based on fluid forces and neural network output
            move(bot)

    # Select the fittest bot for reproduction
    population.sort(key=lambda x: sum([vertex[1] for vertex in x['shape']]), reverse=True)
    fittest_bot = population[0]

    # Add the fittest bot's shape to the output queue
    output_queue.put((gen, fittest_bot['shape']))

# Create a queue for storing the output of each generation
output_queue = queue.Queue()

# Create a list to store the threads
threads = []

# Execute the generations using threading
for gen in range(generations):
    thread = threading.Thread(target=run_generation, args=(gen, output_queue))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

# Process the output queue to get the fittest bot's shape for each generation
results = []
while not output_queue.empty():
    results.append(output_queue.get())

# Render the final results in the turtle window
for gen, fittest_shape in results:
    bot_turtle.clear()
    for vertex in fittest_shape:
        bot_turtle.goto(vertex[0], vertex[1])
        bot_turtle.pendown()
    bot_turtle.penup()
    turtle.update()
    logging.info("Generation: {}, Fittest bot's shape: {}".format(gen + 1, fittest_shape))

# Keep the window open after the simulation finishes
turtle.done()
