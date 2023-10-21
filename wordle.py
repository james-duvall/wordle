# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 20:30:23 2022

@author: duvall_jw
"""

import pandas as pd
from collections import Counter, defaultdict
from string import ascii_lowercase
from itertools import combinations
import re

w5_sol = pd.read_csv("possible_solutions.csv", names = ['series'])['series']
w5_all = pd.read_csv("allowable_guesses.csv", names = ['series'])['series']
blank_word = pd.DataFrame(data = {'count': 0}, index = list(ascii_lowercase))

class Game:
    def __init__(self):
        self.words = w5_sol.copy()
        self.count = pd.DataFrame(data = {'min': 0, 'max': 3}, index = list(ascii_lowercase))
        self.yellow = [''] * 5
        self.green = [None] * 5
        self.regex = ''
    
    def common(self, n = 26):
        c = Counter()
        for word in self.words:
            c.update(word)
        return c.most_common(n)

    def matches(self, word):
        letters = blank_word.copy()
        for letter, count in Counter(word).items():
            letters.loc[letter] = count
        return (
            (self.count['min'] <= letters['count']).all() and
            (letters['count'] <= self.count['max']).all() and
            bool(re.match(self.regex, word))
            )

    def guess(self, word, result):
        letters = defaultdict(Counter)
        for place in range(5):
            letters[word[place]].update(result[place])
            if result[place] == 'y':
                self.yellow[place] += word[place]
            elif result[place] == 'g':
                self.green[place] = word[place]
        for letter, counter in letters.items():
            if counter['x'] >= 1:
                # If a letter is marked as grey, then the number of times that letter
                # appears in the word is exactly equal to the number of times that the
                # letter is makred as yellow + green in the result.
                self.count.loc[letter, :] = counter['y'] + counter['g']
            else:
                # If a letter is not marked as grey, then the minimum number of times
                # that the letter appears in the word is the number of times that the
                # letter is marked as yellow + green in the result. No additional
                # information has been gained about the max
                self.count.loc[letter, 'min'] = counter['y'] + counter['g']
        regex = [None] * 5
        for place in range(5):
            if self.green[place] is None:
                if (self.yellow[place] == ''):
                    regex[place] = '.'
                else:
                    regex[place] = '[^' + ''.join([letter for letter in self.yellow[place]]) + ']'
            else:
                regex[place] = self.green[place]
        self.regex = '^' + ''.join(regex) + '$'
        self.words = self.words[self.words.apply(self.matches)]
        return len(self.words)
    
    def suggest(self):
        letters = ''.join((x[0] if (x[0] not in self.yellow and x[0] not in self.green) else '' for x in self.common())) + 'aeiou'
        for n in range(5, 0, -1):
            first = letters[:n]
            for last in combinations(letters[n:], 5 - n):
                g = w5_all[w5_all.str.match('^' + ''.join(['(?=.*' + letter + ')' for letter in (first + ''.join(last))]))]
                if not g.empty:
                    return g
        return ''

if __name__ == '__main__':
    g = Game()