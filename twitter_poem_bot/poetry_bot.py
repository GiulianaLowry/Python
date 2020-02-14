# @author Giuliana Lowry
# January 2020
# Written in Python 3.8

import tweepy
import random
import re
from nltk  import *
from collections import defaultdict

# authenticates tokens for bot's twitter account
# tokens and keys removed for git hub to keep account access private
def auth_twitter():

    api_key = ""
    api_secret = ""
    access_token = ""
    secret_token = ""

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, secret_token)
    api = tweepy.API(auth)

    return api

# opens file, removes and replaces unwanted characters for tokenizing
def clean_text(file):

    source_text = file.read()

    source_text = source_text.replace("\n\n", " END ")   # indicates where in the source each verse ends
                                                         # used to determine length of random poems
    source_text = source_text.replace("\"", "")          # replace all unwanted characters
    source_text = source_text.replace("\n(", ", ")
    source_text = source_text.replace(" (", ", ")
    source_text = source_text.replace(")", ",")
    source_text = source_text.replace(",,", ",")
    source_text = source_text.replace(r"\b[A-Z]+\b", "") # remove authours names and poem titles

    return source_text

def make_tokens(cleaned_text):

    tokens = cleaned_text.split()

    return tokens

def make_trigrams(tokens):

    trigrams = ngrams(tokens, 3)

    return trigrams

# makes dictionary from trigrams made in set_trigrams()
def make_dict(trigrams, tokens):

    word_dict = dict()

    for x in trigrams:
        key = x[0]                              # gets key from first index of trigram
        if key in word_dict.keys():
            word_dict[key].append([x[1], x[2]]) # appends values to dict if key already exists in dict
        else:
            word_dict[key] = [[x[1], x[2]]]     # adds key and values to dict if key is not already in dict

    # adds second last word as key and last word as value
    # catches the last token that was missed in trigramss
    word_dict[tokens[len(tokens)-2]] = [tokens[len(tokens)-1]]

    return word_dict

def generate_poem(tokens, word_dict):

    # gets random token to start markov chains
    start = random.choice(tokens)
    # picks random next two words from starting key
    next = random.choice(word_dict[start])

    # picks a new start token while the start is "END" or next value is a string instead of an array
    while start == "END" or isinstance(next, str):
        start = random.choice(tokens)
        next = random.choice(word_dict[start])

    # sets array of peom words to first three words
    poem = [start] + next;
    char_count = sum(len(i) for i in poem)

    # adds to array of peom words using markov chain until
    # the next value contains "END" and meets minimum length
    while "END" not in next and char_count < 250:
        start = next[len(next)-1]
        next = random.choice(word_dict[start])
        poem += next
        char_count += sum(len(i) for i in next)

    # converts array to string of words to poem can be tweeted
    poem_str = poem[0]
    for x in range (1, len(poem)-1):
        if x != "END":
            poem_str += " " + poem[x]
        if x == "END":
            break

    return poem_str

def format_poem(poem):

    punct = ['!', '.', '?', ',', ';', ':']
    end_punct = ['!', '.', '?']

    # replaces punctuation with new line so
    # poem is on multiple lines
    for y in punct:
        replace = y + "\n"
        poem = poem.replace(y, replace)
        poem = poem.replace("\n ", "\n")

    poem_lines = poem.split("\n")

    # capitalizes first Letter of each line, makes the rest lower case
    final_poem = ""
    for z in poem_lines:
        z = z.capitalize()
        final_poem += z + "\n"

    # cleans string of double line and "END"
    final_poem = final_poem.replace("End\n", "")
    final_poem = final_poem.replace("\n\n", "")

    return final_poem

# checks if poem is too long
def too_long(poem_str, max_len):

    num_chars = len(poem_str)

    if num_chars > max_len:
        return True

    return False

# removes last line of poem
def shorten_poem(f_poem):

    x = len(f_poem)-2
    while f_poem[x] != "\n" and x > 0:
        x = x - 1
    x = x - 1

    return f_poem[0:x]

# tweets poem
def tweet_poem(api, tweet):

    api.update_status(tweet)
    #print(tweet + "\n")

def main():

    file_name = "poem_file.txt"
    file = open(file_name, encoding='utf-8')

    tw_api = auth_twitter()
    text = clean_text(file)
    tokens = make_tokens(text)
    ngrams = make_trigrams(tokens)
    p_dict = make_dict(ngrams, tokens)
    p_string = generate_poem(tokens, p_dict)
    f_poem = format_poem(p_string)

    while too_long(f_poem, 200) == True:    # removes last line until short enough to tweet
        f_poem = shorten_poem(f_poem)

    f_poem = f_poem + "\n#poetry #bot"

    tweet_poem(tw_api, f_poem)

    file.close()

if __name__ == '__main__':
    main()
