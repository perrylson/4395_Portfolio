#Program opens the unigram and bigram dictionaries
#It reads a file of sentences in different languages; predicts which language they're derived from; and saves results in a txt file
#Opens the result file and compare them with the correct labels
#Prints the accuracy along with the incorrect lines

from nltk import word_tokenize
from nltk.util import ngrams
import pickle

#readFile reads a file and returns the data
def readFile(filePath):
    data = ""
    with open(filePath, 'r') as f:
        data = f.read()

    return data

#Use Laplace smoothing to generate probability of language origin
def calc_prob(text_input, unigram_dict, bigram_dict, vocab_size):
    tokens = word_tokenize(text_input) #Tokenize the text input

    #Extract unigrams and bigrams from the tokens
    unigram_input = list(ngrams(tokens, 1)) 
    bigrams_input = list(ngrams(tokens, 2))

    prob_laplace = 1

    #Iterate through each bigram
    for bigram in bigrams_input:

        #Extract count from bigram dictionary; otherwise set count to 0 for non-existent bigram
        b = bigram_dict[bigram] if bigram in bigram_dict else 0

        #For bigram's first word, extract count from unigram dictionary; otherwise set count to 0 for non-existent unigram
        u = unigram_dict[(bigram[0],)] if (bigram[0],) in unigram_dict else 0

        #Calculate Laplace Smoothing
        prob_laplace *= ((b+1)/(u+vocab_size))

    return prob_laplace

def main():

    #Open the unigram and bigram dictionaries
    ugram_dict_eng = pickle.load(open('data/ugram_dict_English.p', 'rb'))
    bigram_dict_eng = pickle.load(open('data/bigram_dict_English.p', 'rb'))
    
    ugram_dict_fre = pickle.load(open('data/ugram_dict_French.p', 'rb'))
    bigram_dict_fre = pickle.load(open('data/bigram_dict_French.p', 'rb'))

    ugram_dict_ita = pickle.load(open('data/ugram_dict_Italian.p', 'rb'))
    bigram_dict_ita = pickle.load(open('data/bigram_dict_Italian.p', 'rb'))
    
    #Read in test file 
    testFileArr = readFile("data/LangId.test").splitlines()

    #Extract correct labels
    testFileLabels = [i.split()[1] for i in readFile("data/LangId.sol").splitlines()]

    #Calculate total vocab size of the three languages
    vocab_size = len(ugram_dict_eng)+len(ugram_dict_fre)+len(ugram_dict_ita)
    
    resArr = []

    #Iterate through test file and calculate language probability for each sentence
    for i in range(len(testFileArr)):
        prob_eng = calc_prob(testFileArr[i], ugram_dict_eng, bigram_dict_eng, vocab_size)
        prob_fre = calc_prob(testFileArr[i], ugram_dict_fre, bigram_dict_fre, vocab_size)
        prob_ita = calc_prob(testFileArr[i], ugram_dict_ita, bigram_dict_ita, vocab_size)
        probRes = max(prob_eng, prob_fre, prob_ita)

        #Save line number and chosen language 
        if probRes == prob_eng:
            resArr.append(str(i+1) + " " + "English")
        elif probRes == prob_fre:
            resArr.append(str(i+1) + " " + "French")
        else:
            resArr.append(str(i+1) + " " + "Italian")  

    #Write the result file
    with open("data/res.txt", "w") as file:
        for res in resArr:
            file.write(res+"\n")

    #Open the result file
    resLabels = [i.split()[1] for i in readFile("data/res.txt").splitlines()]

    #Measure accuracy
    numCorrect = 0
    totalAmt = len(testFileLabels)
    lineArr = []

    #Iterate through the results and compare them with correct labels; if incorrect result, then save the line number in the array
    for i in range(len(testFileLabels)):
        if resLabels[i] == testFileLabels[i]:
            numCorrect += 1
        else:
            lineArr.append(i+1)

    #Calculate and print accuracy
    acc = numCorrect/totalAmt
    print("Accuracy: %.2f"% acc)
    
    #Print incorrect lines if they exist
    if len(lineArr) > 0:
        print("Incorrect Line(s):")
        for lineNum in lineArr:
            print(lineNum)

if __name__ == '__main__':
    main()