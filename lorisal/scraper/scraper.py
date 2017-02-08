from bs4 import BeautifulSoup
import urllib
import urllib.request
import requests
import time
import os
import xmltodict

# TODO: Should this just be defined inline?
BOOKLISTURL = "https://repository.ou.edu/islandora/object/oku%253Ahos?page="

# TODO: Can we move urllib to using requests?

SCRAPE_BOOKLIST = False
DOWNLOAD_THUMBS = True


def scrapeRepo(database, repository, models):

    images_path = os.path.join(
                    os.getcwd(),
                    "data",
                    repository.shortname
                )

    # TODO: Setup logging for some of these print statements!
    print("Image Save Path:")
    print(images_path)

    imgurl_pre = "https://repository.ou.edu/adore-djatoka/"
    imgurl_pre += "resolver?rft_id=https://repository.ou.edu/uuid/"

    imgurl_post = "/datastream/JP2/view&url_ver=Z39.88-2004"
    imgurl_post += "&svc_id=info:lanl-repo/svc/getRegion"
    imgurl_post += "&svc_val_fmt=info:ofi/fmt:kev:mtx:jpeg2000"
    imgurl_post += "&svc.format=image/jpeg&svc.rotate=0&svc.level="

    if SCRAPE_BOOKLIST:
        print("Start Scrape Booklist")
        booklist = scrapeBookList(BOOKLISTURL)
        booksInRepo = [book.uuid for book in models.Book.select()]

        for book in booklist:
            if book["uuid"] not in booksInRepo:
                print(book["uuid"])
                models.Book.create(
                    repository=repository,
                    full_title=book['full_title'],
                    uuid=book['uuid'],
                    mods_metadata=getBookMODSmetadata(book['uuid']),
                    pages_scraped=False
                )

    book_url_prefix = "https://repository.ou.edu/uuid/"
    book_url_suffix = "/pages?page="
    query = models.Book.select().where(models.Book.pages_scraped == False)
    print("Start Book Page Scrape")
    for book in query:
        print(book.full_title)

        pages = scrapeBook(book_url_prefix + book.uuid + book_url_suffix)

        # If no pages, delete book, else, create Page for each page.
        if not len(pages):
            book.delete_instance()
            print("book deleted")
        else:
            for page in pages:
                print(page['label'])
                models.Page.create(
                    book=book,
                    label=page['label'],
                    page_number=page['page_number'],
                    uuid=page['uuid'],
                    thumbs_downloaded=False
                )

            book.pages_scraped = True
            book.save()


    if DOWNLOAD_THUMBS:
        print("Start Thumb Scrape")
        imgurl_zoom = 2
        imgurl_params = (imgurl_pre, imgurl_post, imgurl_zoom)

        query = models.Page.select().where(
             models.Page.thumbs_downloaded == False
        )
        for page in query:

            keepcharacters = (' ', '.', '_')
            book_title = "".join(
                c for c in page.book.full_title
                if c.isalnum() or c in keepcharacters).rstrip()

            print(book_title + "/" + page.uuid)
            book_path = os.path.join(
                            images_path,
                            book_title
                        )

            if scrapePage(imgurl_params, page.uuid, book_path):
                page.thumbs_downloaded = True
                page.save()
            else:
                print("Save Error.")
    return


def scrapeBookList(url):
    bookList = []
    pageNum = 0
    while True:
        soup = BeautifulSoup(urllib.request.urlopen(url + str(pageNum)), "lxml")
        for thumb in soup.select(".islandora-basic-collection-thumb > a"):
            uuid = thumb["href"]
            uuid = uuid[6:]
            book = {"full_title": thumb["title"], "uuid": uuid}
            bookList.append(book)

        if soup.find("a", text="next"):
            time.sleep(0.1)
            pageNum += 1
        else:
            return bookList


def getBookMODSmetadata(uuid):
    modurl_prefix = "https://repository.ou.edu/uuid/"
    modurl_suffix = "/datastream/MODS/download"
    xml_meta = requests.get(modurl_prefix + uuid + modurl_suffix)

    # Convert xml to a json
    metadata = xmltodict.parse(xml_meta.text)

    return metadata


def scrapeBook(url):
    print("scraping book...")
    pageList = []
    pageNum = 0
    pageOfBook = 1
    while True:
        soup = BeautifulSoup(urllib.request.urlopen(url + str(pageNum)), "lxml")
        for thumb in soup.select(".islandora-object-thumb > a"):
            uuid = thumb["href"]
            uuid = uuid[6:]
            print(uuid)
            page = {
                "label": thumb["title"],
                "uuid": uuid,
                "page_number": pageOfBook
            }
            pageList.append(page)
            pageOfBook += 1

        if soup.find("a", text="next"):
            time.sleep(0.1)
            pageNum += 1
        else:
            return pageList


def scrapePage(url_params, uuid, book_path):

    page_path = os.path.join(book_path, str(url_params[2]))

    if not os.path.exists(page_path):
        os.makedirs(page_path)

    image_path = os.path.join(page_path, uuid)
    print(image_path)

    url = url_params[0] + uuid + url_params[1] + str(url_params[2])
    print(url)
    r = requests.get(url)
    if r.status_code == 200:
        with open(image_path+".jpg", 'wb') as f:
            f.write(r.content)
            return 1
    else:
        return 0


def scrapePageOld(url, imgurl_params, pageNum):
    soup = BeautifulSoup(urllib.urlopen(url + str(pageNum)), "lxml")

    for thumb in soup.select(".islandora-basic-collection-thumb > a"):
        escapedName = thumb["title"].replace(" ", "-")
        newimagepath = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "images",
            escapedName)
        if not os.path.exists(newimagepath):
            os.makedirs(newimagepath)

        scrapeBook(
            "https://repository.ou.edu" + thumb["href"] + "/pages?page=",
            0,
            escapedName
        )
        print("Scraping page of books")

    if soup.find("a", text="next"):
        time.sleep(3)
        print("Found next page of books")
        pageNum += 1
        scrapePage(url, pageNum)


def scrapeBookOld(url, pageNum, bookName, imgurl_params):
    soup = BeautifulSoup(urllib.urlopen(url + str(pageNum)), "lxml")
    imgurl_pre = imgurl_params[0]
    imgurl_post = imgurl_params[1]
    imgurl_post += imgurl_params[2]

    for thumb in soup.select(".islandora-object-thumb > a"):
        title = thumb["title"].replace(" ", "-")
        # child = thumb.findChildren()[0]
        thumbUrl = imgurl_pre+thumb["href"]+imgurl_post
        print("Scraping /images/" + bookName + "/" + title + ".jpg")
        urllib.urlretrieve(
            thumbUrl,
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         "images",
                         bookName,
                         title + ".jpg"
                         )
        )
        # print thumbUrl

    if soup.find("a", text="next"):
        time.sleep(1)
        print("Found next page")
        pageNum += 1
        scrapeBook(url, pageNum, bookName)


# def scrapePage(uuid, url_pre, url_post, zoom=0, title="image", bookName="misc"):
# urllib.urlretrieve(thumbUrl, os.path.join(os.path.dirname(os.path.realpath(__file__)), "images", bookName, title + ".jpg"))
