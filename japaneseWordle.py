"""
Wordle environment for Japanese specifically
probabilistic ranking mechanism for the words instead of just random selection, based on information entropy gain 
"""

import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
import os
import math
from tqdm import tqdm
from japaneseUtil import *
from koreanUtil import *
import sys
import matplotlib.font_manager as fm

#NotoSansKR-VariableFont_wght.ttf
fprop = fm.FontProperties(fname='Noto_Sans_KR/static/NotoSansKR-ExtraBold.ttf')

chineseFProp = fm.FontProperties(fname='SimHei.ttf')

# dataset: https://www.kaggle.com/datasets/dinislamgaraev/popular-japanese-words

NUM_GUESSES = 6
NUM_LETTERS = 5 # for Japanese, really means kana, but for consistency with Wordle terminology

#NUM_LETTERS = 5
koreanWordTuples, koreanDictionary = readKoreanFiles(KOREAN_DIR)
ELIGIBLE_TUPLES = filterWords(koreanWordTuples, NUM_LETTERS)

JAPANESE_DIR = "./dictionaries"
DEFAULT_COLOR = [32, 32, 32]
CORRECT_COLOR = [178, 255, 102]
FOUND_COLOR = [255, 255, 153]
WRONG_COLOR = [192, 192, 192]
RGB_NUM_CHANNELS = 3
_, DAKUTEN_MAPPINGS = getHiraganaChars()

DICTIONARY_DIR = "dictionaries"
CHINESE_FILENAME = "chinese-words.csv"

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

def findMatchingPinyin(targetPinyin, eligibleTuples):
	for (pinyin, hanzi, english) in eligibleTuples:
		if (pinyin == targetPinyin):
			return hanzi 
	return -1 

def getGuessColors(currentGuess, secretKana):
	numLetters = len(secretKana)
	highlightColors = [WRONG_COLOR for _ in range(numLetters)]

	remainingCopies = {}
	for i in range(numLetters):
		secretChar = secretKana[i] 
		if secretChar in remainingCopies: remainingCopies[secretChar] += 1
		else: remainingCopies[secretChar] = 1
		# decrement green copies right away
		if secretChar == currentGuess[i]: 
			remainingCopies[secretChar] -= 1
			highlightColors[i] = CORRECT_COLOR
		
	# now scan the current guess string for yellow letters / characters
	for i in range(numLetters):
		if (highlightColors[i] == CORRECT_COLOR): continue # skip already green letters
		guessLetter = currentGuess[i]
		if (guessLetter in secretKana and remainingCopies[guessLetter] > 0):
			highlightColors[i] = FOUND_COLOR
			remainingCopies[guessLetter] -= 1

	return highlightColors

