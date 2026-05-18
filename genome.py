
import math
import random

import config


class Genome:
    def __init__(self):
        # Weights for Input -> Hidden layer
        self.w_ih = [[random.uniform(-1, 1) for _ in range(config.HIDDEN_SIZE)] for _ in range(config.INPUT_SIZE)]
        # Weights for Hidden -> Output layer
        self.w_ho = [[random.uniform(-1, 1) for _ in range(config.OUTPUT_SIZE)] for _ in range(config.HIDDEN_SIZE)]
        
        # Biases
        self.b_h = [random.uniform(-1, 1) for _ in range(config.HIDDEN_SIZE)]
        self.b_o = [random.uniform(-1, 1) for _ in range(config.OUTPUT_SIZE)]
        self.traits = {
            name: random.uniform(bounds[0], bounds[1])
            for name, bounds in config.MORPHOLOGY_TRAITS.items()
        }

    def feed_forward(self, inputs):
        if len(inputs) != config.INPUT_SIZE:
            raise ValueError(f"Expected {config.INPUT_SIZE} inputs, got {len(inputs)}")

        # Input -> Hidden
        hidden = []
        for j in range(config.HIDDEN_SIZE):
            s = 0
            for i in range(config.INPUT_SIZE):
                s += inputs[i] * self.w_ih[i][j]
            s += self.b_h[j]
            hidden.append(math.tanh(s))
        
        # Hidden -> Output
        outputs = []
        for k in range(config.OUTPUT_SIZE):
            s = 0
            for j in range(config.HIDDEN_SIZE):
                s += hidden[j] * self.w_ho[j][k]
            s += self.b_o[k]
            outputs.append(math.tanh(s))

        return outputs

    def clone(self):
        child = Genome()
        child.w_ih = [row[:] for row in self.w_ih]
        child.w_ho = [row[:] for row in self.w_ho]
        child.b_h = self.b_h[:]
        child.b_o = self.b_o[:]
        child.traits = self.traits.copy()
        return child

    def crossover(self, partner):
        child = Genome()
        # Randomly mix weights from self and partner
        for i in range(config.INPUT_SIZE):
            for j in range(config.HIDDEN_SIZE):
                child.w_ih[i][j] = self.w_ih[i][j] if random.random() > 0.5 else partner.w_ih[i][j]
        
        for j in range(config.HIDDEN_SIZE):
            for k in range(config.OUTPUT_SIZE):
                child.w_ho[j][k] = self.w_ho[j][k] if random.random() > 0.5 else partner.w_ho[j][k]
        
        # Mix biases
        child.b_h = [self.b_h[i] if random.random() > 0.5 else partner.b_h[i] for i in range(config.HIDDEN_SIZE)]
        child.b_o = [self.b_o[i] if random.random() > 0.5 else partner.b_o[i] for i in range(config.OUTPUT_SIZE)]
        child.traits = {}
        for name, bounds in config.MORPHOLOGY_TRAITS.items():
            a = self.traits.get(name, random.uniform(bounds[0], bounds[1]))
            b = partner.traits.get(name, random.uniform(bounds[0], bounds[1]))
            if random.random() < 0.35:
                value = (a + b) * 0.5
            else:
                value = a if random.random() > 0.5 else b
            child.traits[name] = self._clamp_trait(name, value)

        return child

    def to_dict(self):
        return {
            "input_size": config.INPUT_SIZE,
            "hidden_size": config.HIDDEN_SIZE,
            "output_size": config.OUTPUT_SIZE,
            "w_ih": self.w_ih,
            "w_ho": self.w_ho,
            "b_h": self.b_h,
            "b_o": self.b_o,
            "traits": self.traits,
        }

    @classmethod
    def from_dict(cls, data):
        expected = (config.INPUT_SIZE, config.HIDDEN_SIZE, config.OUTPUT_SIZE)
        actual = (
            data.get("input_size"),
            data.get("hidden_size"),
            data.get("output_size"),
        )
        if actual != expected:
            raise ValueError(
                "Saved genome dimensions do not match current config: "
                f"expected {expected}, got {actual}"
            )

        genome = cls()
        genome.w_ih = [row[:] for row in data["w_ih"]]
        genome.w_ho = [row[:] for row in data["w_ho"]]
        genome.b_h = data["b_h"][:]
        genome.b_o = data["b_o"][:]
        genome.traits = {
            name: genome._clamp_trait(name, data["traits"].get(name, genome.traits[name]))
            for name in config.MORPHOLOGY_TRAITS
        }
        return genome

    def mutate(self):
        # Mutate Input->Hidden weights
        for i in range(config.INPUT_SIZE):
            for j in range(config.HIDDEN_SIZE):
                if random.random() < config.MUTATION_RATE:
                    self.w_ih[i][j] += random.gauss(0, config.MUTATION_AMOUNT)
        
        # Mutate Hidden->Output weights
        for j in range(config.HIDDEN_SIZE):
            for k in range(config.OUTPUT_SIZE):
                if random.random() < config.MUTATION_RATE:
                    self.w_ho[j][k] += random.gauss(0, config.MUTATION_AMOUNT)

        # Mutate Biases
        for i in range(config.HIDDEN_SIZE):
             if random.random() < config.MUTATION_RATE:
                 self.b_h[i] += random.gauss(0, config.MUTATION_AMOUNT)
        for i in range(config.OUTPUT_SIZE):
             if random.random() < config.MUTATION_RATE:
                 self.b_o[i] += random.gauss(0, config.MUTATION_AMOUNT)

        for name, bounds in config.MORPHOLOGY_TRAITS.items():
            if random.random() < config.TRAIT_MUTATION_RATE:
                span = bounds[1] - bounds[0]
                self.traits[name] = self._clamp_trait(
                    name,
                    self.traits[name] + random.gauss(0, span * config.TRAIT_MUTATION_AMOUNT)
                )

    def _clamp_trait(self, name, value):
        low, high = config.MORPHOLOGY_TRAITS[name]
        return max(low, min(high, value))
