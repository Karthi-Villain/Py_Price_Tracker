import cloudscraper
from bs4 import BeautifulSoup
import streamlit as st
import json, math, csv, random, os
import pandas as pd

st.set_page_config(page_title="Price Tracker",layout="centered")
st.header("Price Tracker")

URL=st.text_input(label="Enter URL: ",placeholder="Enter Amazon/Flipkart Product Link")

#creating scrapers list to prevent anti spam detection
scrapers=[]
for i in range(int(os.getenv('S_Count',default=30))):
    scrapers.append(cloudscraper.create_scraper())

#Removing Streamlit Footers
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

#Helps to Display the Graps if Data Collected
def Show_Graph(Product_ID):
    try:
        FileDir=f"./Details/{Product_ID}.csv"
        df = pd.read_csv(FileDir, parse_dates=['date'],dayfirst=True)
        with open(FileDir,'r')as f:
            GraphTitle=f'Price From {len(f.readlines())-1} Days'
        st.subheader(GraphTitle)
        st.line_chart(df.set_index('date'))
        st.set_option('deprecation.showPyplotGlobalUse', False)
    except Exception as e:
        print(str(e))

#Html Markdown for displaying The Details
def Display_Results(Product_Name,Current_Price,Actual_Price,Delivary_Details,Reviews,Off_Percentage,Product_Image,Product_ID):
    col1,col2=st.columns(2)
    with col1:
        with st.container():
            st.image(Product_Image,width=300)
            st.markdown(f'''<p><span style="font-family:Lucida Sans Unicode,Lucida Grande,sans-serif"><strong><span style="color:#d35400">-{Off_Percentage}%</span><span style="color:#e74c3c">&nbsp;</span><span style="font-size:20px">{Current_Price}</span></strong></span></p>''',unsafe_allow_html=True)
            st.write(Reviews)
    with col2:
        with st.container():
            st.subheader(Product_Name)
            st.write(f'''<h2><span style="font-family:Georgia,serif"><span style="font-size:14px"><strong><span style="color:#009900">Current Price:</span></strong> </span><span style="font-size:20px">{Current_Price}</span></span></h2>

<h2><span style="font-family:Georgia,serif"><span style="font-size:14px"><strong><span style="color:#f1c40f">Actual Price:</span></strong> </span><span style="font-size:20px">{Actual_Price}</span></span></h2>''',unsafe_allow_html=True)
            st.write(Delivary_Details)
    st.markdown("""<p style="text-align:center"><strong>Made With&nbsp;❤️</strong></p>""",unsafe_allow_html=True)
    Show_Graph(Product_ID)

#Fetchs Last Day Price
def Get_Last_Day_Price(FileName):
    try:
        with open(FileName,'r') as Data:
            Lines=Data.readlines()
            Last_Price=Lines[-1].split(",")[1]
        return int(Last_Price)
    except:
        return 0
    
#For Saving User Alerts in Scraper_List.csv file
def Save_Details(Current_Price,Product_ID,FUrl):
    Target_Price=int(st.number_input("Enter Your Target Price: ",max_value=int(Current_Price[1:].replace(',','').replace('.00','')),min_value=0,value=int(Current_Price[1:].replace(',','').replace('.00',''))-1))
    coll1,coll2=st.columns([4,1])
    with coll1:
        Email=st.text_input("Enter Email Address:")
    with coll2:
        saveBtn=st.button("Get Alerts")
    if URL and saveBtn:
        with open("Scraper_List.csv",'r') as CsvObj:
            rows=csv.reader(CsvObj,delimiter=',')
            #Headers= Product_ID,LastPrice,Target_Price,RecipientMail,Url
            Already_Exist=False
            for row in rows:
                if Product_ID in row:
                    if Target_Price != int(row[2]) or Email not in row:
                        Already_Exist=False
                    else:
                        Already_Exist=True
                    
            if(Already_Exist==False):
                with open("Scraper_List.csv",'a',newline='',encoding="utf-8") as NewCsv:
                    writer = csv.writer(NewCsv,delimiter=",")
                    writer.writerow([Product_ID,int(Current_Price[1:].replace(',','').replace('.00','')),Target_Price,Email,FUrl])
                    st.success("New Allert is added.")
        
