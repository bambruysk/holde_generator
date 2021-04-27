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

class Holde():
    def __init__(self, name, num, neighbours, corrupt, label):
        self.name = name 
        self.num = num
        self.neighbours = neighbours
        self.corrupt = corrupt
        self.label =  label


    def renderToFile(self, filename = ""):
        if not name:
            filename = self.name 
            im = Image.open("template.jpg")
        
        draw = ImageDraw.Draw(im)
        fnt = ImageFont.truetype("20351.otf", 120)
        draw.text((100,100), "Поместье", font=fnt, fill=(255,255,255,255))

        with open(filename, "wb") as res:
            im.save(res, "JPEG")


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

#    saveFileToGD("result.jpg")


# if __name__ == 'main':
#     main()

main()