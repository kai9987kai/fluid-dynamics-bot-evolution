
# Simulation Constants
POPULATION_SIZE = 20
GENERATIONS = 100
SIMULATION_STEPS = 400  # Increased steps to allow time for foraging
RANDOM_SEED = None

# Physics & Environment
FLUID_SCALE = 50.0      # Scale for sine wave flow field
FLUID_STRENGTH = 0.5    # Max force of the flow
FLOW_DRIFT = 0.2
FLOW_TIME_SCALE = 0.025
FLOW_VORTEX_STRENGTH = 0.35
FLOW_VORTEX_RADIUS = 180.0
FLOW_SAMPLE_RADIUS = 35.0
DRAG_COEFFICIENT = 0.05
MAX_SPEED = 5.0
THRUST_POWER = 0.5
BOT_COLLISION_RADIUS = 5.0
TARGET_RADIUS = 15.0
OBSTACLE_COUNT = 5
OBSTACLE_SPEED = 1.0
CURRICULUM_ENABLED = True
CURRICULUM_STEP = 0.035
MAX_CURRICULUM_DIFFICULTY = 1.75
TARGET_DRIFT_START_GENERATION = 2
TARGET_DRIFT_RADIUS = 55.0
TARGET_DRIFT_RATE = 0.018

# Energy System
STARTING_ENERGY = 100.0
ENERGY_CONSUMPTION_RATE = 0.1  # Per frame
THRUST_ENERGY_COST = 0.05      # Per unit of thrust
FOOD_ENERGY_VALUE = 50.0
FOOD_COUNT = 10
NUTRIENT_ZONE_COUNT = 3
NUTRIENT_ZONE_RADIUS = 45.0
NUTRIENT_ZONE_DRIFT = 0.65
NUTRIENT_ENERGY_RATE = 0.08
NUTRIENT_SCORE = 18.0

# Neural Network Inputs
# Raycasts + Velocity + Fluid Force + Nearest Food Vector + Target Vector
# + Target Distance + Energy + Flow Alignment + Boundary Warning
# + Nearest Nutrient Vector/Distance + Memory
SENSOR_RAY_COUNT = 5
BASE_SENSOR_RANGE = 200.0
BOUNDARY_MARGIN = 80.0
MEMORY_SIZE = 2
MEMORY_DECAY = 0.65
SENSOR_AUX_INPUTS = 16
INPUT_SIZE = SENSOR_RAY_COUNT + SENSOR_AUX_INPUTS + MEMORY_SIZE
HIDDEN_SIZE = 12
OUTPUT_SIZE = 2 + MEMORY_SIZE  # Steering, thrust, recurrent memory writes

# Genetic Algorithm
MUTATION_RATE = 0.1
MUTATION_AMOUNT = 0.5
ELITISM_COUNT = 2
TOURNAMENT_SIZE = 3

# Morphology genes evolve alongside the neural controller. Values are clamped
# inside these ranges after crossover and mutation.
MORPHOLOGY_TRAITS = {
    "body_length": (8.0, 18.0),
    "body_width": (5.0, 14.0),
    "sensor_range": (140.0, 300.0),
    "sensor_spread": (0.55, 1.35),
    "drag_scale": (0.75, 1.35),
    "thrust_scale": (0.75, 1.35),
    "turn_rate": (0.12, 0.32),
    "energy_efficiency": (0.75, 1.25),
}
TRAIT_MUTATION_RATE = 0.18
TRAIT_MUTATION_AMOUNT = 0.08

# Quality-diversity evolution keeps distinct behavioral niches alive instead of
# selecting only the current top scorer.
NOVELTY_WEIGHT = 35.0
NOVELTY_NEIGHBORS = 5
ARCHIVE_PARENT_RATE = 0.18
ARCHIVE_PROGRESS_BINS = 5
ARCHIVE_SURVIVAL_BINS = 4
ARCHIVE_FOOD_BINS = 4
ARCHIVE_ALIGNMENT_BINS = 3
SURVIVAL_TIME_WEIGHT = 0.35
FOOD_SCORE = 60.0
PROGRESS_SCORE = 250.0
FLOW_ALIGNMENT_SCORE = 25.0
TARGET_REACHED_BONUS = 600.0
ENERGY_SCORE = 0.15
CURRICULUM_SCORE = 18.0

# Visualization
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
OFFSET_X = 0
OFFSET_Y = 0
FLOW_VECTOR_STEP = 100
FLOW_VECTOR_SCALE = 40
FLOW_VISUAL_REFRESH_STEPS = 25