class WordleGameWindow(): #TODO: adapt to support Chinese (maybe Pinyin) and Korean as well
	def __init__(self, numGuesses, numLetters, secretKana, secretWord, guesses, language = "Japanese"):
		self.grid = np.zeros((numGuesses, numLetters, RGB_NUM_CHANNELS))
		self.grid = self.grid.astype(np.int32)

		self.secretKana = secretKana  #eventually change to secretLetters to generalize
		self.secretWord = secretWord
		self.guesses = guesses
		self.numGuesses = numGuesses 
		self.numLetters = numLetters 
		self.language = language

		if language == "Japanese":
			self.fontName = "Hiragino Sans"
		elif language == "Korean":
			self.fontName = "Noto Serif CJK"
		elif language == "Mandarin": # because of Pinyin usage as well
			self.fontname = "Noto Serif CJK"
		elif language == "English":
			self.fontname = "Arial"

	def updateGuesses(self, newGuessesList):
		self.guesses = newGuessesList

	def setBoardColors(self): # need to the secretWord to highlight the letters
		for i in range(self.numGuesses):
			if (i >= len(self.guesses) - 1): 
				for j in range(0, self.numLetters): self.grid[i,j] = DEFAULT_COLOR 
				continue

			if self.language == "Japanese":
				currentGuess = simplifyDakuten(self.guesses[i], DAKUTEN_MAPPINGS)
				secretKana = simplifyDakuten(self.secretKana, DAKUTEN_MAPPINGS)
			else:
				currentGuess = self.guesses[i]
				secretKana = self.secretKana

			highlightColors = getGuessColors(currentGuess, secretKana)
			for j in range(self.numLetters): 
				self.grid[i,j] = highlightColors[j]

	def addGridLines(self, ax):
		NUM_POINTS_PER_LINE = 100 # i.e. the grid lines resolution quality 
		LINE_WIDTH = 2
		LINE_COLOR = "black"
		x_coords = np.linspace(0, NUM_LETTERS, 100) - 0.5
		# write the horizontal lines to the Wordle window screen  
		for y_guess in range(NUM_GUESSES + 1):
			y_coords = (-0.5 + y_guess) * np.ones(NUM_POINTS_PER_LINE)
			ax.plot(x_coords, y_coords, color = LINE_COLOR, linewidth = LINE_WIDTH)

		# write the vertical lines to the Wordle window screen
		y_coords = np.linspace(0, NUM_GUESSES, 100) - 0.5
		for x_guess in range(NUM_LETTERS + 1):
			x_coords = (-0.5 + x_guess) * np.ones(NUM_POINTS_PER_LINE)
			ax.plot(x_coords, y_coords, color = LINE_COLOR, linewidth = LINE_WIDTH)

	def createGameBoard(self):
		TITLE_FONT_SIZE, LETTER_FONT_SIZE = 17, 24

		self.fig, self.ax = plt.subplots()

		if self.language == "Japanese":
			self.fig.suptitle(f"{self.language} Wordle\nTarget: {self.secretKana} ({self.secretWord})", 
				fontname = self.fontName, fontsize = TITLE_FONT_SIZE, y = 0.99)
		elif self.language == "Korean":
			self.fig.suptitle(f"{self.language} Wordle\nTarget: {self.secretWord}", 
				fontproperties = fprop, fontsize = TITLE_FONT_SIZE, y = 0.99)
		elif self.language == "English":
			self.fig.suptitle(f"{self.language} Wordle\nTarget: {self.secretWord}", 
				fontproperties = fprop, fontsize = TITLE_FONT_SIZE, y = 0.99)
		elif self.language == "Mandarin":
			self.fig.suptitle(f"Mandarin Chinese Wordle\nTarget: {self.secretKana} ({self.secretWord})", 
				fontproperties = chineseFProp, fontsize = TITLE_FONT_SIZE, y = 0.99)
		
		self.setBoardColors()
		im = self.ax.imshow(self.grid)
		for i in range(NUM_GUESSES):
			if (i >= len(self.guesses)): continue
			if (len(self.guesses[i]) == 0): continue
			guess = self.guesses[i]
			if self.language == "Korean": 
				hangul = findMatchingHangul(guess, ELIGIBLE_TUPLES)
				hangulLetters = [list(unicodedata.normalize("NFD", syllable)) for syllable in hangul]
				currSyllable = 0
				syllableLetter = 0
			elif self.language == "Mandarin":
				hanzi = findMatchingPinyin(guess, chineseWordTuples)

			for j in range(NUM_LETTERS):
				if (j >= len(guess)): continue 

				if (self.language == "Japanese" or self.language == "English"):
					letter = guess[j]
				elif (self.language == "Korean"): 
					letter = hangul[currSyllable]
					syllableLetter += 1
					if (syllableLetter == len(hangulLetters[currSyllable])):
						syllableLetter = 0
						currSyllable += 1
				elif (self.language == "Mandarin"):
					letter = guess[j]

				fontColor = "black" if (i < len(self.guesses) - 1) else "white"

				if (self.language == "Japanese"):
					text = self.ax.text(j, i, letter, ha="center", va="center", color = fontColor, 
						fontname = self.fontName, fontsize = LETTER_FONT_SIZE)
				elif (self.language == "Korean"):
					hangulJamo = unicodedata.normalize("NFD", letter)
					text = self.ax.text(j, i, hangulJamo[syllableLetter - 1], ha="center", va="center", color = fontColor, 
						fontproperties = fprop, fontsize = LETTER_FONT_SIZE + 6)

				elif (self.language == "English"):
					text = self.ax.text(j, i, letter, ha="center", va="center", color = fontColor, 
						fontsize = LETTER_FONT_SIZE )
				
				elif (self.language == "Mandarin"):
					text = self.ax.text(j, i, letter, ha="center", va="center", color = fontColor, 
						fontproperties = chineseFProp, fontsize = LETTER_FONT_SIZE + 10)
				
				if (self.language == "Korean" and j == NUM_LETTERS - 1):
					SCREEN_WIDTH = 6 - 0.7
					text = self.ax.text(SCREEN_WIDTH, i, hangul, ha="center", va="center", color = fontColor, 
						fontproperties = fprop, fontsize = LETTER_FONT_SIZE + 6)
				
				if (self.language == "Mandarin" and j == NUM_LETTERS - 1):
					SCREEN_WIDTH = 6 - 0.7
					text = self.ax.text(SCREEN_WIDTH, i, hanzi, ha="center", va="center", color = fontColor, 
						fontproperties = chineseFProp, fontsize = LETTER_FONT_SIZE + 10)


		self.addGridLines(self.ax)
		plt.axis("off")

		
	def displayGameBoard(self):
		plt.show()

