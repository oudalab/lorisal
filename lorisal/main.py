from scraper import scraper
import models

RUN_SCRAPER = True
REBUILD = True
BUILD = False


def main():

    # If we need to rebuild the models crudely, this will do so without altering
    # the tables, but will drop all tables and then create them anew. Otherwise
    # it'll just build the tables if they don't exist.
    if REBUILD:
        models.rebuild()
        repo = buildStructure()

    if BUILD:
        models.build()
        repo = buildStructure()

    db = models.db

    # Run scraper
    # For now I'll modify db inside of scraper, but in future it may be better
    # to have it be a generator object returning Named Tuples
    # where it returns info a book or page at a
    # time so that it isn't tied to this db structure.
    if RUN_SCRAPER:
        scraper.scrapeRepo(db, repo)


def buildStructure():

    ouhsc = models.Repository(
        name='OU History of Science Collection',
        url='https://repository.ou.edu/'
    )
    ouhsc.save()

    testStructures(ouhsc)

    return ouhsc


def testStructures(repository):

    testBook = models.Book.create(
        repository=repository,
        title="Test Book",
        uuid="testbookuuid"
    )

    testPage = models.Page.create(
        book=testBook,
        name="Test Page 1",
        page_number="1",
        uuid="testuuidpage1"
    )

    testImage = models.ExtractedImage.create(
        page=testPage,
        image_id=0
    )

    print(testImage.page.book.title)


def testQuerys(repository):
    return


if __name__ == '__main__':
    main()
