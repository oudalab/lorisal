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

_Libraries likely used_: Peewee for db, BeautifulSoup for scraping 

### 2. Image Identifier

This module will take an input an image file (ideally of thumbnail size) and identify it contains any pictures. That is,
 most of our imagery will be scans from books where most of the pages will not contain any imagery, just text.
 The presence of imagery will be noted in the database so that the main program can go back and know which pages of a 
 book need to be worked on, downloaded at full resolution, etc.

_Libraries likely used_: OpenCV?
### 3. Image Extractor

This module will identify the boundaries of imagery that needs to be extracted and isolated from the book scan. At this
point it's unclear whether it's necessary to save the extracted images to a discrete file in the data folder or to merely
write the corner coordinates to the db. (Extracting images could have other uses and also would make other modules not
need to do image processing, and since most pages in a book don't have imagery, the disk usage is probably negligible.)

_Libraries likely used_: OpenCV

### 4. Tagger

This module will use ML techniques to identify objects in extracted imagery and then tag the image as such. Recording
not only the identified objects, but also their coordinates could be useful for identifying relationships of the objects
in the labeling stage, but more research is yet to be done here.

_Libraries likely used_: YOLO3000? Keras?

### 5. OCR and Knowledge Gathering

This module will take pages adjacent to an extracted image and try to do optical character recognition so we can use the
source text to better label the image. Text summarizers may be helpful here.

_Libraries likely used_: TBD

### 6. Image Labeler

Using the previously identified objects (tags), metadata and knwowledge garnered by the OCR module, this module can take
the info that has been recorded in the db and attempt to create an english sentence describing the scene. This is very
much down the line and the workflow here could change significantly.

_Libraries likely used_: TBD

### 7. Searcher

This module will allow the user to search for imagery based on tags, labels and OCR data. Maybe by this point we can
incorporate an english, full utterance style of search even if we want to be fancy.

_Libraries likely used_: TBD

## TODOs:
- [x] Build basic skeleton for project
- [ ] Implement thumbnail scraper
- [ ] Implement SQLite models for repository data
- [ ] Implement Image Identifier
- [ ] Implement full-size image scraper
- [ ] Implement Image Extractor (through either coordinates or saved image)
- [ ] Implement Object Recognition and Tagger
- [ ] Implement OCR, Summarizer, any knowledge gathering "external" of the image itself
- [ ] Implement Image Labeler