# could try making the class more general to languages
# but Japanese is a fairly unique language
class WordleGame():
	def __init__(self, numGuesses, numLetters, debugMode = False):
		self.language = "Japanese"
		wordTuples, self.jisho = readJapaneseFiles(JAPANESE_DIR)
		self.eligibleTuples = filterWords(wordTuples, numLetters)
		self.secretKana, self.secretWord, self.secretDefinition = getRandomJapaneseWord(self.eligibleTuples)

		self.numGuesses, self.numLetters = numGuesses, numLetters
		self.guesses = []
		self.startingGuess = None

		if debugMode:
			print(f"Secret {numLetters}-kana Japanese word selected from {len(self.eligibleTuples)} eligible words in Jisho")
			print(f"Secret Kana: {self.secretKana}, Word: {self.secretWord}, Definition: {self.secretDefinition}")

	def initializeGame(self):
		self.guesses = [] # list of word guessed, including partial guesses
		#self.guesses = ["あいうち", "あいこう", "あいけん", "あい"]

	def setSolution(self, secretKana, secretWord, secretDefinition):
		self.secretKana, self.secretWord, self.secretDefinition = secretKana, secretWord, secretDefinition

	def setStartingWord(self, startingWord):
		self.startingGuess = startingWord

	def setSolver(self, solver):
		self.solver = solver
	
	def runGraphics(self):
		window = WordleGameWindow(self.numGuesses, self.numLetters, self.secretKana, 
			self.secretWord, self.guesses, self.language)
		window.updateGuesses(self.solver.getGuesses())
		window.createGameBoard()
		window.displayGameBoard()

	def run(self, graphics = True, useBaseline = True):
		self.initializeGame()

		self.solver = WordleSolver(self.numGuesses, self.numLetters, self.secretKana, 
				self.secretWord, self.eligibleTuples, 
				startingGuess = self.startingGuess, useBaseline = useBaseline)
		
		numGuessesNeeded = self.solver.solve(graphics)
		if graphics: self.runGraphics()
		return numGuessesNeeded

def isCompatible(submittedGuess, letterColors, nextGuess):
	numLetters = len(submittedGuess)

	indicesByColor = {"correct": [], "found": [], "wrong": []}
	for index, color in enumerate(letterColors): 
		if (color == CORRECT_COLOR): indicesByColor["correct"].append(index)
		elif (color == FOUND_COLOR): indicesByColor["found"].append(index)
		else: indicesByColor["wrong"].append(index)

	# check over green indices first
	for greenIndex in indicesByColor["correct"]:
		if (nextGuess[greenIndex] != submittedGuess[greenIndex]): return False
		# "zero" out this letter in guess string to show it's been accounted for 
		nextGuess = nextGuess[:greenIndex] + " " + nextGuess[greenIndex + 1:]

	# check over yellow indices now 
	for yellowIndex in indicesByColor["found"]:
		if (nextGuess[yellowIndex] == submittedGuess[yellowIndex]): return False 
		
		indexInNextGuess = nextGuess.find(submittedGuess[yellowIndex])
		if (indexInNextGuess == -1): return False
		nextGuess = nextGuess[:indexInNextGuess] + " " + nextGuess[indexInNextGuess + 1:]

	# check over gray indices now 
	for grayIndex in indicesByColor["wrong"]:
		indexInNextGuess = nextGuess.find(submittedGuess[grayIndex])
		if (indexInNextGuess != -1): return False
			
	return True 

def colorsToStr(colors):
	str = ""
	for color in colors: 
		if (color == CORRECT_COLOR): str += "🟩"
		elif (color == FOUND_COLOR): str += "🟨"
		elif (color == WRONG_COLOR): str += "🔲"
		else: str += " "
	return str

def colorsToPatternString(colors):
	str = ""
	for color in colors: 
		if (color == CORRECT_COLOR): str += "C"
		elif (color == FOUND_COLOR): str += "F"
		elif (color == WRONG_COLOR): str += "W"
		else: str += " "
	return str

