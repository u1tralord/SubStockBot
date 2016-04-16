import time
import json
import array
import math
import hashlib
from threading import Timer, Lock

'''
	This is the generic function module.
	All generic functions should be placed here.
'''

# Returns current time in seconds from epoch UTC
current_utc_time = lambda: int(round(time.time()))

# Returns current time in millis from epoch UTC
current_utc_time_millis = lambda: int(round(time.time()) * 1000)

# Runs a task at a specified interval.
#     delay = time in seconds between runs
#     action = function name to be repeated
#     *args, **kwargs = arguments and keyword arguments to be passed to the action function
#     this is an overloaded function and can take an infinite number of arguments
#     syntax = repeat_task(5, myFunc, 3, 4, myKwarg1=True, myKwarg2=10)
def repeat_task(delay, action, *args, **kwargs):
	Timer(delay, repeat_task, [delay, action] + list(args), kwargs).start()
	action(*args, **kwargs)

# Saves JSON object to provided file path
#     filename = String for filename to be saved to
#     jsonData = JSON data to be written to file
def json_to_file(filename, jsonData):
	outfile = open(filename + '.json', 'w')
	json.dump(jsonData, outfile, sort_keys = True, indent = 4,
		ensure_ascii=False)
	outfile.close()

# Mergesort function
#     alist = generic list to sorted
def mergeSort(alist):
	if len(alist)>1:
		mid = len(alist)//2
		lefthalf = alist[:mid]
		righthalf = alist[mid:]

		mergeSort(lefthalf)
		mergeSort(righthalf)

		i=0
		j=0
		k=0
		while i < len(lefthalf) and j < len(righthalf):
			if lefthalf[i] < righthalf[j]:
				alist[k]=lefthalf[i]
				i=i+1
			else:
				alist[k]=righthalf[j]
				j=j+1
			k=k+1

		while i < len(lefthalf):
			alist[k]=lefthalf[i]
			i=i+1
			k=k+1

		while j < len(righthalf):
			alist[k]=righthalf[j]
			j=j+1
			k=k+1

class BloomFilter(object):
	"""docstring for BloomFilter"""

	def __init__(self, capacity, error_rate):

		if not (0 < error_rate < 1):
			raise ValueError("Error rate must be a decimal percentage above 0.00 and less than 1.00")
		if (capacity <= 0):
			raise ValueError("Capacity must be greater than 0")

		# M = Number of bits needed to store the amount of elements
		self.m = math.ceil((-capacity * math.log(error_rate))/(math.log(2)**2))
		
		# K = Number of hash functions to use
		self.k = math.ceil((self.m/capacity)*math.log(2))

		# Create a bit array to hold whether or not the item is in the set
		self.bit_array = bitarray(self.m)

	def add(self, key):
		for seed in range(self.k):
			seededKey = "{}{}".format(seed, key)
			hashRaw = hashlib.md5(seededKey.encode('utf-8'))
			hashInt = int(hashRaw.hexdigest(), 16)
			self.bit_array[hashInt % self.m] = 1

	def lookup(self, key):
		for seed in range(self.k):
			seededKey = "{}{}".format(seed, key)
			hashRaw = hashlib.md5(seededKey.encode('utf-8'))
			hashInt = int(hashRaw.hexdigest(), 16)
			if self.bit_array[hashInt % self.m] == 0:
				return False
		return True
	
	def __contains__(self, key):
		return self.lookup(key)

class bitarray(object):
	"""docstring for bitarray"""

	def __init__(self, arrSize):
		self.byteArray = array.array('B', (0 for i in range(0, math.ceil(arrSize/8))))

	def get_size(self):
		return len(self.byteArray)*8

	def __setitem__(self, key, value):
		if value != 1 and value != 0:
			raise ValueError("Bits can only be set to a 0 or a 1")
		shiftedValue = value << key%8
		self.byteArray[key//8] |= shiftedValue

	def __getitem__(self, key):
		return 1 if self.byteArray[key//8] & 2**(key%8) != 0 else 0

	def __str__(self):
		out_str = ''
		for i in range(0, len(self.byteArray)):
			for bitNum in range(8):
				out_str += "1" if self.byteArray[i] & 2**bitNum != 0 else "0"
		return out_str