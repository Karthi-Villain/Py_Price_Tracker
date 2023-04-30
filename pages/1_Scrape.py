import cloudscraper
from bs4 import BeautifulSoup
import csv, os, time, random
from datetime import date


def Amazon_Link(bsoup):
    global Current_Price
    if "In stock" in bsoup.find('div',id="availability").text:
        Current_Price=bsoup.find_all('span',class_="a-offscreen")[0].text
        Current_Price=int(Current_Price[1:-3].replace(',',''))
    else:
        Current_Price=0

def Flipkart_Link(bsoup):
    global Current_Price
    Current_Price=int(bsoup.find("div",class_="_30jeq3 _16Jk6d").text[1:].replace(',','').replace('.00',''))
    
def Save_Details(Current_Price):
    DuplicateDate=False
    File_Name=Product_ID+".csv"
    File_Dir=os.path.join(os.path.split(os.path.dirname(__file__))[0], "Details", File_Name)
    #Check For Date
    isExist = os.path.exists(File_Dir)
    if not isExist:
            with open(File_Dir,"a",newline='',encoding="utf-8") as ID_File2:
                write=csv.writer(ID_File2,delimiter=",")
                write.writerow(["date","prices"])
    with open(File_Dir,"r",newline='',encoding="utf-8") as ID_File:
        rows=ID_File.readlines()
        if len(rows)>=2 and str(date.today().strftime("%d/%m/%Y")) in str(rows[-1]) and Current_Price <= int(str(rows[-1])[11:]) :
                with open(File_Dir,'w',newline="",encoding="utf-8") as temp:
                    temp.writelines(rows[:-1])
                with open(File_Dir,"a",newline='',encoding="utf-8") as ID_File2:
                    write=csv.writer(ID_File2,delimiter=",")
                    write.writerow([date.today().strftime("%d/%m/%Y"),int(Current_Price)])
        elif len(rows)>=2 and Current_Price > int(str(rows[-1])[11:]):
            pass
        else:
            with open(File_Dir,"a",newline='',encoding="utf-8") as ID_File2:
                write=csv.writer(ID_File2,delimiter=",")
                write.writerow([date.today().strftime("%d/%m/%Y"),int(Current_Price)])
    print('Saved Prices of ',File_Name)
def Scraper_Fun(URL):
    scraper=cloudscraper.create_scraper()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    req=scraper.get(URL,headers=headers)
    bsoup = BeautifulSoup(req.text,"html.parser")
    if req.status_code!=200:
        pass
    else:
        if("amazon" in req.url):
            Amazon_Link(bsoup)
        elif "flipkart" in req.url:
            Flipkart_Link(bsoup)

with open(os.path.join(os.path.split(os.path.dirname(__file__))[0], 'Scraper_List.csv'),"r") as SL:
    Details=csv.reader(SL)
    next(Details,None) #Skip initial Headers
    for Product in Details:
        Product_ID,Last_Price,Target_Price,Email,URL=Product 
        Current_Price=0
        Scraper_Fun(URL)
        if Current_Price < int(Target_Price):
            pass
        elif Current_Price < int(Last_Price):
            pass
        else:
            pass
        Save_Details(Current_Price)
        time.sleep(random.randint(7,12))


