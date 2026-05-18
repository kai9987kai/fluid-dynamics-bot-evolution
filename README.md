# fluid-dynamics-bot-evolution

An evolutionary robotics simulation where neural-network bots learn to survive and navigate a dynamic 2D fluid environment. Bots evolve both their controller weights and body morphology while dealing with moving obstacles, food, drifting nutrient currents, vortex-like flow fields, and a target that becomes harder to reach as the curriculum advances.

The project uses only the Python standard library. Visualization is handled with `turtle`, and the same simulation can run headlessly for faster experiments.

## What It Does

- Evolves a population of bots over many generations.
- Uses neural controllers with recurrent memory outputs.
- Evolves morphology traits such as body length, body width, sensor range, sensor spread, drag scale, thrust scale, turn rate, and energy efficiency.
- Simulates time-varying fluid flow with waves, vortices, drag, and a constant drift.
- Adds food particles and drifting nutrient zones as energy sources.
- Uses moving obstacles and a curriculum that increases difficulty over time.
- Preserves diverse behavioral niches with a quality-diversity archive.
- Saves best genomes to JSON and exports generation history to CSV.

## Current Features

### Evolution

- Tournament selection
- Crossover and mutation
- Elitism
- Quality-diversity archive
- Novelty scoring from behavior descriptors
- Archive-seeded parent selection
- Save/load best genome workflow

### Bot Intelligence

- Feed-forward neural network with recurrent memory state
- Five obstacle ray sensors
- Food direction and distance sensing
- Nutrient-zone direction and distance sensing
- Target direction and distance sensing
- Velocity, local flow force, energy, boundary warning, and flow-alignment inputs

### Environment

- Dynamic sine/cosine flow field
- Local vortex currents
- Moving circular obstacles
- Food particles that respawn after being eaten
- Drifting nutrient zones that slowly restore energy
- Drifting target after early generations
- Difficulty ramp that increases obstacle movement speed

### Visualization

- Live `turtle` rendering
- Flow vectors
- Moving obstacles
- Food particles
- Nutrient zones
- Target circle
- Bot bodies scaled by evolved morphology
- Best live bot highlighted in blue
- Sensor rays for the best live bot
- Overlay with generation, step, alive count, fitness, archive size, and curriculum difficulty

## Project Structure

| File | Purpose |
| --- | --- |
| `main.py` | CLI entry point, visual rendering, headless runner |
| `simulation.py` | Population, environment, flow field, evolution loop, archive, save/export |
| `bot.py` | Bot physics, sensing, recurrent memory, fitness, behavior descriptor |
| `genome.py` | Neural-network weights, morphology traits, crossover, mutation, serialization |
| `config.py` | Simulation, physics, neural-network, evolution, and visualization constants |
| `tests/test_simulation.py` | Unit tests for controller wiring, archive behavior, save/load, and exports |
| `original_fluid_bot.py` | Legacy prototype kept for reference |

## Requirements

- Python 3.10 or newer recommended
- No third-party packages required

## Run

Start the visual simulation:

```bash
python main.py
```

Run a deterministic visual simulation:

```bash
python main.py --seed 1
```

Run headlessly:

```bash
python main.py --headless --generations 10 --steps 200 --seed 1
```

Save the best genome and export history:

```bash
python main.py --headless --generations 25 --steps 300 --seed 1 --save-best best_genome.json --history-csv history.csv
```

Resume from a saved genome:

```bash
python main.py --load-genome best_genome.json
```

Run a resumed headless experiment:

```bash
python main.py --headless --load-genome best_genome.json --generations 20 --steps 300 --history-csv resumed_history.csv
```

## CLI Options

| Option | Description |
| --- | --- |
| `--headless` | Runs without opening a Turtle window |
| `--generations N` | Number of generations to run |
| `--steps N` | Max simulation steps per generation |
| `--seed N` | Sets the random seed for repeatable runs |
| `--load-genome PATH` | Seeds the population from a saved best-genome JSON file |
| `--save-best PATH` | Saves the best genome at the end of the run |
| `--history-csv PATH` | Exports per-generation stats to CSV |

## Test

```bash
python -m unittest discover -s tests
```

## Tuning

Most behavior is controlled from `config.py`.

Useful constants to tune:

- `POPULATION_SIZE`
- `GENERATIONS`
- `SIMULATION_STEPS`
- `MUTATION_RATE`
- `MUTATION_AMOUNT`
- `MORPHOLOGY_TRAITS`
- `NOVELTY_WEIGHT`
- `ARCHIVE_PARENT_RATE`
- `CURRICULUM_STEP`
- `MAX_CURRICULUM_DIFFICULTY`
- `NUTRIENT_ZONE_COUNT`
- `FLOW_VORTEX_STRENGTH`

If you change `SENSOR_RAY_COUNT`, `MEMORY_SIZE`, or neural input/output constants, run the tests before launching a long experiment.

## Research-Informed Direction

The current feature set follows several active research themes:

- Quality-diversity methods such as MAP-Elites help retain useful stepping stones and reduce premature convergence.
- Morphology/controller co-evolution is fragile, so the archive preserves diverse body/controller combinations instead of only the single highest-fitness lineage.
- Recurrent controller memory gives agents a compact internal state, useful in partially observable environments.
- Active flow-control and learning-based fluid-dynamics research motivates local flow sensing, flow alignment rewards, and dynamic currents.

References:

- [Premature convergence in morphology and control co-evolution](https://journals.sagepub.com/doi/10.1177/10597123231198497)
- [Quality Diversity under Sparse Interaction and Sparse Reward](https://pubmed.ncbi.nlm.nih.gov/39823378/)
- [Controller Distillation Reduces Fragile Brain-Body Co-Adaptation and Enables Migrations in MAP-Elites](https://arxiv.org/abs/2504.06523)
- [Dynamic flow control through active matter programming language](https://www.nature.com/articles/s41563-024-02090-w)
- [Machine learning in fluid dynamics: A critical assessment](https://journals.aps.org/prfluids/accepted/10.1103/8t52-mtb9)

## Interpreting Results

Early generations often crash, starve, or drift passively. As evolution progresses, useful strategies may emerge: conserving energy, riding flow vectors, foraging before target pursuit, avoiding boundary traps, or specializing in nutrient-zone survival. The archive keeps multiple strategies available as parents, which helps the system keep improving after a simple fitness-only run would plateau.
