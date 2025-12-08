import pandas as pd
import os
from tqdm import tqdm
import numpy as np

JAPANESE_DIR = "./dictionaries"

def readJapaneseFiles(dirName):
	df_words = pd.read_csv(os.path.join(dirName, "japanese-words.tsv"), delimiter = "\t")
	kanaList = list(df_words["kana"])
	wordList = list(df_words["word or phrase"])
	translationList = list(df_words["translation"])
	tagsList = list(df_words["tags"])

	wordTuples = []
	jisho = {} # maps each pronounciation kana to list of (word, translation) pairs due to homophones 
	for kana, word, translation, tags in zip(kanaList, wordList, translationList, tagsList):
		if not isnan(tags):
			tagsParsed = [tag.strip() for tag in tags.split("|") if not isnan(tag)]
			if ("derogatory" in tagsParsed): continue # filtering out derogatory words
		if isnan(kana): continue # filter out loan words, other kana-only words for now
		# originally kana = word but need to translate katakana to hiragana for the kana section

		wordTuples.append((kana, word, translation))
		if kana in jisho: 
			jisho[kana].append({"word": word, "English": translation})
		else: 
			jisho[kana] = [{"word": word, "English": translation}]

	return wordTuples, jisho # is Japanese for dictionary lol

def filterWords(wordTuples, numLetters = 5):
	eligibleTuples = []
	for (kana, word, translation) in wordTuples: # tqdm(wordTuples) 
		if (len(kana.strip()) == numLetters):
			eligibleTuples.append((kana, word, translation))
	return eligibleTuples

def isnan(input):
	return type(input) == float

def getRandomJapaneseWord(eligibleTuples):
	index = np.random.randint(0, len(eligibleTuples))
	return eligibleTuples[index]

"""
ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖ
"""

def getHiraganaChars():
	UNICODE_MIN, UNICODE_MAX = 0x3041, 0x3096

	HIRAGANA_SYLLABARY = "" # why am i yelling lol
	for i in range(UNICODE_MIN, UNICODE_MAX + 1):
		HIRAGANA_SYLLABARY += chr(i)

	DAKUTEN_MAPPINGS = {}
	vowels = "ぁあぃいぅうぇえぉお"
	kColumn = "かがきぎくぐけげこご" # [ka, ga, ki, gi, ku, gu, ke, ge, ko, go]
	sColumn = "さざしじすずせぜそぞ"
	tColumn = "ただちぢつづてでとど"
	yColumn = "ゃやゅゆょよ"

	for dakutenPairs in [vowels, yColumn]:
		for i in range(0, len(dakutenPairs), 2):
			DAKUTEN_MAPPINGS[dakutenPairs[i + 1]] = dakutenPairs[i + 1]
			DAKUTEN_MAPPINGS[dakutenPairs[i]] = dakutenPairs[i + 1]

	for dakutenPairs in [kColumn, sColumn, tColumn]:
		for i in range(0, len(dakutenPairs), 2):
			DAKUTEN_MAPPINGS[dakutenPairs[i]] = dakutenPairs[i]
			DAKUTEN_MAPPINGS[dakutenPairs[i + 1]] = dakutenPairs[i]

	DAKUTEN_MAPPINGS["っ"] = "つ"
	DAKUTEN_MAPPINGS["ゕ"] = "か"
	DAKUTEN_MAPPINGS["ゖ"] = "け"

	DAKUTEN_MAPPINGS["ん"] = "ん"
	DAKUTEN_MAPPINGS["ゔ"] = "う"

	wColumn = "ゎわゐゑを"
	for char in wColumn: DAKUTEN_MAPPINGS[char] = char
	DAKUTEN_MAPPINGS["ゎ"] = "わ" # override

	nColumn = "なにぬねの"
	mColumn = "まみむめも"
	rColumn = "らりるれろ"
	for kana in nColumn + mColumn + rColumn: 
		DAKUTEN_MAPPINGS[kana] = kana

	hColumn = "はばぱひびぴふぶぷへべぺほぼぽ"
	for i in range(0, len(hColumn), 3):
		DAKUTEN_MAPPINGS[hColumn[i]] = hColumn[i]
		DAKUTEN_MAPPINGS[hColumn[i + 1]] = hColumn[i]
		DAKUTEN_MAPPINGS[hColumn[i + 2]] = hColumn[i]

	return HIRAGANA_SYLLABARY, DAKUTEN_MAPPINGS

def simplifyDakuten(kanaString, dakutenMappings):
	newString = ""
	for kana in kanaString: 
		newString += dakutenMappings[kana] if (kana in dakutenMappings) else kana
	return newString 

if __name__ == "__main__":
	wordTuples, jisho = readJapaneseFiles(JAPANESE_DIR)
	kanaCountToFreq = {}
	for (kana, word, English) in wordTuples:
		kanaCount = len(kana)
		if (kanaCount in kanaCountToFreq): kanaCountToFreq[kanaCount] += 1
		else: kanaCountToFreq[kanaCount] = 1

	print(kanaCountToFreq, "\n")

	HIRAGANA_SYLLABARY, DAKUTEN_MAPPINGS = getHiraganaChars()
	print(HIRAGANA_SYLLABARY, len(HIRAGANA_SYLLABARY))
	print(DAKUTEN_MAPPINGS, len(DAKUTEN_MAPPINGS))




