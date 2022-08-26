import requests
from bs4 import BeautifulSoup as Soup
import os.path

# clean up the soup we construct from the links
def clean_soup(link):
    data = requests.get(link).text
    soup = Soup(data, "lxml")
    blacklist = ["script", "style"]
    attrlist = ["class", "id", "name", "style", 'cellpadding', 'cellspacing']
    skiptags = ['font', 'a', 'b', 'i', 'u']
    
    for tag in soup.findAll():
        if tag.name.lower() in blacklist:
            # blacklisted tags are removed in their entirety
            tag.extract()

        if tag.name.lower() in skiptags:
            tag.replaceWithChildren()
            
        for attribute in attrlist:
            del tag[attribute]
            
                    
    return soup


import unicodedata

# normalize the text
# remove some escape characters
def normtxt(txt):
    return unicodedata.normalize("NFKD",txt)

# get section from 10K
# looks for the term "item 1a" and collects text until "item 1b" is found
# returns None if there is no appropriate section found
# raise error when it cannot find the end of the section

def extract_section(soup, section='1a', section_end='1b'):
    
    search_next = ["p", "div", "table"]
    
    # loop over all tables
    items = soup.find_all(("table", "div"))

    myitem = None
    
    search_txt = ['item '+ section ]
    
    for i, item in enumerate(items):
        txt = normtxt(item.get_text())
        
        # this is to avoid long sentences or tables that contain the item
        if len(txt.split()) > 5:
            continue
        if any([w in txt.lower() for w in search_txt]):
            myitem = item
            
    if myitem is None:
        # print("section not found, returned None")
        return None
        
    lines = ""
    des = myitem.find_next(search_next)
    
    search_txt = [ 'item '+section_end ]

    while not des is None:
        des = des.find_next(search_next)
        
        if des is None:
            raise ValueError("end section not properly found")
            
        if any([w in normtxt(des.get_text()).lower() for w in search_txt]):
            break
            
        elif des is not None:
            if len(des.get_text().split()) > 2 and '|' not in normtxt(des.get_text()):
                # need to get rid of escape characters
                lines += normtxt(" "+des.get_text())
            #elif len(des.get_text().split()) > 2:
                #print("removing text: ",des.get_text())
            
        else:
            continue
    
    return lines[1:]
    
    

    