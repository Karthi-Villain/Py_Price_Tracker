import cloudscraper
from bs4 import BeautifulSoup
import streamlit as st
import json, math, csv

st.set_page_config(page_title="Price Tracker",layout="centered")
st.header("Price Tracker")

URL=st.text_input(label="Enter URL: ")

BtnBool=False

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def Display_Results(Product_Name,Current_Price,Actual_Price,Delivary_Details,Reviews,Off_Percentage,Product_Image):
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
def Get_Last_Day_Price(FileName):
    try:
        with open(FileName,'r') as Data:
            Lines=Data.readlines()
            Last_Price=Lines[-1].split(",")[1]
        return int(Last_Price)
    except:
        return 0
    
    
def Save_Details(Current_Price,Product_ID):
    Target_Price=st.slider("Enter Your Target Price: ",max_value=int(Current_Price[1:-3].replace(',','')),min_value=0,value=int(Current_Price[1:-3].replace(',',''))-1)
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
                    Last_Price=0#Get_Last_Day_Price(FileName)
                    if Target_Price != int(row[2]) or Email not in row:
                        Already_Exist=False
                    else:
                        Already_Exist=True
                    
            if(Already_Exist==False):
                with open("Scraper_List.csv",'a',newline='',encoding="utf-8") as NewCsv:
                    writer = csv.writer(NewCsv,delimiter=",")
                    writer.writerow([Product_ID,0,Target_Price,Email,URL])
                    st.success("New Allert is added.")
        

def Get_Product_ID(FUrl):
    if ('amzn' in str(URL) or 'amazon' in str(URL)):
        if('amzn' in str(URL)):
            return FUrl[URL.find("dp/")+3:URL.find("dp/")+13]
        else:
            return FUrl[URL.find("dp/")+3:URL.find("dp/")+13]
    
def Do_Scrape(URL):
    Progress=st.progress(15)
    scraper=cloudscraper.create_scraper()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    Progress.progress(30)
    req=scraper.get(URL,headers=headers)
    Progress.progress(60)

    if req.status_code==200:
        st.success("Scraping")
    else:
        st.warning("Failed to Scrape Your Product\nCheck the Given Link.")

    bsoup = BeautifulSoup(req.text,"html.parser")
    if('amzn' in str(URL) or 'amazon' in str(URL)):
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

        Display_Results(Product_Name,Current_Price,Actual_Price,Delivary_Details,Reviews,Off_Percentage,Product_Image)
        Save_Details(Current_Price,Product_ID)

if URL:
    Do_Scrape(URL)