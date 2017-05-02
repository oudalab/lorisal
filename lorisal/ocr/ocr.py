from PIL import Image

import sys
import codecs
import pyocr
import pyocr.builders
import os

# TODO: TEST THIS CODE! ReWritten from notebooks after losing original file.

DELETE_EXISTING = False
SAVE_HOCR = True


def ocrRepo(database, repository, models):

    keepcharacters = (' ', '.', '_')
    images_path = os.path.join(
                    os.getcwd(),
                    "data",
                    repository.shortname
                )

    imgurl_zoom = 10
    tool = state_OCR_tool()

    query = models.ExtractedImage.select()

    for extractedImage in query:

        page = extractedImage.page

        book_title = "".join(
            c for c in page.book.full_title
            if c.isalnum() or c in keepcharacters).rstrip()

        book_path = os.path.join(
                    images_path,
                    book_title
                )
        page_path = os.path.join(book_path, str(imgurl_zoom))
        image_path = os.path.join(page_path, page.uuid)+".jpg"

        # TODO: Test if OCR exists in db
        ocrExists = False

        if ocrExists:
            if DELETE_EXISTING:
                # if the image has ocr info in db, rm it and hocr if exists.
                page.ocr_text = None
                # TODO: Delete hOCR file if exists
            else:
                continue

        meta = eval(page.book.mods_metadata)

        try:
            lang = meta["mods"]["language"][0]["languageTerm"]["#text"]
        except:
            try:
                lang = meta["mods"]["language"]["languageTerm"]["#text"]
            except:
                lang = "eng"

        # DO OCR AND SAVE TO page.
        line_and_word_boxes = tool.image_to_string(
                Image.open(image_path), lang=lang,
                builder=tool
        )

        txt = ""
        for line in line_and_word_boxes:
            txt += line.content

        page.ocr_text = txt
        page.save()

        if SAVE_HOCR:

            extract_path = os.path.join(book_path, "extract")
            hocr_path = os.path.join(extract_path, page.uuid)+".html"

            with codecs.open(
                        hocr_path, 'w', encoding='utf-8') as file_descriptor:
                    tool.write_file(file_descriptor, line_and_word_boxes)


def state_OCR_tool():
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)
    # The tools are returned in the recommended order of usage
    tool = tools[0]
    print("Will use tool '%s'" % (tool.get_name()))
    # Ex: Will use tool 'libtesseract'
    return tool


# The following are tools written for image detection tests, unused but
# could be useful for sanity checks later on.


def boxArea(coords):
    x1 = coords[0][0]
    x2 = coords[1][0]
    y1 = coords[0][1]
    y2 = coords[1][1]
    return (x2 - x1) * (y2 - y1)


def charsPerUnitArea(content, position):
    area = boxArea(position)
    chars = len(content)
    return chars/area


def box_intersect(a, b):
    # b is center, base. return percent of a inside b.
    a_area = box_area(a)

    x1 = max(min(a[0][0], a[1][0]), min(b[0][0], b[1][0]))
    y1 = max(min(a[0][1], a[1][1]), min(b[0][1], b[1][1]))
    x2 = min(max(a[0][0], a[1][0]), max(b[0][0], b[1][0]))
    y2 = min(max(a[0][1], a[1][1]), max(b[0][1], b[1][1]))

    if x1 < x2 and y1 < y2:
        return (((x2-x1) * (y2-y1)) / (a_area + 0.0))
    else:
        return 0.0


def box_area(a):
    a_width = (a[1][0] - a[0][0])
    a_height = (a[1][1] - a[0][1])
    a_area = a_width * a_height
    return a_area
