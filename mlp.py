#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as ny


class MLP:
	""" Multilayer Perceptron.
	Code based on chapter 3 of 'Machine Learning: An Algorithmic Perspective' by Stephen Marsland.
	(http://seat.massey.ac.nz/personal/s.r.marsland/MLBook.html)
	"""


	def __init__( self, inputs, targets, hidden_nodes = 2, beta = 1, momentum = 0.9 ):
		""" Constructor.

		inputs       -- Array with training data.
		targets      -- Array with targets to the training data.
		hidden_nodes -- Number of nodes in the hidden layer.
		beta         -- Some positiv parameter in the activation function.
		momentum     -- Learning speed.
		"""

		self.inputs = ny.array( inputs )
		self.targets = ny.array( targets )

		self.nodes_in = len( inputs[0] )
		self.nodes_out = len( targets[0] )
		self.data_amount = len( inputs )

		# Add bias node
		ones = -ny.ones( ( self.data_amount, 1 ) )
		self.inputs = ny.concatenate( ( self.inputs, ones ), axis = 1 )

		self.nodes_hidden = hidden_nodes
		self.beta = beta
		self.momentum = momentum

		self._init_weights()


	def _init_weights( self ):
		""" Randomly initialize weights.
		There are to weight layers: One from the input nodes
		to the hidden nodes, and one from the hidden nodes to
		the output nodes.
		"""

		self.weights_layer1 = ny.random.rand(
			self.nodes_in + 1, self.nodes_hidden
		)
		self.weights_layer2 = ny.random.rand(
			self.nodes_hidden + 1, self.nodes_out
		)


	def early_stopping( self, valid, validtargets, eta = 0.25, iterations = 1000, outtype = "logistic" ):
		""" Early stopping. Used instead of method train().

		eta        -- Learning rate.
		iterations -- Number of iterations to do.
		"""

		# Add bias node
		valid = ny.concatenate( ( valid, -ny.ones( ( len( valid ), 1 ) ) ), axis = 1 )

		old_val_err1, old_val_err2, new_val_err = 100002, 100001, 100000
		count = 0

		while ( old_val_err1 - new_val_err > 0.001 ) or ( old_val_err2 - old_val_err1 > 0.001 ):
			count += 1
			if count % 10 == 0:
				print "[early_stopping] count: %d   error: %f" % ( count, new_val_err )
			self.train( eta, iterations, outtype )
			old_val_err2 = old_val_err1
			old_val_err1 = new_val_err
			validout = self._forward( valid )
			new_val_err = 0.5 * ny.sum( ( validtargets - validout ) ** 2 )
		print "[early_stopping] end count: " + str( count ) + " and error: " + str( new_val_err )


	def train( self, eta = 0.25, iterations = 1000, outtype = "logistic" ):
		""" Train the network. Used instead of method early_stopping().

		eta        -- Learning rate.
		iterations -- Number of iterations to do.
		outtype    -- Activation function to use: "linear", "logistic"
		"""

		self.eta = eta
		self.outtype = outtype
		shuffle = range( self.data_amount )

		# Init arrays for weight updates
		self.update_w1 = ny.zeros( ( ny.shape( self.weights_layer1 ) ) )
		self.update_w2 = ny.zeros( ( ny.shape( self.weights_layer2 ) ) )

		# Start training
		for n in range( iterations ):
			self.outputs = self._forward( self.inputs )

			# Compute error and update weights
			deltao, deltah = self._compute_errors()
			self._update_weights( deltao, deltah )

			# Randomise order of training data
			ny.random.shuffle( shuffle )
			self.inputs = self.inputs[shuffle,:]
			self.targets = self.targets[shuffle,:]


	def _forward( self, inputs ):
		""" Forward phase.

		Returns the calculated outputs.
		"""

		ones = -ny.ones( ( len( inputs ), 1 ) )

		# Activation in hidden layer
		self.hidden = ny.dot( inputs, self.weights_layer1 )
		self.hidden = 1.0 / ( 1.0 + ny.exp( -self.beta * self.hidden ) )
		self.hidden = ny.concatenate( ( self.hidden, ones ), axis = 1 )

		# Acitvation in output layer
		outputs = ny.dot( self.hidden, self.weights_layer2 )

		if self.outtype == "linear":
			pass
		elif self.outtype == "logistic":
			outputs =  1.0 / ( 1.0 + ny.exp( -self.beta * outputs ) )
		elif self.outtype == 'softmax':
			normalisers = ny.sum( ny.exp( outputs ), axis = 1 ) * ny.ones( ( 1, ny.shape( outputs )[0] ) )
			outputs = ny.transpose( ny.transpose( ny.exp( outputs ) ) / normalisers )
		else:
			print "ERROR: Unknown outtype = %s" % outtype

		return outputs


	def _compute_errors( self ):
		""" Compute the error of each layer.

		Returns the error of the output and hidden layer.
		"""

		# Error in output layer
		deltao = ( self.targets - self.outputs )

		if self.outtype == "linear":
			deltao /= self.data_amount
		elif self.outtype == "logistic":
			deltao *= self.outputs * ( 1.0 - self.outputs )
		elif self.outtype == 'softmax':
			deltao /= self.data_amount

		# Error in hidden layer
		deltah = self.hidden * ( 1.0 - self.hidden )
		deltah *= ny.dot( deltao, ny.transpose( self.weights_layer2 ) )

		return deltao, deltah


	def _update_weights( self, deltao, deltah ):
		""" Update weights of layers.

		deltao -- Error in output layer.
		deltah -- Error in hidden layer.
		"""

		inputs_tr = ny.transpose( self.inputs )
		hidden_tr = ny.transpose( self.hidden )

		self.update_w1 = self.momentum * self.update_w1
		self.update_w1 += self.eta * ny.dot( inputs_tr, deltah[:,:-1] )

		self.update_w2 = self.momentum * self.update_w2
		self.update_w2 += self.eta * ny.dot( hidden_tr, deltao )

		self.weights_layer1 += self.update_w1
		self.weights_layer2 += self.update_w2


	def use( self, inputs ):
		""" After training the network, now use it!

		inputs -- Input/test data.

		Returns the calculated output.
		"""

		inputs = ny.array( [inputs] )

		# Add bias node
		ones = -ny.ones( ( 1, 1 ) )
		inputs = ny.concatenate( ( inputs, ones ), axis = 1 )

		# Activation in hidden layer
		hidden = ny.dot( inputs, self.weights_layer1 )
		hidden = 1.0 / ( 1.0 + ny.exp( -self.beta * hidden ) )
		hidden = ny.concatenate( ( hidden, ones ), axis = 1 )

		# Acitvation in output layer
		outputs = ny.dot( hidden, self.weights_layer2 )
		outputs =  1.0 / ( 1.0 + ny.exp( -self.beta * outputs ) )

		return outputs



if __name__ == "__main__":
	# Test the neuronal networks with a simple problem: XOR.
	inputs  = [[0,0], [0,1], [1,0], [1,1]]
	targets = [[0],   [1],   [1],   [0]]

	print "Testing MLP with XOR:"
	my_mlp = MLP( inputs, targets, hidden_nodes = 2 )
	my_mlp.train( eta = 0.2, iterations = 1000, outtype = "logistic" )
	out = [
		round( my_mlp.use( [0,0] ) ), round( my_mlp.use( [0,1] ) ),
		round( my_mlp.use( [1,0] ) ), round( my_mlp.use( [1,1] ) )
	]
	target = [0,1,1,0]
	correct = 0
	for i in range( 4 ):
		if out[i] == target[i]: correct += 1
		else: print "  False: %d == %d" % ( out[i], target[i] )
	print "Correct: %d/4" % correct