import math
import random

N_BIAS = 1

def sigmoid(x):
    return math.tanh(x)

def dsigmoid(y):
    return 1.0 - y**2

class NeuralNetwork(object):

    def buildWeights(self, n1, n2, fill=None):
        res = []
        for x in range(n1):
            inner = []
            for z in range(n2):
                inner.append(fill or random.uniform(-0.2, 0.2))
            res.append(inner)
        return res

    def __init__(self, n_input, n_hidden, n_output):

        # Define nums
        self.n_input = n_input + N_BIAS
        self.n_output = n_output  
        self.n_hidden = n_hidden

        # Build outputs
        self.out_input = [1.0]*self.n_input
        self.out_hidden = [1.0]*self.n_hidden
        self.out_output = [1.0]*self.n_output

        # Build weights
        self.w_input_hidden = self.buildWeights(self.n_input, self.n_hidden)
        self.w_hidden_output = self.buildWeights(self.n_hidden, self.n_output)

        # Track changes
        self.change_input_hidden = self.buildWeights(self.n_input, self.n_hidden, 0.0)
        self.change_hidden_output = self.buildWeights(self.n_hidden, self.n_output, 0.0)

    def back_propagate(self, targets, N, M):

        output_deltas = [0] * self.n_output
        hidden_deltas = [0] * self.n_hidden

        # Calculate output delats
        for o in range(self.n_output):
            error = targets[o] - self.out_output[o]
            output_deltas[o] = dsigmoid(self.out_output[o]) * error

        # Calculate hidden delats
        for h in range(self.n_hidden):
            error = 0.0
            for o in range(self.n_output):
                error += output_deltas[o] * self.w_hidden_output[h][o]
            hidden_deltas[h] = dsigmoid(self.out_hidden[h]) * error

        # Update hidden_output weights
        for h in range(self.n_hidden):
            for o in range(self.n_output):
                change = output_deltas[o] * self.out_hidden[h]
                self.w_hidden_output[h][o] += N*change \
                        + M*self.change_hidden_output[h][o]
                self.change_hidden_output[h][o] = change

        # Update input_hidden weights
        for i in range(self.n_input):
            for h in range(self.n_hidden):
                change = hidden_deltas[h] * self.out_input[i]
                self.w_input_hidden[i][h] += N*change + M*self.change_input_hidden[i][h]
                self.change_input_hidden[i][h] = change

        # Calculate error
        error = 0.0
        for k in range(len(targets)):
            error = error + 0.5*(targets[k]-self.out_output[k])**2
        return error

    def update(self, inputs):
        for i in range(self.n_input - N_BIAS):
            self.out_input[i] = inputs[i]

        for h in range(self.n_hidden):
            res = [self.w_input_hidden[i][h] * self.out_input[i] for i in range(self.n_input)]
            self.out_hidden[h] = sigmoid(sum(res))

        for o in range(self.n_output):
            res = [self.w_hidden_output[h][o] * self.out_hidden[h] for h in range(self.n_hidden)]
            self.out_output[o] = sigmoid(sum(res))

        return self.out_output

    def train(self, patterns, iterations=100000, N=0.5, M=0.5):
        for _ in xrange(iterations):
            error = 0.0
            for inp, expected in patterns:
                self.update(inp)
                error += self.back_propagate(expected, N, M)

            if _ % 100 == 0:
                print('error %-.5f' % error)

    def test(self, patterns):
        for pattern, expected in patterns:
            print "%s -> %s" % (pattern, self.update(pattern))

def main():
    pattern = [
        [[0,0], [0]],
        [[0,1], [1]],
        [[1,0], [1]],
        [[1,1], [1]]
    ]
    #pattern = [
        #[[0,0], [0]],
        #[[0,1], [1]],
        #[[1,0], [1]],
        #[[1,1], [0]]
    #]
    n = NeuralNetwork(2, 4, 1)
    n.train(pattern)
    n.test(pattern)

if __name__ == '__main__':
    main()
