import time
import nltk 
import copy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize, sent_tokenize 
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer 
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn

import requests
from bs4 import BeautifulSoup

from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
from collections import defaultdict

porter = PorterStemmer()
lancaster=LancasterStemmer()
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

#Mines the textual abstract of a paper given pubmed uid
def abstract(uid):
    url ='https://www.ncbi.nlm.nih.gov/pubmed/?term='+uid
    page = requests.get(url)
    page.status_code

    soup = BeautifulSoup(page.text, 'html.parser')
    str1=''

    i=10
    flag=True

    while(flag):
        line=soup.find_all('p')[i].get_text()
        if(line.find('8600 Rockville Pike, Bethesda')==-1):
            str1=str1+'\n'+line
            i+=1
            #print(line)
            continue
        
        flag=False

    return str1

#converts a given list of uid's into a list of abstract texts
def abs_list(uid_l,n):
    text=[]
    for i in range(min(n,len(uid_l))):
        text.append(abstract(uid_l[i])[1:])

    return text

# gathers uids from given file
def uid_from_file(filename):
    uid_l=[]
    fo=open(filename,"r+")
    for line in fo:
        uid_l.append(line[:-1])
    return uid_l

def merge(papers):
    mess=[]
    for p in papers:
        mess+=(word_tokenize(p))
    merged=[(lemmatizer.lemmatize(i)).lower()  for i in mess if i not in stop_words and i not in ['(',')','-','!','.'] and any(c.isalpha() for c in i)]
    return merged

def freq_dict(words):
    fq= defaultdict( int )
    for w in words:
        fq[w] += 1
    return fq

def merged_freq(fq,l,up):
    mergedf=[]
    for i in fq.keys():
        if fq[i]>=l and fq[i]<=up:
            mergedf.append(i)
    return mergedf

uid_l=uid_from_file('union_training_uids.txt')
papers=abs_list(uid_l,50)
merged=merge(papers)
freq_d=freq_dict(merged)

mergedf=merged_freq(freq_d,2,3)

print(mergedf)

