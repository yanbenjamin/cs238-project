from japaneseWordle import *

import pprint

DICTIONARY_DIR = "dictionaries"
CHINESE_FILENAME = "chinese-words.csv"
NUM_LETTERS = 5 # in pinyin letters
NUM_GUESSES = 6

def getRandomChineseWord(eligibleTuples):
	index = np.random.randint(0, len(eligibleTuples))
	return eligibleTuples[index]

def findMatchingPinyin(targetPinyin, eligibleTuples):
	for (pinyin, hanzi, english) in eligibleTuples:
		if (pinyin == targetPinyin):
			return hanzi 
	return -1 

def findMatchingHanzi(targetHanzi, eligibleTuples):
	for (pinyin, hanzi, english) in eligibleTuples:
		if (hanzi == targetHanzi):
			return pinyin 
	return -1 

def readChineseFiles(dirname, filename):
	df_chinese = pd.read_csv(os.path.join(dirname, filename))
	pinyinList = list(map(lambda text: text.strip(), list(df_chinese["pinyin"]))) # list(df_chinese["pinyin"]).map(lambda text: text.strip())
	simplifiedCharactersList = list(map(lambda text: text.strip(), list(df_chinese["word_simplified"])))
	EnglishDefList = list(map(lambda text: text.strip(), list(df_chinese["cc_cedict_english_definition"]))) #  list(df_chinese["English Definition"]).map(lambda text: text.strip())

	chineseDictionary = {} # maps from the kanji to the corresponding english definitions
	chineseWordTuples = []

	for hanzi, pinyin, english in zip(simplifiedCharactersList, pinyinList, EnglishDefList):
		pinyinCompressed = "".join(pinyin.split(" "))
		if pinyin in chineseDictionary: 
			chineseDictionary[hanzi].append(english)
		else:
			chineseDictionary[hanzi] = [english]
		
		chineseWordTuples.append((pinyinCompressed, hanzi, english))

	#pprint.pprint(len(chineseWordTuples)) #[:100])
	return chineseWordTuples, chineseDictionary

chineseWordTuples, chineseDictionary = readChineseFiles(DICTIONARY_DIR, CHINESE_FILENAME)

class ChineseWordleSolver(WordleSolver):
	def __init__(self, numGuesses, numLetters, secretKana, secretWord, eligibleTuples, 
			  startingGuess = None, useBaseline = True):
		self.numLetters = numLetters 
		self.numGuesses = numGuesses 
		self.guesses = [""]
		self.startingGuess = startingGuess

		self.secretKana = secretKana
		self.secretWord = secretWord
	
		self.eligibleKana = [tup[0] for tup in eligibleTuples]
		self.eligibleKana = list(set(self.eligibleKana))

		self.useBaseline = useBaseline

class ChineseWordleGame(WordleGame):
	def __init__(self, numGuesses, numLetters, debugMode = False):
		chineseWordTuples, chineseDictionary = readChineseFiles(DICTIONARY_DIR, CHINESE_FILENAME)
		self.eligibleTuples = eligibleTuples = filterWords(chineseWordTuples, NUM_LETTERS)
		self.secretKana, self.secretWord, self.secretDefinition = getRandomChineseWord(self.eligibleTuples)
		self.language = "Mandarin"

		self.numGuesses, self.numLetters = numGuesses, numLetters
		self.guesses = []
		self.startingGuess = None

		if debugMode:
			print(f"Secret {numLetters} letter Mandarin word selected from {len(self.eligibleTuples)} eligible words")
			print(f"Secret Letters: {self.secretKana}, Word: {self.secretWord}, Definition: {self.secretDefinition}")
			
	def run(self, graphics = True, useBaseline = True):
		self.initializeGame()
		self.solver = ChineseWordleSolver(self.numGuesses, self.numLetters, self.secretKana, 
				self.secretWord, self.eligibleTuples, startingGuess = self.startingGuess, useBaseline = useBaseline)
		numGuessesNeeded = self.solver.solve(graphics)
		if graphics: self.runGraphics()
		return numGuessesNeeded

def solveChineseWord(secretPinyin, startingGuess = "dǎkāi"):  # means tomorrow in Korean

	game = ChineseWordleGame(NUM_GUESSES, NUM_LETTERS, debugMode = True)
	chineseWordTuples, chineseDictionary = readChineseFiles(DICTIONARY_DIR, CHINESE_FILENAME)
	eligibleTuples = filterWords(chineseWordTuples, NUM_LETTERS)
	print(len(eligibleTuples))
	pprint.pprint(eligibleTuples[:10])

	game.setStartingWord(startingGuess)

	if secretPinyin != None:
		secretHanzi = findMatchingPinyin(secretPinyin, eligibleTuples)
		game.setSolution(secretPinyin, secretHanzi, chineseDictionary[secretHanzi])

	numGuessesNeeded = game.run(graphics = True)
	if (numGuessesNeeded != -1):
		print(f"Solved with {numGuessesNeeded}　guess attempts!")
	else:
		print("Did not solve unfortunately :(")

if __name__ == "__main__":
	eligibleChineseTuples = filterWords(chineseWordTuples, NUM_LETTERS)
	if (len(sys.argv) > 1): 
		pinyin = findMatchingHanzi(sys.argv[1].lower(), chineseWordTuples)
		if pinyin == -1: raise ValueError("invalid input")
		solveChineseWord(pinyin, startingGuess = "dàxué")
	else: 
		randomPinyin, randomHanzi, randomEnglish = getRandomChineseWord(eligibleChineseTuples)
		print(f"Word: {randomHanzi}, Definition: {randomEnglish}")
		solveChineseWord(randomPinyin)