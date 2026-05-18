import os
import tempfile
import unittest

import config
from bot import Bot
from genome import Genome
from main import run_headless
from simulation import Simulation


class SimulationTests(unittest.TestCase):
    def test_bot_controller_input_matches_config(self):
        sim = Simulation(seed=7)
        bot = Bot(pos_x=-300, pos_y=0, genome=Genome())

        bot.update(
            sim.get_flow_force(bot.pos[0], bot.pos[1]),
            sim.obstacles,
            sim.foods,
            sim.nutrient_zones,
            sim.target_pos,
        )

        self.assertEqual(len(bot.sensor_readings), config.SENSOR_RAY_COUNT)
        self.assertEqual(len(bot.memory), config.MEMORY_SIZE)
        self.assertLessEqual(bot.energy, config.STARTING_ENERGY)

    def test_headless_run_builds_quality_diversity_archive(self):
        sim = run_headless(generations=2, steps=15, seed=11)

        self.assertEqual(sim.generation, 2)
        self.assertEqual(len(sim.population), config.POPULATION_SIZE)
        self.assertGreater(len(sim.archive), 0)
        self.assertIn("best_fitness", sim.last_stats)
        self.assertEqual(len(next(iter(sim.archive))), 4)

    def test_genome_clone_preserves_and_isolates_morphology(self):
        genome = Genome()
        clone = genome.clone()

        self.assertEqual(genome.traits, clone.traits)
        first_trait = next(iter(config.MORPHOLOGY_TRAITS))
        clone.traits[first_trait] += 1.0
        self.assertNotEqual(genome.traits[first_trait], clone.traits[first_trait])

    def test_feed_forward_rejects_wrong_input_size(self):
        genome = Genome()

        with self.assertRaises(ValueError):
            genome.feed_forward([0.0] * (config.INPUT_SIZE - 1))

    def test_genome_save_load_and_history_export(self):
        sim = run_headless(generations=1, steps=5, seed=13)

        with tempfile.TemporaryDirectory() as tmp_dir:
            genome_path = os.path.join(tmp_dir, "best.json")
            history_path = os.path.join(tmp_dir, "history.csv")

            sim.save_best_genome(genome_path)
            sim.export_history_csv(history_path)
            loaded = Simulation.load_genome(genome_path)

            self.assertEqual(loaded.to_dict()["input_size"], config.INPUT_SIZE)
            self.assertTrue(os.path.exists(history_path))
            self.assertGreater(os.path.getsize(history_path), 0)


if __name__ == "__main__":
    unittest.main()
