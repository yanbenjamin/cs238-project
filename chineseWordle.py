from japaneseWordle import *

ENGLISH_DICTIONARY = "dictionaries/wordle-nyt-answers-alphabetical.txt"
NUM_LETTERS = 5 # in pinyin letters
NUM_GUESSES = 6

def getEnglishWords(filename):
	with open(filename, "r") as file: 
		words = []
		for f in file:
			words.append(f.strip())
		return [word.upper() for word in words if len(word) == NUM_LETTERS]

def getRandomEnglishWord(words):
	return np.random.choice(words)			
