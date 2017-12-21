import os
import io
import json
import random
import enchant
from textblob import TextBlob

script_dir = os.path.dirname(__file__)

# check if json files exist
def startupCheck():
    if os.path.isfile(script_dir) and os.access(script_dir, os.R_OK):
        pass
    else:
        with io.open(os.path.join(script_dir, 'frienddict.json'), 'w') as db_file:
            db_file.write(json.dumps({}))

    if os.path.isfile(script_dir) and os.access(script_dir, os.R_OK):
        pass
    else:
        with io.open(os.path.join(script_dir, 'likedict.json'), 'w') as db_file:
            db_file.write(json.dumps({}))

startupCheck()

# create a dictionary object for word lookup
d = enchant.Dict("en_US")

# instantiate dicts for use later
global friend_dict
global like_dict
friend_dict = {}
like_dict = {}

# load dicts from json files as a database

friend_file_path = os.path.join(script_dir, 'frienddict.json')
like_file_path = os.path.join(script_dir, 'likedict.json')

# writes to a json file from dict
def update_json_file(file_path, dictionary):
    with open(file_path, 'w') as outfile:
        json.dump(dictionary, outfile, \
        #pretty dumping this
        sort_keys=True, indent=4, separators=(',', ': '))

# reads json file and assigns it to a dict
def read_json_file(file_path, dictionary):
    with open(file_path, 'r') as fi:
        dictionary = json.load(fi)
        pass
    return dictionary

friend_dict = read_json_file(friend_file_path, friend_dict)
print(friend_dict)
like_dict = read_json_file(like_file_path, like_dict)

# make the distribution with the friend dict
def construct_friend_distribution(friend_dictionary):
    distribution = []
    for element in friend_dictionary:
        # the friend exists n times in the dist, where n is the weight
        for i in range(int(friend_dictionary[element])):
            distribution.append(element)
    return distribution

# Applies the likability value as a multiplier to the friends' weights
# and returns a dict for use in generating a distribution.
def apply_likability(friend_dictionary, likability_dict):
    for key in friend_dictionary:
        if key in likability_dict:
            friend_dictionary[key] = friend_dictionary[key]*likability_dict[key]
    return friend_dictionary

# Selects a friend randomly after the distribution is contructed with the weights
# and if it exists, with the likability multipliers applied.
def select_friend(friend_dictionary, likability_dict, reduction_rate):
    usable_dict = friend_dictionary
    if likability_dict:
        usable_dict = apply_likability(friend_dictionary, likability_dict)
    # construct distribution
    dist = construct_friend_distribution(usable_dict)
    # choose randomly from dist
    selection = random.choice(dist)
    weight = usable_dict[selection]
    # if selected, reduce the weight by the reduction rate,
    # and grow the weights of all others in the friend list
    for element in usable_dict:
        if element == selection:
            # weight must be larger than the reduction rate,
            # otherwise it is unaffected
            if usable_dict[element]/reduction_rate == 0:
                pass
            else:
                usable_dict[element] = usable_dict[element]/reduction_rate
        else:
            usable_dict[element] = usable_dict[element] + 1
    # update database (json file)
    update_json_file(friend_file_path, usable_dict)

    return selection, weight

# main menu display
def display_menu():
    global friend_dict
    global like_dict
    print("\nType a number to select a menu item.\n1. Enter friends\n",
    "2. Describe friends\n3. Select a friend\n4. Display friend weight values\n5. Display friend likability values\n6. Clear all data\nType any other key to quit.", sep="")
    user_input = input()
    # enter friends
    if user_input == "1":
        enter_friends(friend_dict)
        display_menu()
    # describe friends
    elif user_input == "2":
        describe_friends(friend_dict, like_dict)
        display_menu()
    # select friends with a reduction rate
    elif user_input == "3":
        if not bool(friend_dict):
            print("\nBefore selecting friends, enter friends and weights \nusing the 'Enter friends' option on the menu.\n")
            display_menu()

        #user selects a reduction rate for the growth and decay model
        print("\nEnter a reduction rate (this must be a whole number; suggested: 1-3).\nThe weights will be reduced by a factor of this number when\n a friend is selected. A higher reduction rate could indicate\nthe time duration a meeting would take or just how much you want to\nhang out with them again after this selection.")

        while True:
            rr = input()
            try:
                val = int(rr)
            except ValueError:
                print("That's not an appropriate value. Please re-enter an integer.")
                continue
            break
        selection, weight = select_friend(friend_dict, like_dict, int(rr))
        print('\n' + selection + ' selected from a list of ' + str(len(friend_dict)),
                          ' friends with weight of ' + str(weight) + '\n', sep="")
        display_menu()
    # display friend list with weights not including likability
    elif user_input == "4":
        print('\nFriend weight values\n' + json.dumps(friend_dict, indent=2, sort_keys=True))
        display_menu()
    # display friend list with likability multipliers
    elif user_input == "5":
        print('\nFriend likability values\n' + json.dumps(like_dict, indent=2, sort_keys=True))
        display_menu()
    # deletes all data from json files
    elif user_input == "6":
        user_input = input('Are you sure you want to clear all data from the database? (y/n)')
        if user_input.lower() == "y":
            friend_dict = {}
            like_dict = {}
            update_json_file(like_file_path, like_dict)
            update_json_file(friend_file_path, friend_dict)

        display_menu()
    # quit
    else:
        print("Quitting")
        pass