class WordleSolver(): #designed for Japanese 
	def __init__(self, numGuesses, numLetters, secretKana, secretWord, eligibleTuples, 
			  startingGuess = None, useBaseline = True):
		self.numLetters = numLetters 
		self.numGuesses = numGuesses 
		self.guesses = [""]
		self.startingGuess = startingGuess

		self.secretKana = simplifyDakuten(secretKana, DAKUTEN_MAPPINGS)
		self.secretWord = secretWord
		self.hiragana = list(set(DAKUTEN_MAPPINGS.values()))
		
		self.eligibleKana = [simplifyDakuten(tup[0], DAKUTEN_MAPPINGS) for tup in eligibleTuples]
		self.eligibleKana = list(set(self.eligibleKana)) # remove duplicates after simplification

		self.useBaseline = useBaseline

	def getGuesses(self):
		return self.guesses.copy()

	def setBaselineModel(self, useBaseline = True):
		self.useBaseline = useBaseline
	
	def getInformationGain(self, guess, remainingCandidates):
		patternToWords = {}
		for candidate in remainingCandidates: 
			letterColors = getGuessColors(guess, candidate)
			colorPattern = colorsToPatternString(letterColors)
			if (colorPattern in patternToWords):
				patternToWords[colorPattern].append(candidate)
			else:
				patternToWords[colorPattern] = [candidate]
		
		# get the pattern with the least number of affiliated words essentially to narrow down the list
		numWords = len(remainingCandidates)
		expectedEntropy = 0.0
		for colorPattern, words in patternToWords.items():
			probabilityOfGroup = len(words) / numWords 
			expectedEntropy += probabilityOfGroup * math.log2(1 / probabilityOfGroup)

		return expectedEntropy
			
	def getBestEntropyGuess(self, remainingCandidates):
		# we don't know the true guess word, but for each candidate, we can simiulate across all possible words
		bestGuess = ""
		maxGainOfInformation = -1
		for guess in remainingCandidates:
			gainOfInformation = self.getInformationGain(guess, remainingCandidates)
			if (gainOfInformation > maxGainOfInformation):
				maxGainOfInformation = gainOfInformation
				bestGuess = guess
		
		if (bestGuess == ""): return remainingCandidates[0]
		return bestGuess		

	def solve(self, printMode = True):
		
		# summary: iterate through evaluating the guesses, and refining the words and so forth
		for guessNum in range(1, self.numGuesses + 1):
			if (len(self.eligibleKana) == 0): 
				return -1
				#raise ValueError(f"Error! Secret kana is {self.secretKana}, word is {self.secretWord}")
			
			if self.startingGuess != None and guessNum == 1: 
				submittedGuess = self.startingGuess
			else:
				if self.useBaseline:
					submittedGuess = np.random.choice(self.eligibleKana)
				else: 
					submittedGuess = self.getBestEntropyGuess(self.eligibleKana)

			self.guesses[len(self.guesses) - 1] = submittedGuess
			self.guesses.append("") # for next guess later

			letterColors = getGuessColors(submittedGuess, self.secretKana)
			colorString = colorsToStr(letterColors)
			#if printMode: print(f"Current Guess: {submittedGuess}, Result: {colorString}")  # get highlighted results
			if printMode: print(f"Current Guess: {submittedGuess}, Result: {colorString}")  # get highlighted results

			if (submittedGuess == self.secretKana): return guessNum
			self.reduceCandidatePool(submittedGuess, letterColors)

		return -1 # did not solve within numGuesses opportunities

	def reduceCandidatePool(self, submittedGuess, letterColors):
		stillEligible = []
		colorString = colorsToStr(letterColors)
		for newGuess in self.eligibleKana: 
			if (isCompatible(submittedGuess, letterColors, newGuess)):
				stillEligible.append(newGuess)
		self.eligibleKana = stillEligible

def getFrequencyTable(array):
	freqTable = {}
	for elem in array:
		if elem in freqTable: freqTable[elem] += 1
		else: freqTable[elem] = 1
	return freqTable

def solveJapaneseWord(secretKana):
	game = WordleGame(NUM_GUESSES, NUM_LETTERS, debugMode = False)
	wordTuples, jisho = readJapaneseFiles(JAPANESE_DIR)
	eligibleTuples = filterWords(wordTuples, NUM_LETTERS)
	game.setStartingWord("あさがお") # morning sunflower, has common hiragana letters

	secretIdx = np.random.randint(0, len(jisho[secretKana])) # due to homophones
	secretJishoEntry = jisho[secretKana][secretIdx]
	secretWord, English = secretJishoEntry["word"], secretJishoEntry["English"]
	game.setSolution(secretKana, secretWord, English)

	numGuessesNeeded = game.run(graphics = True)
	if (numGuessesNeeded != -1):
		print(f"Solved with {numGuessesNeeded}　guess attempts!")
	else:
		print("Did not solve unfortunately :(")

if __name__ == "__main__":
	NUM_LETTERS = 4
	SAMPLE_WORD = "きがつく"
	word = sys.argv[1] if len(sys.argv) > 1 else SAMPLE_WORD
	solveJapaneseWord(word)




