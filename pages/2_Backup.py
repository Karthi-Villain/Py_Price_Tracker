from mediafire import MediaFireApi
from mediafire import MediaFireUploader
from datetime import date
import zipfile
import os
import streamlit as st

def zipdir(path, ziph):
    # ziph is zipfile handle
    print(path)
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))
            print(os.path.join(root, file))

directory=os.path.join(os.getcwd(),'Details')
zipf = zipfile.ZipFile('Backup.zip', 'w', zipfile.ZIP_DEFLATED)
zipdir(directory, zipf)
zipf.write(os.path.join(os.getcwd(),'Scraper_List.csv'))
print(os.getcwd(),"\Scraper_List.csv")
zipf.close()

api = MediaFireApi()
uploader = MediaFireUploader(api)
session = api.user_get_session_token(
    email=os.getenv("Mediafire_Mail"),
    password=os.getenv("Mediafire_Pass"),
    app_id='42511')

api.session = session
response = api.user_get_info()
fd = open(os.path.join(os.getcwd(),'Backup.zip'), 'rb')
FileName=str(date.today().strftime("%d/%m/%Y")).replace('/','_')+'_Bac.zip'
result = uploader.upload(fd, FileName,
                         folder_key='fufvr27uasdbn')

print(result)
ArchiveData=open("./Backup.zip","rb")
st.download_button("Download Data",data=ArchiveData,file_name=FileName)