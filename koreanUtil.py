import pandas as pd 
import numpy as np
import os

import unicodedata

KOREAN_DIR = "./dictionaries"

def findMatchingHangul(targetLetters, eligibleTuples):
	for (letters, hangul, english) in eligibleTuples:
		if (letters == targetLetters):
			return hangul 
	return -1 

def isnan(input):
	return type(input) == float

def getRandomKoreanWord(eligibleTuples):
	index = np.random.randint(0, len(eligibleTuples))
	return eligibleTuples[index]

def readKoreanFiles(dirName):
	df_korean = pd.read_csv(os.path.join(dirName, "korean-words.csv"))
	hangulList = list(df_korean["Form"])
	koreanDefList = list(df_korean["Korean Definition"])
	EnglishDefList = list(df_korean["English Definition"])

	koreanDictionary = {}
	koreanWordTuples = []

	for hangul, koreanDefinition, EnglishDefinition in zip(hangulList, koreanDefList, EnglishDefList):

		#produce tuples with (hangul, jamo letters, englishDefinition) 
		if hangul in koreanDictionary: 
			koreanDictionary[hangul].append(EnglishDefinition)
		else:
			koreanDictionary[hangul] = [EnglishDefinition] 

		jamoLetters = "".join(splitHangul(hangul))
		koreanWordTuples.append((jamoLetters, hangul, EnglishDefinition))

	return koreanWordTuples, koreanDictionary

def splitHangul(hangulWord):
	allJamoLetters = []
	for hangulSyllable in hangulWord:
		jamoLetters = list(unicodedata.normalize("NFD", hangulSyllable))
		allJamoLetters.extend(jamoLetters)

	return allJamoLetters

if __name__ == "__main__":
	koreanWordTuples, koreanDictionary = readKoreanFiles(KOREAN_DIR)

	sampleWord = "안녕하세요"
	print(splitHangul(sampleWord))

	for tup in koreanWordTuples[:10]:
		print(tup[2])





