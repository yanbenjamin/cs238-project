
from japaneseWordle import *
from chineseWordle import * 
from koreanWordle import * 
from englishWordle import *
import argparse

NUM_GUESSES = 6
NUM_LETTERS = 5
NUM_WORDS_TO_TEST = 100

def printResults(wins, numPossibleWords, sumGuessesNeeded, guessesNeededList):
	winRate = round(wins / numPossibleWords * 100, 2)
	avgGuessesWin = round(sumGuessesNeeded / wins, 1)
	numGuessesFreqMap = getFrequencyTable(guessesNeededList)

	print(f"Win Rate: {winRate}%")
	print(f"Average Guesses for Win: {avgGuessesWin}")
	print(f"Number of Guesses Needed: {numGuessesFreqMap}")

def runEnglishWordleTests(numGuesses, numLetters, debugMode = False, startingWord = None,
						  useBaseline = True):
	game = EnglishWordleGame(numGuesses, numLetters, debugMode = False)
	validWords = getEnglishWords(ENGLISH_DICTIONARY)

	wins = 0
	total = 0
	sumGuessesNeeded = 0
	guessesNeededList = []

	indices = list(range(0, len(validWords)))
	numToTest =  min(NUM_WORDS_TO_TEST, len(validWords))
	selectedIndices = np.random.choice(indices, numToTest, replace = False)	
	wordsToTest = [validWords[selectedIndices[i]] for i in range(numToTest)]

	for secretWord in tqdm(wordsToTest):
		if startingWord == None:
			game.setStartingWord(getRandomEnglishWord(validWords))
		else:
			game.setStartingWord(startingWord)
		game.setSolution(secretWord, secretWord, secretWord)
		numGuessesNeeded = game.run(graphics = False, useBaseline = useBaseline)
		if (numGuessesNeeded != -1): 
			sumGuessesNeeded += numGuessesNeeded
			guessesNeededList.append(numGuessesNeeded)
			wins += 1
		total += 1
	
	#numPossibleWords = len(validWords)
	printResults(wins, total, sumGuessesNeeded, guessesNeededList)

def runWordleTests(WordleGame, eligibleTuples, randomWordFunction, startingWord = None,
				   useBaseline = True):
	wins = 0
	sumGuessesNeeded = 0
	guessesNeededList = []

	#game.setStartingWord("あさがお")
	tupleIndices = list(range(0, len(eligibleTuples)))
	numToTest =  min(NUM_WORDS_TO_TEST, len(eligibleTuples))
	selectedIndices = np.random.choice(tupleIndices, numToTest, replace = False)	
	tuplesToTest = [eligibleTuples[selectedIndices[i]] for i in range(numToTest)]

	total = 0
	for (kana, word, English) in tqdm(tuplesToTest):
		if startingWord == None:
			randomStartingWord, _, _ = randomWordFunction(eligibleTuples)
			WordleGame.setStartingWord(randomStartingWord) #randomKana)
		else:
			WordleGame.setStartingWord(startingWord) #randomKana)
		WordleGame.setSolution(kana, word, English)
		numGuessesNeeded = WordleGame.run(graphics = False, useBaseline = useBaseline)
		if (numGuessesNeeded != -1): 
			sumGuessesNeeded += numGuessesNeeded
			guessesNeededList.append(numGuessesNeeded)
			wins += 1
		total += 1
	
	printResults(wins, total, sumGuessesNeeded, guessesNeededList)

def get_args():
	parser = argparse.ArgumentParser(description="For parsing the Worduolingo model settings")
	parser.add_argument("-l", "--language", type=str, default="english", help="Which language for Worduolingo (out of English, Mandarin Chinese, Japanese, Korean)")
	parser.add_argument("-s", "--startWord", default= None, help="which starting word to use")
	parser.add_argument("-b", "--useBaseline", action="store_true", help="Use baseline model")

	return parser.parse_args()

if __name__ == "__main__": 
	args = get_args()
	whichLanguage = args.language.lower()
	useBaseline = args.useBaseline

	if whichLanguage == "english":
		runEnglishWordleTests(NUM_GUESSES, NUM_LETTERS, useBaseline = useBaseline)

	elif whichLanguage == "japanese": 
		game = WordleGame(NUM_GUESSES, NUM_LETTERS - 1, debugMode = False)
		wordTuples, jisho = readJapaneseFiles(JAPANESE_DIR)
		eligibleTuples = filterWords(wordTuples, NUM_LETTERS - 1)
		runWordleTests(game, eligibleTuples, getRandomJapaneseWord, useBaseline = useBaseline)
	
	elif whichLanguage == "mandarin" or whichLanguage == "chinese":
		chineseGame = ChineseWordleGame(NUM_GUESSES, NUM_LETTERS)
		wordTuples, chineseDictionary = readChineseFiles(DICTIONARY_DIR, CHINESE_FILENAME)
		eligibleTuples = filterWords(wordTuples, NUM_LETTERS)
		runWordleTests(chineseGame, eligibleTuples, getRandomChineseWord, useBaseline = useBaseline)
	elif whichLanguage == "korean":
		koreanGame = KoreanWordleGame(NUM_GUESSES, NUM_LETTERS, debugMode = True)
		koreanWordTuples, koreanDictionary = readKoreanFiles(KOREAN_DIR)
		eligibleTuples = filterWords(koreanWordTuples, NUM_LETTERS)
		jamoLetters = "".join(splitHangul("있다"))
		runWordleTests(koreanGame, eligibleTuples, getRandomKoreanWord, startingWord = None, useBaseline = useBaseline)
	
	else:
		print("Unfortunately that language doesn't have a Wordle game here just yet, check back soon!")
		print("Current Wordle games include English, Mandarin Chinese, Japanese, Korean")