# allows user to enter friends with an assigned weight. This weight
# represents priority or how much the selector would like to spend time
# with the friend being entered
def enter_friends(friend_dictionary):
    print("\nEnter a friend and a weight separated by a comma.\nType quit, q, or exit to go to main menu.\n")
    while True:
        user_input = input()
        if user_input == "quit" or user_input == "q" or user_input == "exit":
            break
        friend, weight = user_input.split(",")
        friend_dictionary[friend.capitalize()] = int(weight)

    update_json_file(friend_file_path, friend_dictionary)

# allows user to make statements about friends in a strict format
# the algorithm performs a sentiment analysis on the adjectives and
# filler words but does not analyze the subject/friend.
# it will set the value of the friend as an average of the words used to
# describe them. The scale is from 0 to 2. anything below 1 is negative,
# anything above 1 is positive (on average).
def describe_friends(friend_dictionary, likability_dict):
    print("\nEnter a statement about a friend in the format:\n'[Name] is [adj] ... , [adj], and [adj]'. \nThere can be as many adjectives as one wants, or one can \ninput multiple statements about the same person to achieve the same effect.\nType quit, q, or exit to go to main menu.\n")
    while True:
        user_input = input()
        if user_input == "quit" or user_input == "q" or user_input == "exit":
            break
        sentence_arr = user_input.split()
        if sentence_arr[0] in friend_dictionary:
            subject = sentence_arr[0]
            total_sentiment = 0

            # check if its an english word. if it isnt, throw it away
            for word in sentence_arr:
                ind = sentence_arr.index(word)
                sentence_arr[ind] = word.replace(',', '')
                word = sentence_arr[ind]
                if not d.check(word):
                    sentence_arr.remove(word)

            sentence_arr = list(filter(('and').__ne__, sentence_arr))
            sentence_arr = list(filter(('is').__ne__, sentence_arr))

            if len(sentence_arr) == 0:
                print('\nYour statement is unclear. Please make sure to check spelling and try again.')
                continue

            # sentiment analysis done here
            for word in sentence_arr:
                wordblob = TextBlob(word)
                total_sentiment += wordblob.sentiment.polarity
            # adjust scale from [-1,1] to [0,2] and assign likability to
            # subject in the dict
            if subject in likability_dict:
                likability_dict[subject] = (likability_dict[subject] + (total_sentiment/len(sentence_arr) + 1))/2
            else:
                likability_dict[subject] = total_sentiment/len(sentence_arr) + 1

    update_json_file(like_file_path, likability_dict)

def simulate_distribution(friend_dictionary, likability_dict, n):
    test_arr = []
    usable_dict = friend_dictionary
    if likability_dict:
        usable_dict = apply_likability(friend_dictionary, likability_dict)
    # construct distribution
    dist = construct_friend_distribution(usable_dict)
    #clean the count for the simulation
    for element in usable_dict:
        usable_dict[element] = 0

    for i in range(n):
        selection = random.choice(dist)
        test_arr.append(selection)
        usable_dict[selection] += 1

    for element in usable_dict:
        usable_dict[element] = float(usable_dict[element])*(len(dist)/float(n))

    sim_pretty_print_dict(usable_dict)

def sim_pretty_print_dict(dictionary):
    for element in dictionary:
        print(element + ': ' + str(dictionary[element]))

display_menu()
