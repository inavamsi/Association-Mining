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
  
#checks whther a string has a digit
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

# Finds the list of nouns in a given phrase l
def nouns(l):
    is_noun = lambda pos: pos[:2] == 'NN'
    # do the nlp stuff
    tokenized = nltk.word_tokenize(l)
    nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)] 
    return nouns

# Finds the list of verbs in a given phrase l
def verbs(l):
    is_verb = lambda pos: pos[:2] == 'VB'
    # do the nlp stuff
    tokenized = nltk.word_tokenize(l)
    verbs = [word for (word, pos) in nltk.pos_tag(tokenized) if is_verb(pos)] 
    return verbs

#intersection of two lists
def intersection(l1,l2):
    return list(set(l1) & set(l2)) 

#union of two lists
def union(l1,l2):
    return list(set(l1) | set(l2)) 

# joins  a list of strings
def join_str(list):
    result= '' 
    for element in list:
        result += ' '+str(lemmatizer.lemmatize(element))
    return result

#checks whether two phrases match given a score and error
def term_match(l1,l2, score, flag, error,throw):
    #regulation, assembly, activation, developement, tissue, cell
    #throw=[]#'metabolic', 'assembly', 'developement', 'tissue', 'cell','pathway']
    #l1=[(lemmatizer.lemmatize(i)).lower() for i in l1 if i not in throw]
    #l2=[(lemmatizer.lemmatize(i)).lower()  for i in l2 if i not in throw]
   # l2=[i for i in l2 if i not in ['regulation', 'assembly', 'activation', 'developement', 'tissue', 'cell', 'detection','pathway']]
    
    l1=[(lancaster.stem(lemmatizer.lemmatize(i))).lower() for i in l1 if i not in throw]
    l2=[(lancaster.stem(lemmatizer.lemmatize(i))).lower()  for i in l2 if i not in throw]

    if len(l2)>1.5*len(l1):
        return False

    int_len=len(intersection(l1,l2))
    if(len(l2)==0 or len(l1)==0):
        return 0
    if(len(l2)>2 and len(l1)>2 and int_len<2):
        return False
    
    if 2*int_len*int_len/(len(l1)*len(l2)) < score:
        return False
    
    if(flag):
        return True

    sent1=join_str([i for i in l1 if i not in throw])
    sent2=join_str([i for i in l2 if i not in throw])
    int_nouns=len(intersection(nouns(sent1),nouns(sent2)))
    if len(nouns(sent1))> int_nouns+error*(2*score) or len(nouns(sent2))> int_nouns+error :
        return False     


    for i in l1:
        if hasNumbers(i):
            if i not in l2:
                return False
        if i.find('-')!=-1:
            found=False
            for j in l2:
                if j.find('-')!=-1:
                    found=True
                    break
            if(not found):
                return False
    for i in l2:
        if hasNumbers(i):
            if i not in l1:
                return False
        if i.find('-')!=-1:
            found=False
            for j in l1:
                if j.find('-')!=-1:
                    found=True
                    break
            if(not found):
                return False
    #print(l1,"***",l2)
    #print(int_len, "*****",2*int_len*int_len/(len(l1)*len(l2)))


    return True

#Finds the list of terms in a sentence for a given vocabulary
def term_list(sent,fileobj, winlen, similarity_score):
    prev_match=None
    count=0

    objlist=[]

    for i in range(len(sent)):
        if(sent[i] in fileobj.wordlist):
            objlist.append(sent[i])

    for j in range(len(fileobj.vocab)):
        small_list=[]
        for i in range(0,len(sent)-winlen+1):
            count+=1
            if(count==winlen+1):
                prev_match=None
            if term_match(sent[i:i+winlen],fileobj.vocab[j],similarity_score,fileobj.flag,fileobj.error,fileobj.throw):
                if(fileobj.orig[j]!=prev_match):
                    small_list.append(join_str(fileobj.orig[j]))
                    prev_match=fileobj.orig[j]
                    count=0
        if small_list!=[]:
            objlist+=small_list

    return objlist

# Class for each vocabulary namely HPO, GO, Gene Names, Protiens, pathways
class Mine():
    def __init__(self, name, filename,st,end,wordlist,flag, postfix, winlen_l, error,throw):
        fo = open(filename, "r+")
        self.orig=[]
        for line in fo:
            if postfix != None:
                line=line[:postfix]
            if end == None :
                split_lines=line.split()[st:]
            else:
                split_lines=line.split()[st:end]
            self.orig.append(split_lines)

        self.name=name
        self.throw=throw
        self.error=error
        self.winlen_l=winlen_l
        self.wordlist=wordlist
        self.flag=flag

        #for j in range(len(self.orig)):
        #    for i in self.orig[j]:
        #        if i.find('-')!=-1:
        #            print(i.split('-'))
        self.vocab = [[i.lower() for i in self.orig[j] if i not in stop_words ] for j in range(len(self.orig))]

#Given a list of papers, Print the associations onto screen
def print_associations(papers):
    for txt in papers:
        sentences = sent_tokenize(txt)
        orig_sentences=copy.deepcopy(sentences)
        sentences = [[i.lower() for i in word_tokenize(sentences[j])if i not in stop_words ] for j in range(len(sentences))]


        similarity_score=0.7
            
        print("")
        print("*************************")
        print("")

        for a in range(len(sentences)):
            sent=sentences[a]
            sent=[j for j in sent if j not in [',','-','!','.']]

            all_empty=True
            obj_lists=[]
            #print(sent)

            for fileobj in file_list:
                #print(fileobj)
                list2app=[]
                for temp in fileobj.winlen_l:
                    #print(temp, list2app, term_list(sent,fileobj, temp, similarity_score))
                    for phrase in term_list(sent,fileobj, temp, similarity_score):
                        if phrase not in list2app:
                            list2app.append(phrase)
                            all_empty=False
                obj_lists.append((fileobj.name,list2app))
            
            if(not all_empty):
                for name,i in obj_lists:
                    print(name," : ",i)
                print("")
                print("")


#Create an instance for each vocabulary
go = Mine('go',"terms.txt",2,-1,[],False,None,[3,4],1,['cell','pathway'])
hpo = Mine('hpo',"all_hpo.txt",0,None,[],False,-1,[3,4],0,[])
pcg = Mine('gene name',"uniprot.txt",-1,None,[],True,None,[1,2],0,[])
protien = Mine('protien',"uniprot.txt",0,1,[],True,None,[1],0,[])
pathways=Mine('pathways',"all_human_pathways.txt",1,-2,[],False,None,[3,4],1,['pathway'])

#List of vocabularoes we will use
file_list=[hpo,go,pcg,pathways,protien]


#Get paper abstracts and print associations
uid_l=uid_from_file('union_training_uids.txt')
papers=abs_list(uid_l,5)
print_associations(papers)
