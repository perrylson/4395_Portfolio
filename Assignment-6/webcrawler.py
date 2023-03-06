#Script extracts data from sites on a given subject, which in this case is the San Francisco Bay Area
#Uses Beautiful Soup to perform web scraping
#Performs preprocessing on text 
#Calculates token popularity with tf-idf metric; score is used for finding top terms in the sites
#Generates a knowledge base by iterating through sites and extracting facts for each term
#Note: Must install nltk, bs4 via pip

from nltk import word_tokenize
import pickle
from bs4 import BeautifulSoup
import requests
import urllib.request
import re
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import math



#Crawl the website with given starter URL; extract relevant URLs and outputs a list
def webCrawl(starter_URL, link_amt):
    response = requests.get(starter_URL)
    soup = BeautifulSoup(response.text, features="html.parser")
    linkArr = [starter_URL]
    i = 1

    #Iterate through a tags
    for link in soup.find_all("a"):
        if i >= link_amt:
            break
        link_res = str(link.get('href'))
        if 'bay' in link_res or 'area' in link_res:
            if '&' in link_res:
                idx = link_res.find('&')
                link_res = link_res[:idx]
            if link_res.startswith('http') and 'google' not in link_res and 'pdf' not in link_res and 'web.archive' not in link_res: 
                if checkValidSite(link_res):
                    linkArr.append(link_res)
                    i += 1
    return linkArr

