#Program reads a txt file; performs preprocessing; and extracts all the nouns from the data
#It displays various information(e.g., lexical density, token amount, and noun frequency)

#Program initiates a word game 
#Users guess letters from a random word
#Player starts with 5 points
#Player receives 1 point if they guess a correct letter; otherwise, an incorrect guess docks 1 point
#Game ends when player enters a "!" character or obtains a negative score

#Note: Default nltk POS tagging sometimes generate incorrect tags; hence, there might be some adjectives in the noun list

#Example program call: python Assignment-2.py anat19.txt

import sys
import nltk
from random import randint
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


#readFile reads a file and returns the data
def readFile(filePath):
    data = ""
    with open(filePath, 'r') as f:
        data = f.read()
         
    return data

#findLexicalDiversity computes the lexical diversity of the tokenized text
def findLexicalDiversity(text):
    tokens = word_tokenize(text)
    return len(set(tokens))/ len(tokens)

#findCharOccurrences finds all the occurences of a character in a string
#Return an array of indexes if string contains the character argument
#Can return an empty array if there are no occurrences
def findCharOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]


#preprocessText performs preprocessing on the raw text
#Returns a tuple of tokens and nouns
def preprocessText(text):
    wnl = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    tokens = word_tokenize(text.lower()) #tokenize lower-case raw text

    #Keep tokens that are alpha, have length > 5, and not in the NLTK stopword list
    filtered_tokens = [t for t in tokens if t.isalpha() and len(t) > 5 and t not in stop_words]

    #Lemmatize the tokens; apply set and list operations to make a list of unique lemmas
    lemmas = list(set([wnl.lemmatize(t) for t in filtered_tokens]))

    #Apply POS tagging to the unique lemmas
    tags = nltk.pos_tag(lemmas)

    #Print the first 20 tags
    print("\nFirst 20 tags:")
    for tag_tuple in tags[:20]:
        print(tag_tuple)

    #Create a list of lemmas that are nouns
    noun_list = [tup[0] for tup in tags if tup[1].startswith("N")]

    #Print the number of tokens and nouns
    print("\nToken and noun count:")
    print("Number of tokens:", len(tokens))
    print("Number of nouns:", len(noun_list))

    return tokens, noun_list



#createNounDict creates a dictionary of {noun: count of noun in tokens} items
#Function sorts the dictionary by count and returns a dictionary
def createNounDict(tokens, noun_list):

    #Initialize a dictionary with noun keys and default values of 0
    noun_dict = dict.fromkeys(noun_list, 0)

    #Iterate through token list and increment noun frequency
    for token in tokens:
        if token in noun_dict.keys():
            noun_dict[token] += 1

    return dict(sorted(noun_dict.items(), key=lambda x:x[1], reverse=True))

#playWordGame initiates a word guessing game
#Random word is selected from a list of 50 common nouns
def playWordGame(noun_list):
    gameFinished = False
    wordSolved = False
    playerScore = 5

    print("\nLet's play a word guessing game!")

    #Select a random noun
    rand_word = noun_list[randint(0, len(noun_list)-1)]

    #Initialize a word display array that changes with every letter guess
    rand_word_display = ["_"]*len(rand_word)

    #Support repeated game sessions
    while not gameFinished:
        correctLetterGuess = True

        #Display current state of random word
        print("\n")
        for i in rand_word_display:
            print(i, end=" ")
        print("\n")

        #Check solve flag and select a new random word
        if wordSolved:
            print("You solved it!")
            print("\nCurrent score:", playerScore)
            print("\nGuess another word")

            rand_word = noun_list[randint(0, len(noun_list)-1)]
            rand_word_display = ["_"]*len(rand_word)    
            wordSolved = False
            
            print("\n")
            for i in rand_word_display:
                print(i, end=" ")
            print("\n")
        
        #Prompt for a letter 
        letter = input("Guess a letter: ")

        if letter !="!":
            #Check if letter followed proper format
            while not letter.isalpha() or len(letter) > 1:
                print("Error: Please provide a valid letter.")
                letter = input("Guess a letter: ")
                if letter == "!":
                    break

        #Exit game if user enters a "!" character
        if letter == "!":
            print("Exit game")
            gameFinished = True
            continue

        letter = letter.lower()

        #Find indexes of letter occurrences in the string
        idxArr = findCharOccurrences(rand_word, letter)


        if len(idxArr) > 0:

            #Iterate through random word and check if letter had been guessed previously
            #Otherwise, replace "_" character with letter
            for idx in idxArr:
                if rand_word_display[idx] != "_":
                    correctLetterGuess = False
                    break
                else:
                    rand_word_display[idx] = letter

        else:
            correctLetterGuess = False

        #Increment score if user guesses a correct letter
        #Decrement score if user guesses an incorrect letter
        if correctLetterGuess:
            playerScore += 1
            print("Right! Score is", playerScore)
        else:
            playerScore -= 1
            print("Sorry, guess again. Score is", playerScore)

        #Check if user guessed the correct word
        if rand_word == "".join([str(i) for i in rand_word_display]):
            wordSolved = True

        #Print game over and stop game if user has a negative score
        if playerScore < 0:
            print("Game over: Score is negative")
            print("Correct word:", rand_word)
            gameFinished = True
        

def main():

    #Set file path to Python script argument
    filePath = ""
    if len(sys.argv) > 1:
        filePath = sys.argv[1]
    else:
        print("Error: Missing file path")
        exit()    

    #Parse text 
    text = readFile(filePath)

    #Print lexical diversity, formatted to 2 decimal places    
    print("Lexical diversity: %.2f\n" % findLexicalDiversity(text))    

    #Unpack lists of tokens and nouns
    tokens, noun_list = preprocessText(text)

    #Create a sorted dictionary of nouns
    sorted_dict = createNounDict(tokens, noun_list)
    
    #Print 50 nouns with the highest word count
    print("\n50 most common nouns and their counts:")
    for key, val in list(sorted_dict.items())[:50]:
        print(key+": "+str(val)) 

    #Create a list of 50 nouns
    noun_list = [key for key,val in list(sorted_dict.items())[:50]]

    #Start word game
    playWordGame(noun_list)


if __name__ == '__main__':
    main()