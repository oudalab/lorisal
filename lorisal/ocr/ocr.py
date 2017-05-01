from PIL import Image

import pyocr
import pyocr.builders
import os

# TODO: REWRITE THIS CODE! ReWritten after losing original file.

def ocrRepo(database, repository, models):

    images_path = os.path.join(
                    os.getcwd(),
                    "data",
                    repository.shortname
                )

    tool = state_OCR_tool()


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