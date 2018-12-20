import sys
import random


NUM_OF_FRAMES=0
PAGE_REFERENCE_STR=''


base_code = \
"""
def %s():
	ptr = 0
	mem_layout = [None] * NUM_OF_FRAMES
	mem_status = [None] * NUM_OF_FRAMES
	
	faults = 0
	refs = PAGE_REFERENCE_STR.split(',')
	for i in refs:
%s
	return faults
"""


lfu = \
"""
if i not in mem_layout:
	faults += 1	
	if None in mem_status:
		idx = ptr
	else:
		flt = [i for i in mem_status if i[0] == min(mem_status, key=lambda x: x[0])[0]]
		idx = mem_status.index(min(flt, key=lambda x: x[1]))
	mem_layout[idx] = i
	mem_status[idx] = [0, ptr]
else:
	mem_status[mem_layout.index(i)][0] += 1
ptr += 1
"""


enh_sncd_chance = \
"""
if i not in mem_layout:
	faults += 1
	if not None in mem_status:
		finished = False
		for j in range(2):
			for k in range(NUM_OF_FRAMES):
				if mem_status[ptr] == [0, 0]:
					finished = True
					break
				ptr = (ptr+1)%NUM_OF_FRAMES
			if finished:
				break
			for k in range(NUM_OF_FRAMES):
				if mem_status[ptr] == [0, 1]:
					finished = True
					break
				else:
					mem_status[ptr][0] = 0
				ptr = (ptr+1)%NUM_OF_FRAMES
			if finished:
				break
	mem_layout[ptr] = i
	mem_status[ptr] = [0, 0]
	ptr = (ptr+1)%NUM_OF_FRAMES
else:
	idx = mem_layout.index(i)
	mem_status[idx] = [1, random.randint(mem_status[idx][1],1)]
"""


scnd_chance = \
"""
if i not in mem_layout:
	faults += 1
	if not None in mem_status:
		while True:
			if mem_status[ptr] == 0:
				break
			else:
				mem_status[ptr] = 0
			ptr = (ptr+1)%NUM_OF_FRAMES
	mem_layout[ptr] = i
	mem_status[ptr] = 0
	ptr = (ptr+1)%NUM_OF_FRAMES
else:
	mem_status[mem_layout.index(i)] = 1
"""


opt = \
"""
if i not in mem_layout:
	faults += 1
	idx = mem_status.index(max(mem_status)) if None not in mem_status else ptr
	mem_layout[idx] = i
mem_status[mem_layout.index(i)] = \
	refs.index(i, ptr+1) if i in refs[ptr+1:] else len(refs)
ptr += 1
"""


lru = \
"""
if i not in mem_layout:
	faults += 1
	idx = mem_status.index(min(mem_status)) if None not in mem_status else ptr
	mem_layout[idx] = i 
mem_status[mem_layout.index(i)] = ptr
ptr += 1
"""


fifo = \
"""
if i not in mem_layout:
	faults += 1
	mem_layout[ptr] = i
	ptr = (ptr+1)%NUM_OF_FRAMES
"""


algorithms = \
{
	'try_FIFO': fifo,
	'try_LRU': lru,
	'try_enhanced_second_chance': enh_sncd_chance,
	'try_second_chance': scnd_chance,
	'try_LFU': lfu,
	'try_optimal': opt
}


def init():
	global NUM_OF_FRAMES, PAGE_REFERENCE_STR
	
	print("Enter number of frames available in memory: ")
	NUM_OF_FRAMES = int(input())
	if not NUM_OF_FRAMES in range(1,21):
		print("Number of frames needs to reside between 1 and 20.")
		sys.exit(1)

	print("Enter length of reference string: ")
	for i in range(int(input())):
		PAGE_REFERENCE_STR += str(random.randint(0,99))+','
	PAGE_REFERENCE_STR = PAGE_REFERENCE_STR[0:-1]
	
	code = ''
	for i in algorithms:
		code += base_code % (i, '\t\t'.join(algorithms[i].splitlines(True)))
	return code


def main():
	exec(init())
	print("Page reference string: " + PAGE_REFERENCE_STR)

	msg = 'Number of faults when using %s replacement algorithm: %s'
	for i in algorithms:
		print(msg % (' '.join(i.split('_')[1:]), locals()[i]()))


main()