#Getting Unique Product ID for Storing Its Prices over Dates
def Get_Product_ID(FUrl):
    if ('amzn' in str(FUrl) or 'amazon' in str(FUrl)):
        if('dp/' in str(URL)):
            return FUrl[FUrl.find("dp/")+3:FUrl.find("dp/")+13]
        else:
            return FUrl[FUrl[FUrl.find("gp/product/")+11:FUrl.find("gp/product/")+21]]
    elif "flipkart" in FUrl:
        return FUrl[FUrl.index("/itm")+1:FUrl.index("/itm")+17]


#for Scraping all the required Details 
def Do_Scrape(URL):
    Progress=st.progress(15)
    scraper=random.choice(scrapers)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    Progress.progress(30)
    req=scraper.get(URL,headers=headers)
    Progress.progress(60)

    if req.status_code==200:
        st.success("Scraping")
    else:
        st.warning("Failed to Scrape Your Product\nCheck the Given Link.")

    bsoup = BeautifulSoup(req.text,"html.parser")
    try:
        if('amzn' in req.url or 'amazon' in req.url):
            Progress.progress(80)
            Product_Name=bsoup.find("span",id="productTitle").text.strip()
            if "In stock" in bsoup.find('div',id="availability").text:
                Current_Price=bsoup.find_all('span',class_="a-offscreen")[0].text
                Actual_Price=bsoup.find('span',class_="a-size-small a-color-secondary aok-align-center basisPrice").find("span",class_="a-offscreen").text
                Off_Percentage=math.floor(100-(int(Current_Price[1:-3].replace(',',''))/int(Actual_Price[1:].replace(',','')))*100)
            else:
                Current_Price=0
                Actual_Price=0
                Off_Percentage=0
            Delivary_Details=bsoup.find('div',id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE").text.strip()
            Reviews=bsoup.find("a",class_="a-popover-trigger a-declarative").text.strip()
            Product_Images=json.loads(bsoup.find('div',id="imgTagWrapperId").img['data-a-dynamic-image'])
            Product_Image=list(Product_Images.keys())[list(Product_Images.values()).index(max(Product_Images.values()))]
            Product_ID=Get_Product_ID(req.url)
            Progress.progress(100)
            if 'dp/' in req.url:
                FUrl=req.url[:req.url.find('dp/')+13]
            else:
                FUrl=req.url[:req.url.find("gp/product/")+21]
            Display_Results(Product_Name,Current_Price,Actual_Price,Delivary_Details,Reviews,Off_Percentage,Product_Image,Product_ID)
            Save_Details(Current_Price,Product_ID,FUrl)
        elif "flipkart" in str(req.url):
            Progress.progress(80)
            Product_Name=bsoup.find("h1",class_="yhB1nd").text
            if not "None" == bsoup.find("div",class_="_16FRp0") or "None" == bsoup.find("div",class_="_1dVbu9"):
                Delivary_Details=bsoup.find("div",class_="_3XINqE").text[:-4]
            else:
                Current_Price=0
                Actual_Price=0
                Off_Percentage=0
                Delivary_Details="Currently Unavailable!"
            Current_Price=bsoup.find("div",class_="_30jeq3 _16Jk6d").text
            Actual_Price=bsoup.find("div",class_="_3I9_wc _2p6lqe").text
            Off_Percentage=bsoup.find("div",class_="_3Ay6Sb _31Dcoz").text[:-5]
            Reviews=bsoup.find("div",class_="_3LWZlK").text+" "+bsoup.find("span",class_="_2_R_DZ").text   
            Product_ID=Get_Product_ID(req.url)
            Product_Image=bsoup.find("img",class_="_396cs4 _2amPTt _3qGmMb").attrs["src"]
            FUrl=req.url[:req.url.find("/itm")+17]
            Progress.progress(100)
            Display_Results(Product_Name,Current_Price,Actual_Price,Delivary_Details,Reviews,Off_Percentage,Product_Image,Product_ID)
            Save_Details(Current_Price,Product_ID,FUrl)
        else:
            st.write("Site not Supported Yet")
    except:
        st.warning('Try After Some Time')

if URL:
    Do_Scrape(URL)