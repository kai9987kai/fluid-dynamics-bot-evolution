
# Simulation Constants
POPULATION_SIZE = 20
GENERATIONS = 100
SIMULATION_STEPS = 400  # Increased steps to allow time for foraging

# Physics & Environment
FLUID_SCALE = 50.0      # Scale for sine wave flow field
FLUID_STRENGTH = 0.5    # Max force of the flow
DRAG_COEFFICIENT = 0.05
MAX_SPEED = 5.0
THRUST_POWER = 0.5
OBSTACLE_SPEED = 1.0

# Energy System
STARTING_ENERGY = 100.0
ENERGY_CONSUMPTION_RATE = 0.1  # Per frame
THRUST_ENERGY_COST = 0.05      # Per unit of thrust
FOOD_ENERGY_VALUE = 50.0
FOOD_COUNT = 10

# Neural Network Inputs
# 3 Raycasts + 2 Velocity + 2 Fluid Force + 2 Nearest Food Vector + 1 Energy Level
INPUT_SIZE = 10
HIDDEN_SIZE = 12
OUTPUT_SIZE = 2  # Thrust Left/Right (-1 to 1), Thrust Forward (0 to 1)

# Genetic Algorithm
MUTATION_RATE = 0.1
MUTATION_AMOUNT = 0.5
ELITISM_COUNT = 2

# Visualization
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
OFFSET_X = 0
OFFSET_Y = 0
