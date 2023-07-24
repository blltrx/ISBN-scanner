from pyzbar import pyzbar
import cv2
import requests
import csv
from time import sleep


def infomation(isbn: str) -> list:
    url = f"https://openlibrary.org/isbn/{isbn}.json"
    print(f"FETCHING DATA AT {url}")

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        authornames = [""]
        publisher = ""
        title = data["title"]
        try:
            [publisher] = data["publishers"]
            authorsdict = data["authors"]
        
            authornames = []

            for author in authorsdict:
                key = author["key"]
                url = f"https://openlibrary.org/{key}.json"
                response = requests.get(url)
                data = response.json()
                name = data["name"]
                authornames.append(name)
        except KeyError as excp:
            print(f"could not fetch data for publisher and/or author for {isbn} : {excp}")

        return [title, publisher, authornames[0]]
    return []


def create_infolist(barcodes: list) -> list:
    infomationlist = []
    for barcode in barcodes:
        if barcode[1] == "EAN13":
            code = str(barcode[0].decode("utf-8"))
            info = infomation(code)
            info.append(barcode[2])
            print(info)
            infomationlist.append([info])
    return infomationlist


def write_csv(infomationlist: list) -> None:
    print(f"WRITING TO CSV")
    with open("output.csv", 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["name", "publisher", "author one", "quantity"])
        for i in infomationlist:
            csvwriter.writerows(i)

def find(data, type, barcodes):
    for ind, i in enumerate(barcodes):
        if data == i[0] and type == i[1]:
            return ind
    return False

def main() -> None:
    vid = cv2.VideoCapture(0)
    barcodes = []
    while(True):
        result, frame = vid.read()

        cv2.imshow('frame', frame)
        obj = pyzbar.decode(frame)

        if obj != []:
            barcode = obj[0]
            data = barcode.data
            codetype = barcode.type
            ind = find(data, codetype, barcodes)

            if type(ind) == bool:
                print(f"SCANNED : {data, codetype}")
                barcodes.append([data, codetype, 1])
                sleep(2) # seconds

            elif type(ind) == int:
                print(f"SCANNED : {data, codetype} AGAIN")
                barcodes[ind][2] += 1
                sleep(2) # seconds

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        

    vid.release()
    cv2.destroyAllWindows()

    infomationlist = create_infolist(barcodes)

    write_csv(infomationlist)


if __name__ == "__main__":
    main()