#Some source sites on Wikipedia are outdated, so they'll return a 404 status error
#checkValidSite verifies if page still exist
def checkValidSite(URL):
    flag = True
    req = urllib.request.Request(url=URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read()  
    except urllib.request.HTTPError as e:
        if e.getcode() == 404:
            flag = False
        else:
            raise 
    return flag

#helper function
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

#Scrape the raw data from the URLs and save it as pickle files
def scrapeText(linkArr):
    for i in range(len(linkArr)):
        fileName = "site_" + str(i+1) + ".p"
        req = urllib.request.Request(url=linkArr[i], headers={'User-Agent': 'Mozilla/5.0'})

        html = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(html, features="html.parser")
        data = soup.findAll(string=True)
        result = list(filter(visible, data))
        data_str = ' '.join(result)
        pickle.dump(data_str, open(fileName, 'wb'))

#Preprocess documents and clean them
def cleanText(site_amt):
    punctuationList = [".", "!", "?"]
    removeList = ["/", "//", "|", "Google Tag"] #Some sites contain links or analytic tools 

    #Iterate through raw text and clean it 
    for i in range(site_amt):
        fileName = "site_" + str(i+1) + ".p"
        cleanFileName = "clean_" + fileName[:-2] + ".txt"
        data = pickle.load(open(fileName, 'rb'))
        #Remove new lines, tab characters, and Wikipedia's [] entries (ex: [13], [edit])
        clean_data = re.sub('\n|\t|\[[^\]]*\]', '', data)
        sentences = sent_tokenize(clean_data)

        with open(cleanFileName, "w", encoding="utf-8") as file:
            for sent in sentences:
                sent = " ".join(sent.split()) #Remove extra white spaces
                #Check if sentence contains valid characters and ends in punctuation marks
                if len(sent) > 0 and sent[-1] in punctuationList and not any(x in sent for x in removeList):
                    file.write(sent+"\n")


#Tokenize document; remove stop words and punctuations
def createTokens(doc):
    tokens = word_tokenize(doc.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [t for t in tokens if t.isalpha()  and t not in stop_words]
    return filtered_tokens

#Create a TF dictionary; term frequency is calculated by dividing token count by total amount of tokens
#Entries are token: result from tf formula
def createTFDict(filtered_tokens):
    tf_dict = dict.fromkeys(set(filtered_tokens), 0)

    for t in filtered_tokens:
        tf_dict[t] += 1
    
    for key in tf_dict.keys():
        tf_dict[key] = tf_dict[key] / len(filtered_tokens)
    return tf_dict

#Create an inverse dependency dictionary with TF dictionaries and corpus
#Used for penalizing words that occur in multiple documents
#Entries are token: result from idf formula
def createIDFDict(TFDictArr, vocab):

    #Create a list of keys from the TF dictionaries
    vocab_keys = [dict.keys() for dict in TFDictArr]
    idf_dict = {}
    
    #Iterate throuch each token in vocabulary
    for word in vocab:

        #Count the number of docs that contain at least one instance of the token
        tmp_amt = len(['x' for keys in vocab_keys if word in keys])

        #Apply log function and divide total number of docs by the earlier occurence variable
        #Add 1 to numerator and denominator to avoid negative result and division by 0
        idf_dict[word] = math.log((1+len(TFDictArr)/(1+tmp_amt)))

    return idf_dict

#Create a TF-IDF dictionary for each site 
#Calculate the TF-IDF score for the site's tokens; combine both TF and IDF to get final score of tokens
#Sort the dictionary with respect to score
#Entries are token: tf-idf score
def createTFIDFDict(tf, idf):
    tf_idf = {}
    
    for key in tf.keys():
        tf_idf[key] = tf[key] * idf[key]
    
    return dict(sorted(tf_idf.items(), key=lambda x:x[1], reverse=True))

#Create a list of popular terms from the sites; uses tf-idf metric to calculate each token's score
def createTermList(site_amt):
    vocab = []
    TFDictArr = []
    termList = []

    #Iterate through cleaned sites and create a TF dictionary
    #Create a corpus of tokens from the sites
    for i in range(site_amt):
        fileName = "clean_site_" + str(i+1) + ".txt"
        with open(fileName, 'r', encoding="utf-8") as f:
            doc = f.read()
            tokens = createTokens(doc)
            temp_dict = createTFDict(tokens)
            vocab.extend(tokens)
            TFDictArr.append(temp_dict)
    
    #Create a IDF dictionary 
    IDF_dict =createIDFDict(TFDictArr, vocab)
    
    #Iterate through the TF dictionaries
    for dictionary in TFDictArr:

        #Create the TF-IDF dictionary
        TF_IDF_dict = createTFIDFDict(dictionary, IDF_dict)

        #Extract the top 3 terms from each site and append them to the list of terms
        for tup in list(TF_IDF_dict.items())[:3]:
            termList.append(tup[0])
    
    #Apply set operations to remove redundant terms
    termList = list(set(termList))
    
    #Display the list of top terms
    print("Top " + str(len(termList)) + " Terms:")
    for term in termList:
        print(term)
    
    return termList    


#Populate a knowledge base dictionary with facts from the cleaned sites; save N facts for each term
#Entries are term: array of string facts
def createKnowledgeBase(knowledgeBase, site_amt, term_fact_amt):
    for term in knowledgeBase:
        fact_counter = 0

        for i in range(site_amt):
            fileName = "clean_site_" + str(i+1) + ".txt"
            with open(fileName, 'r', encoding="utf-8") as f:
                lines = f.read().splitlines()
                for line in lines:
                    #Add fact to knowledge base if sentence contains term
                    if term in line:
                        knowledgeBase[term].append(line)
                        fact_counter += 1
                    
                    if fact_counter >= term_fact_amt:
                        break

            if fact_counter >= term_fact_amt:
                break

    return knowledgeBase

def main():
    starter_URL = "https://en.wikipedia.org/wiki/San_Francisco_Bay_Area"
    
    #Define the amount of URLS to extract
    site_amt = 15

    #Define the number of facts per term
    term_fact_amt = 3

    #Generate the list of links
    linkArr = webCrawl(starter_URL, site_amt)
    
    #Save the site's content as raw text files
    scrapeText(linkArr)

    #Load raw text files; clean them; and save them as cleaned files
    cleanText(site_amt)
    
    #Perform tf-idf calculations and return a list of top terms
    termList = createTermList(site_amt)

    #Use domain knowledge to select top ten terms from the list of terms
    knowledgeBase = {"California": [], "war": [], "town": [], "museum": [], "Francisco": [],
                      "Bay": [], "downtown": [], "shipyards": [], "data": [], "Alviso": []}
 
    #Find facts in the cleaned site files and saved them to the relevant keys
    knowledgeBase = createKnowledgeBase(knowledgeBase, site_amt, term_fact_amt)

    #Print knowledge base for the top ten terms
    print("\n\nKnowledge Base:\n\n")
    
    for key, arr in list(knowledgeBase.items()):
        print(str(term_fact_amt) + " Facts about " + key + ":" "\n")
        for fact in arr:
            print("- "+fact+"\n")

        print("\n")
    
    #Save knowledge base dictionary as a pickle file 
    pickle.dump(knowledgeBase, open("knowledge_base.p", 'wb'))

if __name__ == '__main__':
    main()
