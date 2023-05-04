import cloudscraper
from bs4 import BeautifulSoup
import csv, os, time, random, smtplib, json
from datetime import date, datetime
from email.message import EmailMessage

#creating scrapers list to prevent anti spam detection
scrapers=[]
for i in range(int(os.getenv('S_Count',default=30))):
    scrapers.append(cloudscraper.create_scraper())

#--Mailing--
def SendMails(Product_Name,Product_Image,Current_Price,Target_Mail):
    with smtplib.SMTP(os.getenv('MServer',default='smtp.office365.com'),os.getenv('MPort',default='587')) as smtp:
        print('Mailing Started to '+Target_Mail)
        smtp.starttls()
        smtp.login(os.getenv('Mail'),os.getenv('MPass'))
        print('Mail Signed in with '+os.getenv('Mail'))
        MainMsg=EmailMessage()
        MainMsg['Subject']=f'Price Drop @{Current_Price} {Product_Name}#'
        MainMsg['From']=os.getenv('Mail')
        MainMsg['To']=Target_Mail
        
        #Html Markup for Email Body
        MailBody=f"""\
                    <!DOCTYPE html>
                    <html>
                    <body>
                    <h1 style="text-align:center"><a href="{Product_Image}"><img alt="" src="{Product_Image}" style="border-style:solid; border-width:3px; float:left; height:679px; width:679px" /></a><span style="font-family:Georgia,serif"><span style="font-size:26px"><strong>{Product_Name}</strong></span></span></h1>
                    <h2><span style="color:#16a085"><span style="font-family:Georgia,serif"><strong><span style="font-size:22px">Current Price:&nbsp;{Current_Price}</span></strong></span></span></h2>

                    <p><span style="color:#e67e22"><span style="font-family:Georgia, serif"><span style="font-size:22px"><strong>Previous Price:&nbsp;{Last_Price}</strong></span></span></span></p>
                    <p><span style="color:#e67e22"><span style="font-family:Georgia, serif"><span style="font-size:22px"><strong>Target Price:&nbsp;{Target_Price}</strong></span></span></span></p>

                    <p>&nbsp;</p>

                    <p style="text-align:center"><span style="font-size:14px"><span style="font-family:Comic Sans MS,cursive">Made with&nbsp;❤️</span></span></p>

                    <p style="text-align:center"><a href="https://price-check.onrender.com"><span style="font-size:14px">Price Tracker</span></a></p>

                    <p style="text-align:center">&nbsp;</p>

                    </body>
                    </html>
                    """
        MainMsg.add_alternative(MailBody,subtype='html')
        smtp.send_message(MainMsg)
        print('Mailed Results to '+Target_Mail)
        print(" Mail Sent To:"+Target_Mail+" - "+str(datetime.now()))

#for Scraping Details From Amazon
def Amazon_Link(bsoup):
    global Current_Price ,Product_Name, Product_Image
    if not None == bsoup.find('div',id="availability").text:
        Current_Price=bsoup.find_all('span',class_="a-offscreen")[0].text
        Current_Price=int(Current_Price[1:-3].replace(',',''))
    else:
        Current_Price=0

    Product_Name=bsoup.find("span",id="productTitle").text.strip()
    Product_Images=json.loads(bsoup.find('div',id="imgTagWrapperId").img['data-a-dynamic-image'])
    Product_Image=list(Product_Images.keys())[list(Product_Images.values()).index(max(Product_Images.values()))]

#for Scraping Details From Flipkart
def Flipkart_Link(bsoup):
    global Current_Price ,Product_Name, Product_Image
    Current_Price=int(bsoup.find("div",class_="_30jeq3 _16Jk6d").text[1:].replace(',','').replace('.00',''))
    Product_Name=bsoup.find("h1",class_="yhB1nd").text
    if "None" == bsoup.find("div",class_="_16FRp0") or "None" == bsoup.find("div",class_="_1dVbu9"):
        Current_Price=0
    Product_Image=bsoup.find("img",class_="_396cs4 _2amPTt _3qGmMb").attrs["src"]

#For Saving Latest Prices
def Save_Details(Current_Price):
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

#Scraping
def Scraper_Fun(URL):
    scraper=random.choice(scrapers)
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

#Checking all the Products For Fluctuations
ReWrite=[]
with open(os.path.join(os.path.split(os.path.dirname(__file__))[0], 'Scraper_List.csv'),"r") as SL:
    Details=csv.reader(SL)
    next(Details,None) #Skip initial Headers
    for Product in Details:
        Product_Details=Product
        Product_ID,Last_Price,Target_Price,Target_Mail,URL=Product_Details[0], int(Product_Details[1]) ,int(Product_Details[2]) ,Product_Details[3],Product_Details[4]
        Current_Price=0
        Product_Name=''
        Product_Image=''
        Scraper_Fun(URL)
        print("Comparing ",Current_Price,Target_Price,Product_ID)
        if Current_Price < int(Target_Price):
            #SendMails(Product_Name,Product_Image,Current_Price,Target_Mail)
            print("Price Drop Alerted\n")
        if Current_Price < int(Last_Price):
            #SendMails(Product_Name,Product_Image,Current_Price,Target_Mail)
            print("Price Drop Alerted\n")
            Product[1]=int(Current_Price)
        ReWrite.append([Product_ID,Current_Price,Target_Price,Target_Mail,URL])
        Save_Details(Current_Price)
        t=random.randint(7,10)
        print('Waiting ',t,' Seconds')
        time.sleep(t)

#ReWriting all the Latest Data
with open(os.path.join(os.path.split(os.path.dirname(__file__))[0], 'Scraper_List.csv'),"w",newline="") as File_Mod:
    writer=csv.writer(File_Mod)
    writer.writerow(["Product_ID","Last_Price","Target_Price","Email","Url"])
    for ReWriteRows in ReWrite:
        writer.writerow([ReWriteRows[0],int(ReWriteRows[1]),int(ReWriteRows[2]),ReWriteRows[3],ReWriteRows[4]])
    print("CSV: Latest Price Updated in CSV")