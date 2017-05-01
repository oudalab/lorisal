import os
import errno
from PIL import Image
from scraper.image_mining.figure_extraction import FigureExtractor
from scraper.image_mining.utils import open_image

FIND_FIGURES = False
REMOVE_PREVIOUSLY_FOUND = False
WRITE_EXTRACTED = True


def extractFigures(database, repository, models):

    images_path = os.path.join(
                    os.getcwd(),
                    "data",
                    repository.shortname
                )

    # TODO: Setup logging for some of these print statements!
    print("Image Save Path:")
    print(images_path)

    imgurl_zoom = 10

    if FIND_FIGURES:

        # Identify photos
        query = models.Page.select().where(
            models.Page.full_size_downloaded
        )

        for page in query:
            keepcharacters = (' ', '.', '_')
            book_title = "".join(
                c for c in page.book.full_title
                if c.isalnum() or c in keepcharacters).rstrip()

            # print(book_title + "/" + page.uuid)

            book_path = os.path.join(
                            images_path,
                            book_title
                        )

            page_path = os.path.join(book_path, str(imgurl_zoom))
            image_path = os.path.join(page_path, page.uuid)+".jpg"

            if REMOVE_PREVIOUSLY_FOUND:
                models.ExtractedImage.delete().where(
                    models.ExtractedImage.page == page
                ).execute()

            images_detected = embeddedImageExtraction(image_path, 9, 1)

            # TODO: CHECK IF PREVIOUSLY FOUND!
            for i, box_coord in enumerate(images_detected):
                embedded = models.ExtractedImage.create(
                    page=page,
                    image_id=i,
                    page_coordinate_TL_x=box_coord["x1"],
                    page_coordinate_TL_y=box_coord["y1"],
                    page_coordinate_BR_x=box_coord["x2"],
                    page_coordinate_BR_y=box_coord["y2"],
                )
                print(embedded.page_coordinate_TL_x)

            print(page.uuid + ' found ' + str(len(images_detected)) + " imgs.")
            page.save()

    # for page in query, save all extracted images.
    if WRITE_EXTRACTED:
        keepcharacters = (' ', '.', '_')
        query = models.ExtractedImage.select()

        i = 0

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

            saveImageExtraction(image_path, (
                extractedImage.page_coordinate_TL_x,
                extractedImage.page_coordinate_TL_y,
                extractedImage.page_coordinate_BR_x,
                extractedImage.page_coordinate_BR_y
            ))

            i += 1
            if i % 100 is 0:
                print("%d images written." % (i))
                print(page_path + image_path)

    return


def embeddedImageExtraction(image_path, erosion_size, dilation_size):

    params = {
        "canny_threshold": 0,  # No Luck Setting this at 1 or above
        "erosion_element": "rectangle",
        "erosion_size": erosion_size,  # Larger triggers more images
        "dilation_element": "rectangle",
        "dilation_size": dilation_size,  # Smaller Triggers more images
            }

    extractor = FigureExtractor(**params)

    try:
        base_name, source_image = open_image(image_path)
    except:
        print("Open Error for %s" % (image_path))
        pass

    boxes = []

    for bbox in extractor.find_figures(source_image):
        boxes.append(bbox.as_dict())

    return boxes


def saveImageExtraction(image_path, box_coords):

    TL_x, TL_y, BR_x, BR_y = box_coords

    save_path = image_path.replace("/10/", "/extract/")

    save_path = save_path[:-4] + "_" + str(TL_x) + "-" + str(TL_y)
    save_path += "-" + str(BR_x) + "-" + str(BR_y) + ".jpg"

    # print(save_path[:save_path.rfind("/")])

    try:
        os.makedirs(save_path[:save_path.rfind("/")], mode=0o777)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    im = Image.open(image_path)
    im = im.crop((TL_x, TL_y, BR_x, BR_y))
    im.save(save_path, "JPEG")

    return True
