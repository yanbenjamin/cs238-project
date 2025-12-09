from japaneseWordle import *

ENGLISH_DICTIONARY = "dictionaries/wordle-nyt-answers-alphabetical.txt"
NUM_LETTERS = 5
NUM_GUESSES = 6

def getEnglishWords(filename):
	with open(filename, "r") as file: 
		words = []
		for f in file:
			words.append(f.strip())
		return [word.upper() for word in words if len(word) == NUM_LETTERS]

def getRandomEnglishWord(words):
	return np.random.choice(words)			

class EnglishWordleSolver(WordleSolver):
	def __init__(self, numGuesses, numLetters, secretKana, secretWord, eligibleWords, 
			  startingGuess = None, useBaseline = True):
		self.numLetters = numLetters 
		self.numGuesses = numGuesses 
		self.guesses = [""]
		self.startingGuess = startingGuess

		self.secretKana = secretKana
		self.secretWord = secretWord
	
		self.eligibleKana = eligibleWords 
		self.useBaseline = useBaseline

class EnglishWordleGame(WordleGame):
	def __init__(self, numGuesses, numLetters, debugMode = False):
		self.validGuesses = getEnglishWords(ENGLISH_DICTIONARY)
		self.secretWord = getRandomEnglishWord(self.validGuesses)
		self.language = "English"

		self.numGuesses, self.numLetters = numGuesses, numLetters
		self.guesses = []
		self.startingGuess = None

		if debugMode:
			print(f"Secret {numLetters} English word selected from {len(self.validGuesses)} eligible words")
			print(f"Secret Word: {self.secretWord}")
	
	def run(self, graphics = True, useBaseline = True):
		self.initializeGame()
		self.solver = EnglishWordleSolver(self.numGuesses, self.numLetters, self.secretKana, 
				self.secretWord, self.validGuesses, startingGuess = self.startingGuess, useBaseline = useBaseline)
		numGuessesNeeded = self.solver.solve(graphics)
		if graphics: self.runGraphics()
		return numGuessesNeeded

def solveEnglishWord(secretWord, startingWord = "SLATE"):  # means tomorrow in Korean
	validWords = getEnglishWords(ENGLISH_DICTIONARY)
	game = EnglishWordleGame(NUM_GUESSES, NUM_LETTERS, debugMode = True)

	game.setStartingWord(startingWord)

	if secretWord != None:
		game.setSolution(secretWord, secretWord, secretWord) # English -> English translation lol

	numGuessesNeeded = game.run(graphics = True)
	if (numGuessesNeeded != -1):
		print(f"Solved with {numGuessesNeeded}　guess attempts!")
	else:
		print("Did not solve unfortunately :(")


if __name__ == "__main__":
	eligibleEnglishWords = getEnglishWords(ENGLISH_DICTIONARY)
	if (len(sys.argv) > 1):
		solveEnglishWord(sys.argv[1].upper(), startingWord = "SLATE")
	else: 
		randomWord = np.random.choice(eligibleEnglishWords)
		print(randomWord)
		solveEnglishWord(randomWord, startingWord = "SLATE")
	
	 