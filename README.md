# LORISAL
### _Library Online Repository Image Scraper and Labeler_

Sequence of program can roughly be seen in ordering of "Todo's" below.

##Module descriptions
### 1. Scraper

This module is take as input necessary information about the Islandora repository. At first, this module will be
hardcoded to a specific repository. The tradeoff in flexibility here will allow us to more quickly get to implementing
other modules.

The scraper will save images in a directory structure in the /data/ folder and create an SQLite .db file that catalogs
the imagery. The first pass in the scraper will download all imagery at a thumbnail size, and the second usage will be
downloading full resolution imagery. The scraper will also extract whatever metadata it can about objects in the
repository.

_Libraries used_: Peewee for db, BeautifulSoup for scraping 

### 2. Image Identifier

This module will take an input an image file (ideally of thumbnail size) and identify it contains any pictures. That is,
 most of our imagery will be scans from books where most of the pages will not contain any imagery, just text.
 The presence of imagery will be noted in the database so that the main program can go back and know which pages of a 
 book need to be worked on, downloaded at full resolution, etc.

_Libraries used_: OpenCV, code from https://github.com/acdha/image-mining
### 3. Image Extractor

This module will identify the boundaries of imagery that needs to be extracted and isolated from the book scan. At this
point it's unclear whether it's necessary to save the extracted images to a discrete file in the data folder or to merely
write the corner coordinates to the db. (Extracting images could have other uses and also would make other modules not
need to do image processing, and since most pages in a book don't have imagery, the disk usage is probably negligible.)

_Libraries used_: OpenCV, code from https://github.com/acdha/image-mining

### 4. OCR and Knowledge Gathering

This module will take the page containing the extracted image and do optical character recognition on it
With the source text, we can search for images.
_Future_: Future work could use adjacent pages, use text summarizers, and use the coordinates for where text was detected to better refine image identification and extraction.

_Libraries used_: pyocr and Tesseract

### 5. Image Labeler

Using the previously identified objects (tags), metadata and knwowledge garnered by the OCR module, this module can take
the info that has been recorded in the db and attempt to create an english sentence describing the scene. This is very
much down the line and the workflow here could change significantly.

_Libraries used_: Tensorflow model img2txt

### 6. Searcher

This module will allow the user to search for imagery based on labels and OCR data. 
_Future_: Natural language search, filters based of book meta-data

_Libraries used_: Peewee's SQLiteExt package for Full Text Search

## TODOs:
- [x] Build basic skeleton for project
- [x] Implement thumbnail scraper
- [x] Implement SQLite models for repository data
- [x] Implement Image Identifier
- [x] Implement full-size image scraper
- [x] Implement Image Extractor (through either coordinates or saved image)
- [ ] Implement Image Labeler
- [x] Implement OCR (info in db, but need to rewrite the module)
- [ ] Implement Full Text Search on Labels and OCR content

