from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload,MediaFileUpload
from googleapiclient.discovery import build
import pprint
import io
import sys

import gspread

from PIL import Image, ImageDraw, ImageFont
import time
import random


pp = pprint.PrettyPrinter(indent=4)
SCOPES = ['https://www.googleapis.com/auth/drive',  'https://www.googleapis.com/auth/spreadsheets']
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
        self.draw.multiline_text((self.width*0.85,700), "Соседи: \n" +  neigbours_list, spacing=6, font= self.regular_fnt,fill=(0,0,0,255), align='right', anchor="rs")
 
    def renderCorrupt(self):
        self.draw.multiline_text((self.width*0.15,700), "Влияние : \n" +  "\n".join([f"{l}:    {c} %" for l,c in zip(location_list, self.corrupt)]), font= self.regular_fnt,fill=(0,0,0,255), align='left', anchor="ls")
 
    def renderLabel(self):
        self.draw.text((self.width*0.85,200), str(self.label) , font=self.header_font,fill=(0,0,0,255), align='right', anchor="rs")
    


    def renderToFile(self, filename = ""):
        if not filename:
            filename = str(self.num) +"_" + self.name + ".jpg"
 
        
        #draw = ImageDraw.Draw(im)
        # fnt = ImageFont.truetype("20351.otf", 120)
        # draw.text((100,100), "Поместье", font=fnt, fill=(255,255,255,255))
        self.renderHeader()
        self.renderNeighs()
        self.renderCorrupt()
        self.renderLabel()

        with open(filename, "wb") as res:
            self.im.save(res, "JPEG")
        return filename

gc = gspread.authorize(credentials)
sh = gc.open('HoldeTest')    

def get_settings():
    sheet = sh.worksheet('Settings')
    rows =  sheet.get_all_values()
    settings = {}
    for row in rows :
        if row[0]:
            if row[0] != 'Locations' and row[0] != 'Main Holde' :
                settings[str(row[0])] = row[1] 
            else:
                settings[str(row[0])] = row[1:]
    return settings

settings = get_settings()
corrupts = {}


def fillCorrupt(force = False):
    #add shhet for each locations if it not exist

    locs  = settings.get('Locations')
    
    sizeX, sizeY = int(settings.get("WorldSizeX",12)),int(settings.get("WorldSizeY",12))
    
    for loc in locs:
        try:
            worksheet = sh.add_worksheet(
                title=loc, 
                rows=settings.get("WorldSizeX",12), 
                cols=settings.get("WorldSizeY",12)
            )
        except Exception as e:
            print("Sheet exist", e)

    loc_sheets = [sh.worksheet(loc) for loc in locs]
    main_holdes = settings.get('Main Holde')

    max_holde_val = 180

    for m, lsh in zip(main_holdes, loc_sheets) :
        corrupts[lsh.title] = lsh.get_all_values()
        if not force and corrupts[lsh.title][0][0]:
           continue
        if lsh.title == "Вольные":
            corrs = []
            for x in range(1,sizeX+1):
                corr = []
                for y in range(1,sizeY+1):
                    dx,dy = abs(x-mx),abs(y-my)
                    dist = max (dx,dy)
                    val = max_holde_val - dist*20
                    corr.append(val)
                random.shuffle(corr)
                corrs.append(corr)
            random.shuffle(corrs)
            corrupts[lsh.title] = corrs
            for x in range(1,sizeX+1):
                for y in range(1,sizeY+1):
                    lsh.update_cell(x,y,corrs[y][x])
                    time.sleep(1)            
            continue

        # corrupts[lsh.title] = lsh.get_all_values()
        # if not force and corrupts[lsh.title][0][0]:
        #    continue
        mx,my = map(int,m.split(","))
        for x in range(1,sizeX+1):
            for y in range(1,sizeY+1):
                dx,dy = abs(x-mx),abs(y-my)
                dist = max (dx,dy)
                val = max_holde_val - dist*20
                lsh.update_cell(x,y,val)
                time.sleep(1)
                print("x,y = ",  x,y, val, end= "")
            print()
        corrupts[lsh.title] = lsh.get_all_values()  



        






    


def main():
 #   getTemplate()
    pp.pprint(settings)
    fillCorrupt()
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

    saveFileToGD(holdef)


# if __name__ == 'main':
#     main()

main()


