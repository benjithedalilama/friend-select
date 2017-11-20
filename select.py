import random
import os
import json

friend_dict = {}
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'dict.json')
with open(file_path, 'r') as fi:
    friend_dict = json.load(fi)
    pass

def construct_friend_distribution(friend_dictionary):
    distribution = []
    for element in friend_dictionary:
        for i in xrange(friend_dictionary[element]):
            distribution.append(element)
    return distribution

def select_friend(friend_dictionary, reduction_rate):
    dist = construct_friend_distribution(friend_dictionary)
    selection = random.choice(dist)
    weight = friend_dictionary[selection]
    for element in friend_dictionary:
        if element == selection:
            #dont reduce if it reduces to 0. When something is greater than the
            #reduction rate it can be reduced, otherwise nah
            if friend_dictionary[element]/reduction_rate == 0:
                pass
            else:
                friend_dictionary[element] = friend_dictionary[element]/reduction_rate
        else:
            friend_dictionary[element] = friend_dictionary[element] + 1

    with open(file_path, 'w') as outfile:
        json.dump(friend_dictionary, outfile, \
        #pretty dumping this
        sort_keys=True, indent=4, separators=(',', ': '))

    return selection, weight

def simulate_distribution(friend_dictionary, n):
    test_arr = []
    dist = construct_friend_distribution(friend_dictionary)
    #clean the count for the simulation
    for element in friend_dictionary:
        friend_dictionary[element] = 0

    for i in xrange(n):
        selection = random.choice(dist)
        test_arr.append(selection)
        friend_dictionary[selection] += 1

    for element in friend_dictionary:
        friend_dictionary[element] = float(friend_dictionary[element])*(len(dist)/float(n))

    sim_pretty_print_dict(friend_dictionary)

def sim_pretty_print_dict(dictionary):
    for element in dictionary:
        print(element + ': ' + str(dictionary[element]))

#rate of reduction of weights for chosen friends
rr = 3
selection, weight = select_friend(friend_dict, rr)
print(selection + ' selected from a list of ' + str(len(friend_dict)) + \
                  ' friends with weight of ' + str(weight) + '\n')

n = 10000
simulate_distribution(friend_dict, n)
