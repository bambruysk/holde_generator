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
holdes = {}



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
        if not force and corrupts[lsh.title]:
           continue
        if lsh.title == "Вольные":
            mx,my = map(int,m.split(","))
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
                    lsh.update_cell(x,y,corrs[y-1][x-1])
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



def getHoldes():
    sheet = sh.worksheet('Holdes')
    holdes_list =  sheet.get_all_records()
    for hold in holdes_list:
        holdes[hold.get('ID')] = hold 
    pp.pprint(holdes)
    return holdes


def getNeigbours(id):
    res = []
    holdesNum = int(settings.get('HoldeNums')) 
    sizeX, sizeY = int(settings.get('WorldSizeX')), int(settings.get('WorldSizeY'))  
    if id < 0 or id >= holdesNum : 
        return res
    #  0  1  2  3  4  5  6  7  8  9
    if id >= sizeX :
        res.append(id-sizeX)
	# 90 91 92 93 94 95 96 97 98 99
    if id < holdesNum-sizeX:  # 100 - 10 
        res.append(id+sizeX)
	# 00  10  20  30  40  50  60  70  80  90
    if id%sizeX != 0 :
        res.append( id-1)
	# 09 19 29 39 49 59 69 79 89 99
    if id%sizeX != sizeX-1 :    
        res.append( id+1)
    return res


def uppdateNeigbours():
    holde_sheet_header = sh.worksheet('Holdes').row_values(1)
    pp.pprint(holde_sheet_header)
    neigbour_col = holde_sheet_header.index('Соседи') + 1
    holdes = getHoldes()
    row = 2
    for id,hol in holdes.items():
        #id = hold.get('ID')
        heighlist = []
        neigh_ids = getNeigbours(int(id))
        for nid in neigh_ids:
            heighlist.append(holdes.get(nid).get('Name'))
        val = hol['Coceди'] = ",".join(heighlist)
        sh.worksheet('Holdes').update_cell(row,neigbour_col,val)
        row += 1
        print(val)
        time.sleep(1)





    


def main():
 #   getTemplate()
    pp.pprint(settings)
  #  fillCorrupt()

    getHoldes()
    #uppdateNeigbours()
    
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


