
from japaneseWordle import *

NUM_GUESSES = 6
NUM_LETTERS = 5

def runJapaneseWordleTests(): # eventually, make this general for languages 

	game = WordleGame(NUM_GUESSES, NUM_LETTERS, debugMode = False)
	wordTuples, jisho = readJapaneseFiles(JAPANESE_DIR)
	eligibleTuples = filterWords(wordTuples, NUM_LETTERS)

	wins = 0
	sumGuessesNeeded = 0
	guessesNeededList = []

	#game.setStartingWord("あさがお")
	for (kana, word, English) in tqdm(eligibleTuples):
		randomKana, _, _ = getRandomJapaneseWord(eligibleTuples)
		game.setStartingWord(randomKana)
		game.setSolution(kana, word, English)
		numGuessesNeeded = game.run(graphics = False)
		if (numGuessesNeeded != -1): 
			sumGuessesNeeded += numGuessesNeeded
			guessesNeededList.append(numGuessesNeeded)
			wins += 1
	
	numPossibleWords = len(eligibleTuples)
	winRate = round(wins / numPossibleWords * 100, 2)
	avgGuessesWin = round(sumGuessesNeeded / wins, 1)
	numGuessesFreqMap = getFrequencyTable(guessesNeededList)

	print(f"Win Rate: {winRate}%")
	print(f"Average Guesses for Win: {avgGuessesWin}")
	print(f"Number of Guesses Needed: {numGuessesFreqMap}")

if __name__ == "__main__": 
	runJapaneseWordleTests()