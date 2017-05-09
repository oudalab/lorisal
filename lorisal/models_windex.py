from peewee import *
from playhouse.sqlite_ext import *

DATABASE = './data/repos_halfocr_windex.db'

db = SqliteExtDatabase(DATABASE, threadlocals=False)


class BaseModel(Model):
    class Meta:
        database = db


class Repository(BaseModel):
    name = CharField(unique=True)
    shortname = CharField(unique=True)
    url = CharField()
    description = TextField(null=True)
    last_scraped = TimestampField()

    def __unicode__(self):
        return self.shortname


class Book(BaseModel):
    repository = ForeignKeyField(Repository, related_name='books')
    full_title = CharField()
    title = CharField(null=True)
    uuid = CharField(unique=True, primary_key=True)
    mods_metadata = TextField(null=True)
    pages_scraped = BooleanField(default=False)

    def __unicode__(self):
        return self.full_title


class Page(BaseModel):
    book = ForeignKeyField(Book, related_name='pages')
    label = CharField(null=True)
    page_number = IntegerField()
    ocr_text = TextField(null=True)
    uuid = CharField(unique=True, primary_key=True)
    images_detected = BooleanField(null=True)
    full_size_downloaded = BooleanField(default=False)
    thumbs_downloaded = BooleanField(default=False)

    def __unicode__(self):
        return self.book.title[:25] + " - " + str(self.page_number)

class ExtractedImage(BaseModel):
    page = ForeignKeyField(Page, related_name='extracts')
    image_id = IntegerField()
    tags = TextField(null=True)
    label = TextField(null=True)
    page_coordinate_TL_x = IntegerField(null=True)
    page_coordinate_TL_y = IntegerField(null=True)
    page_coordinate_BR_x = IntegerField(null=True)
    page_coordinate_BR_y = IntegerField(null=True)

class FTSPage(FTSModel):
    page_uuid = CharField()
    ocr_text = TextField()

    class Meta:
        database = db


class FTSExtractedImage(FTSModel):
    extract_id = IntegerField()
    tags = TextField(null=True)
    label = TextField(null=True)

    class Meta:
        database = db


_tables = [Repository, Book, Page, ExtractedImage]


def build():
    db.connect()
    db.create_tables(_tables)
    db.close()


def rebuild():
    db.connect()
    db.drop_tables(_tables)
    db.close()
    build()
