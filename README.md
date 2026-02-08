# fluid-dynamics-bot-evolution
This repository contains an implementation of a fluid dynamics bot that uses neural networks and a genetic algorithm to evolve its shape and navigate through obstacles. The bot's shape is dynamically adjusted based on simulated fluid forces, and a neural network determines its movement. The genetic algorithm drives the evolution of the bot's shape by selecting the fittest individuals from each generation. The simulation runs for multiple generations, continuously improving the bot's ability to navigate obstacles. The code is written in Python and utilizes the turtle graphics library for visualization.



By observing the results, we can see the following:

The initial generations start with random shapes, and the fitness of the bots' shapes varies.
As the generations progress, we notice some shapes that consistently perform better and are selected as the fittest individuals.
The fittest bot's shape tends to undergo modifications to improve its ability to navigate obstacles.
The shapes become more refined and optimized over time, with some generations producing shapes that perform significantly better than previous ones.
In some cases, the fittest bot's shape may reach a plateau, where further generations do not lead to significant improvements.

Overall, the results demonstrate the effectiveness of the genetic algorithm and neural networks in evolving and adapting the bot's shape to successfully navigate through obstacles in the fluid dynamics simulation.


Key Innovations
1. True Evolution Engine
Selection: Tournament selection picks the fittest parents.
Crossover & Mutation: Traits are properly passed down and modified.
Elitism: The top 2 bots are cloned to the next generation.
2. Complex Fluid Dynamics (Phase 2 Upgrade)
Chaotic Flow Field: The water is no longer a simple stream. It's a complex vector field with swirling currents and eddies (visualized by light blue arrows).
Drag: Bots experience drag proportional to velocity squared.
3. Metabolic Energy System (Phase 2 Upgrade)
Energy: Bots start with 100 energy.
Consumption: Moving costs energy. Surviving costs energy.
Food: Green particles are scattered in the arena. Eating one gives +50 Energy.
Death: Running out of energy kills the bot instantly.
4. Advanced Sensory System
Sight: Bots cast 3 rays (-45°, 0°, +45°) to detect obstacles.
Smell/Sense: Bots know the vector to the nearest food source.
Internal State: Bots know their current energy level and velocity.
Visualization: The fittest bot draws its sight lines (grey) and changes color based on energy (Green=Full, Red=Empty).
5. Dynamic Environment
Moving Obstacles: Red circles bounce around the arena.
Target: A purple circle is the ultimate goal.
How to Run
Run the simulation from the terminal:

bash
python scratch/fluid_sim/main.py
Strategy Guide
Watch as the bots evolve:

Early Gens: Chaotic crashing and starving.
Mid Gens: learning to eat food to survive longer.
Late Gens: Efficient swimmers that grab food on their way to the target.
