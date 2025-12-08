
from japaneseWordle import *

KOREAN_DIR = "./dictionaries"
NUM_LETTERS = 5
NUM_GUESSES = 6

koreanWordTuples, koreanDictionary = readKoreanFiles(KOREAN_DIR)

class KoreanWordleSolverBaseline(WordleSolverBaseline):
	def __init__(self, numGuesses, numLetters, secretKana, secretWord, eligibleTuples, startingGuess = None):
		self.numLetters = numLetters 
		self.numGuesses = numGuesses 
		self.guesses = [""]
		self.startingGuess = startingGuess

		self.secretKana = secretKana
		self.secretWord = secretWord
	
		self.eligibleKana = [tup[0] for tup in eligibleTuples]
		self.eligibleKana = list(set(self.eligibleKana))
		#print(self.eligibleKana)

class KoreanWordleGame(WordleGame):
	def __init__(self, numGuesses, numLetters, debugMode = False):
		koreanWordTuples, self.koreanDictionary = readKoreanFiles(JAPANESE_DIR)
		self.eligibleTuples = filterWords(koreanWordTuples, numLetters)
		self.secretKana, self.secretWord, self.secretDefinition = getRandomKoreanWord(self.eligibleTuples)
		self.language = "Korean"

		self.numGuesses, self.numLetters = numGuesses, numLetters
		self.guesses = []
		self.startingGuess = None

		if debugMode:
			print(f"Secret {numLetters} Jamo Letter Korean word selected from {len(self.eligibleTuples)} eligible words")
			print(f"Secret Jamo Letters: {self.secretKana}, Word: {self.secretWord}, Definition: {self.secretDefinition}")
			
	def run(self, graphics = True):
		self.initializeGame()
		self.solver = KoreanWordleSolverBaseline(self.numGuesses, self.numLetters, self.secretKana, 
				self.secretWord, self.eligibleTuples, startingGuess = self.startingGuess)
		numGuessesNeeded = self.solver.solve(graphics)
		if graphics: self.runGraphics()
		return numGuessesNeeded

def solveKoreanWord(secretHangul, startingWord = "내일"):  # means tomorrow in Korean

	game = KoreanWordleGame(NUM_GUESSES, NUM_LETTERS, debugMode = True)
	koreanWordTuples, koreanDictionary = readKoreanFiles(KOREAN_DIR)
	eligibleTuples = filterWords(koreanWordTuples, NUM_LETTERS)

	startingJamoLetters = "".join(splitHangul(startingWord))
	game.setStartingWord(startingJamoLetters)

	if secretHangul != None:
		secretLetters = "".join(splitHangul(secretHangul))
		game.setSolution(secretLetters, secretHangul, koreanDictionary[secretHangul])

	numGuessesNeeded = game.run(graphics = True)
	if (numGuessesNeeded != -1):
		print(f"Solved with {numGuessesNeeded}　guess attempts!")
	else:
		print("Did not solve unfortunately :(")

if __name__ == "__main__":
	solveKoreanWord("감사")