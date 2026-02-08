
import random
import math
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

    def feed_forward(self, inputs):
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
        
        return child

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
