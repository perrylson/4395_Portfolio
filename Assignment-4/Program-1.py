
#This program reads in corpuses of the English, French, and Italian languages; generates unigram and bigram dictionaries; and save them as pickle files
#Builds language models of English, French, and Italian
#Run this script before program 2
#Takes 6 - 7 minutes to finish program execution

#Example call: python Program-1.py

from nltk import word_tokenize
from nltk.util import ngrams
import pickle

#readFile reads a file and returns the data
def readFile(filePath):
    data = ""
    with open(filePath, 'r') as f:
        data = f.read().splitlines() #Detect and remove any new line characters

    return ''.join(data) #Join the string entries into one string

#Create unigram and bigram dictionaries of the text; items are unigram/bigram: amount of unigram/bigram in corpus
def createGramDicts(text):
    tokens = word_tokenize(text)
    unigrams = list(ngrams(tokens, 1))
    bigrams = list(ngrams(tokens, 2))

    unigram_dict = {t:unigrams.count(t) for t in set(unigrams)}
    bigram_dict = {b:bigrams.count(b) for b in set(bigrams)}

    return unigram_dict, bigram_dict

#Save pickle files
def savePickleFile(dict, fileName):
    pickle.dump(dict, open(fileName, 'wb'))
 

def main():  
    
    #Specify filepaths
    filePath1 = "data/LangId.train.English"
    filePath2 = "data/LangId.train.French"
    filePath3 = "data/LangId.train.Italian"

    #Read files
    text1 = readFile(filePath1)
    text2 = readFile(filePath2)
    text3 = readFile(filePath3)

    #Unpack unigram and bigram dictionaries
    ugram_1, bigram_1 = createGramDicts(text1)
    ugram_2, bigram_2 = createGramDicts(text2)
    ugram_3, bigram_3 = createGramDicts(text3)

    #Split the file path into an array of strings with a delimitter
    fileParts_1 = filePath1.split(".")
    fileParts_2 = filePath2.split(".")
    fileParts_3 = filePath3.split(".")

    #Save pickle files of dictionaries along with corresponding language
    savePickleFile(ugram_1, "data/ugram_dict_"+fileParts_1[-1]+".p")
    savePickleFile(bigram_1, "data/bigram_dict_"+fileParts_1[-1]+".p")
    savePickleFile(ugram_2, "data/ugram_dict_"+fileParts_2[-1]+".p")
    savePickleFile(bigram_2, "data/bigram_dict_"+fileParts_2[-1]+".p")
    savePickleFile(ugram_3, "data/ugram_dict_"+fileParts_3[-1]+".p")
    savePickleFile(bigram_3, "data/bigram_dict_"+fileParts_3[-1]+".p")

if __name__ == '__main__':
    main()
