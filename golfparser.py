__author__ = 'Bernie'
import urllib2, os
from bs4 import BeautifulSoup
from selenium import webdriver

playerDict={}

def get_player_data():
    driver = webdriver.PhantomJS(service_args=["--webdriver-loglevel=NONE"])
    driver.get("http://www.cbssports.com/golf/leaderboard/pga-tour/1186070/hyundai-tournament-of-champions")
    
    html = driver.page_source
    parsed_html = BeautifulSoup(html,'html.parser')
    tournaments = parsed_html.find("tbody", {"id": "LeaderboardSchedule"})
    leaderboard =  parsed_html.find("tbody", {"id": "LeaderboardData"})

    listEarn=[]
    row1 = leaderboard.findAll("tr",{"class","row1"})
    row2 = leaderboard.findAll("tr",{"class","row2"})

    for row in row1:
        items=row.findAll("td")
        name=items[3]
        rank =items[1]
        earn =items[5]
        #print(name.find("a").getText()+","+rank.find("dd").getText()+","+earn.find("dt").getText())
        tup=(rank.find("dd").getText(),earn.find("dt").getText())
        if(tup[1] != None and tup[1] != ""):# must have a salary
            playerDict[name.find("a").getText().split(" PC",1)[0]]=tup

    for row in row2:
        items=row.findAll("td")
        name=items[3]
        rank =items[1]
        earn =items[5]
        #print(name.find("a").getText()+","+rank.find("dd").getText()+","+earn.find("dt").getText())
        tup=(rank.find("dd").getText(),earn.find("dt").getText())
        if(tup[1] != None and tup[1] != ""): #must have a salary
            playerDict[name.find("a").getText().split(" PC",1)[0]]=tup
    
    os.system("pkill phantomjs") # for some reason driver.quit() doesnt kill the process

    
def get_player_names():
    return playerDict.keys()

def get_player_salaries():
    return [playerDict[player][1] for player in playerDict]   

#print(playerDict)
#
#
#
#
#
#
#for earning in list:
#    earn =earning.find("dt")
#    if earn != None:
#        #print(earn.getText())
#        listEarn.append(earn.getText())
#
#list = parsed_html.findAll("td",{"class","playername"})
#for player in list:
#    name =player.find("a")
#    if name != None:
#        if(listEarn.is)
#        playerDict[name.getText()]=listEarn.pop(0)
#        #print(name.getText())
#print playerDict
#
#
##print parsed_html.body.find('div', attrs={'class':'container'}).text
