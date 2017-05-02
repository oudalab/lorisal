import os

WRITE_LABELS = False


def labelExtracts(database, repository, models):

    images_path = os.path.join(
                    os.getcwd(),
                    "data",
                    repository.shortname
                )

    if WRITE_LABELS:
        keepcharacters = (' ', '.', '_')
        query = models.ExtractedImage.select()

        for i, extractedImage in enumerate(query):

            if i % 20 == 0:
                print("Starting label #%d" % (i))

            page = extractedImage.page
            book_title = "".join(
                c for c in page.book.full_title
                if c.isalnum() or c in keepcharacters).rstrip()

            book_path = os.path.join(
                            images_path,
                            book_title
                        )

            page_path = os.path.join(book_path, "extract")
            image_path = os.path.join(page_path, page.uuid)
            image_path += "_" + str(extractedImage.TL_x)
            image_path += "-" + str(extractedImage.TL_y)
            image_path += "-" + str(extractedImage.BR_x)
            image_path += "-" + str(extractedImage.BR_y) + ".jpg"

            if os.path.isfile(image_path):
                # call labeler function
                labels = []
                extractedImage.label = labels
                extractedImage.save()

    return
