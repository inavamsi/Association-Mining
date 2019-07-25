import requests
from bs4 import BeautifulSoup


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

def abs_list(uid_l,n):
    text=[]
    for i in range(min(n,len(uid_l))):
        text.append(abstract(uid_l[i])[1:])

    return text

def uid_from_file(filename):
    uid_l=[]
    fo=open(filename,"r+")
    for line in fo:
        uid_l.append(line[:-1])
    return uid_l


uid_l=uid_from_file('union_training_uids.txt')

text=abs_list(uid_l,5)
print(text)
