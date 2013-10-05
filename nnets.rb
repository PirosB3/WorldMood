require 'ruby_debug'

PROBLEM_SIZE = -0.5..0.5

def propagate_was_change(neurons)
	i = rand(neurons.size)
	activation = 0
	neurons.each_with_index do |other, j|
		if i != j
			activation += other[:weights][i] * other[:output]
		end
	end
	output = activation >= 0 ? 1 : -1
	neurons[i][:output] = output
end

def get_output(neurons, pattern, evals=100)
	vector = pattern.flatten
	neurons.each_with_index do |neuron, i|
		neuron[:output] = vector[i]
	end
	evals.times do
		propagate_was_change(neurons)
	end
	neurons.map do |neuron|
		neuron[:output]
	end
end

def perturb_vector(vector, num_errors=1)
	perturbed = Array.new(vector)
	indices = []
	while indices.length < num_errors do
		index = rand(perturbed.length)
		unless indices.include? index
			indices << index
		end
	end
	indices.each do |i|
		perturbed[i] *= -1
	end
	perturbed
end

def to_binary(vector)
	return Array.new(vector.size){|i| ((vector[i]==-1) ? 0 : 1)}
end

def print_patterns(provided, expected, actual)
	p, e, a = to_binary(provided), to_binary(expected), to_binary(actual)
	p1, p2, p3 = p[0..2].join(', '), p[3..5].join(', '), p[6..8].join(', ')
	e1, e2, e3 = e[0..2].join(', '), e[3..5].join(', '), e[6..8].join(', ')
	a1, a2, a3 = a[0..2].join(', '), a[3..5].join(', '), a[6..8].join(', ')
	puts "Provided   Expected     Got"
	puts "#{p1}     #{e1}      #{a1}"
	puts "#{p2}     #{e2}      #{a2}"
	puts "#{p3}     #{e3}      #{a3}"
end

def calculate_error(expected, actual)
	sum = 0
	expected.each_with_index do |v, i|
		if expected[i] != actual[i]
			sum += 1
		end
	end
	sum
end

def test(neurons, patterns)
	error = 0.0
	patterns.each do |pattern|
		vector = pattern.flatten
		perturbed = perturb_vector(vector)
		output = get_output(neurons, perturbed)
		error += calculate_error(vector, output)
		print_patterns(perturbed, vector, output)
	end

	error = error / patterns.size.to_f
	puts "Final Result: avg pattern error=#{error}"
	return error
end

def train(neurons, patterns)
	num_neurons = neurons.length
	neurons.each_with_index do |neuron, i|
		(i+1...num_neurons).each do |j|
			wij = 0.0
			patterns.each do |pattern|
				vector = pattern.flatten
				wij += vector[i] * vector[j]
			end
			neurons[i][:weights][j] = wij
			neurons[j][:weights][i] = wij
		end
	end
end

def create_neuron(num_inputs)
	weights = (0...num_inputs).map do
		rand(PROBLEM_SIZE)
	end
	{ :weights => weights }
end

def execute(patterns, num_inputs)
	# for a 3x3 pattern, we need the same number of neurons
	neurons = (0...num_inputs).map do
		create_neuron(num_inputs)
	end
	train(neurons, patterns)
	test(neurons, patterns)
end

num_inputs = 9
p1 = [[1,1,1], [-1, 1,-1], [-1,1,-1]]
p2 = [[1,-1,1],[1,-1,1],[1,1,1]]
patterns = [p1, p2]
execute(patterns, num_inputs)
