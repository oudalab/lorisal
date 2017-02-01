from peewee import *

DATABASE = './data/repos.db'

db = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = db


class Repository(BaseModel):
    name = CharField(unique=True)
    url = CharField()
    description = TextField(null=True)
    last_scraped = TimestampField()


class Book(BaseModel):
    repository = ForeignKeyField(Repository, related_name='books')
    title = CharField()
    uuid = CharField()
    mods_metadata = TextField(null=True)


class Page(BaseModel):
    book = ForeignKeyField(Book, related_name='pages')
    name = CharField()
    page_number = IntegerField()
    ocr_text = TextField(null=True)
    uuid = CharField()
    images_detected = BooleanField(default=False)
    full_size_downloaded = BooleanField(default=False)


class ExtractedImage(BaseModel):
    page = ForeignKeyField(Page, related_name='extracts')
    image_id = IntegerField()
    tags = TextField(null=True)
    label = TextField(null=True)
    page_coordinate_TL = IntegerField(null=True)
    page_coordinate_TR = IntegerField(null=True)
    page_coordinate_BL = IntegerField(null=True)
    page_coordinate_BR = IntegerField(null=True)

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
