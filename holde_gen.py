from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload,MediaFileUpload
from googleapiclient.discovery import build
import pprint
import io
import sys

from PIL import Image, ImageDraw, ImageFont


pp = pprint.PrettyPrinter(indent=4)
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'client_secret.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=credentials)

# results = service.files().list(pageSize=10,
#                                fields="nextPageToken, files(id, name, mimeType)").execute()

# pp.pprint(results)

def getTemplate ():
    print(" Start getting file")
    results = service.files().list(pageSize=10,
                               fields="nextPageToken, files(id, name, mimeType)").execute()
    
    pp.pprint(results)

    file_id = '1kj-_IyuJVBc8nHgIZhN5G9VHcHYghGUu'
    request = service.files().get_media(fileId=file_id)
    filename = 'template.jpg'
    fh = io.FileIO(filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print ("Download %d%%." % int(status.progress() * 100))

    fh.close()

def saveFileToGD(filename):
    folder_id = '1O5psqszvUq-qG8ZwEFjS7nHnNLQiMJXw'
    name = filename
    file_path = filename
    file_metadata = {
                    'name': name,
                    'parents': [folder_id]
                }
    media = MediaFileUpload(file_path, resumable=True)
    r = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    pp.pprint(r)

location_list = ["Вольные", "Актлан", "Порт-Фаро", "Новый Уотердип" ]


class Holde():
    def __init__(self, name, num, neighbours, corrupt, label):
        self.name = name 
        self.num = num
        self.neighbours = neighbours
        self.corrupt = corrupt
        self.label =  label
        self.im = Image.open("template.jpg")
        self.draw = ImageDraw.Draw(self.im)
        self.header_font = ImageFont.truetype("18700.ttf", 100)
        self.name_font = ImageFont.truetype("18700.ttf", 130)
        self.regular_fnt = ImageFont.truetype("18700.ttf", 80)
        self.width = 2560
        self.height = 1777

    def renderHeader(self):
        self.draw.text((self.width/2,300), "Поместье  " + str(self.num) , font=self.header_font,fill=(0,0,0,255), align='center', anchor="ms")
        self.draw.text((self.width/2,450), str(self.name) , font=self.name_font,fill=(0,0,0,255), align='center', anchor="ms")
    
    def renderNeighs(self):
        neigbours_list   =  "\n".join(self.neighbours)
        self.draw.multiline_text((self.width*0.85,800), "Соседи: \n" +  neigbours_list, spacing=6, font= self.regular_fnt,fill=(0,0,0,255), align='right', anchor="rs")
 
    def renderCorrupt(self):
        self.draw.multiline_text((self.width*0.15,800), "Влияние : \n" +  "\n".join([f"{l}: {c} %" for l,c in zip(location_list, self.corrupt)]), font= self.regular_fnt,fill=(0,0,0,255), align='left', anchor="ls")
 



    def renderToFile(self, filename = ""):
        if not filename:
            filename = str(self.num) +"_" + self.name + ".jpg"
 
        
        #draw = ImageDraw.Draw(im)
        # fnt = ImageFont.truetype("20351.otf", 120)
        # draw.text((100,100), "Поместье", font=fnt, fill=(255,255,255,255))
        self.renderHeader()
        self.renderNeighs()
        self.renderCorrupt()

        with open(filename, "wb") as res:
            self.im.save(res, "JPEG")
        return filename


def main():
 #   getTemplate()
    im = Image.open("template.jpg")
    pp.pprint(im)
    #size=2560x1777
    width = 2560
    height =  1777
    draw = ImageDraw.Draw(im)
    fnt = ImageFont.truetype("20351.otf", 100)
    draw.text((width/2,300), "Поместье", font=fnt, fill=(0,0,0,255), align='center', anchor="ms")

    with open("result.jpg", "wb") as res:
        im.save(res, "JPEG")

    holde = Holde("Раменское",3,["Жуковский", "Бронницы"],[20,-30,40,10],"Шахта")
    holdef=  holde.renderToFile()

    #saveFileToGD("result.jpg")


# if __name__ == 'main':
#     main()

main()