import os
from subprocess import check_output
import re

WRITE_LABELS = False

def run_classification(inputFiles):
    class_list = []
    for fil in inputFiles:
        imageObject = {}
        imageObject["filepath"] = fil
		
        classification_output = check_output('bazel-bin/im2txt/run_inference  --checkpoint_path=../../model/model.new.ckpt-2000000   --vocab_file=../../model/word_counts2.txt   --input_files=' + fil, shell=True)	

        captions = []
        p = re.compile("\d\) ([\w\s]+)")
        for match in re.findall(p, str(test)):
            captions.append(match)

        imageObject["captions"] = captions

        class_list.append(imageObject)

    return class_list

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
