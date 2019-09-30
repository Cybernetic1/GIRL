import random

popSize = 100
childrenSize = 40
dropRate = 0.1

def test():
	filled = 0
	escaped = 0
	for i in range(popSize):
		if random.uniform(0.0, 1.0) < dropRate:
			if filled >= childrenSize:
				print('x', end='')
			else:
				print('*', end='')
			escaped += 1
		else:
			if filled >= childrenSize:
				print('x', end='')
			else:
				print(' ', end='')
			filled += 1

test()
print()
