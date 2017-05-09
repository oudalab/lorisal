import os
from subprocess import check_output
import re

WRITE_LABELS = True

CHECKPOINT_PATH = "/home/eth/storage/models/im2txt/im2txt/data/downloaded_models/psycharo/model.ckpt-2000000"
VOCAB_FILE = "/home/eth/storage/models/im2txt/im2txt/data/downloaded_models/psycharo/word_counts2.txt"
RUN_INFERENCE_PATH = "/home/eth/storage/models/im2txt/bazel-bin/im2txt/run_inference"

# Larger Batches reduce number of times TF needs to load model into memory,
# but also makes "saving" progress to database less frequent and there is a
# limit to how many can be passed as args to the im2txt script
BATCH_SIZE = 100

def labelExtracts(database, repository, models):

    ExtractedImage = models.ExtractedImage

    images_path = os.path.join(
                    os.getcwd(),
                    "data",
                    repository.shortname
                )

    if WRITE_LABELS:
        keepcharacters = (' ', '.', '_')
        query = ExtractedImage.select()

        to_label = []

        for extractedImage in query:

            page = extractedImage.page
            book_title = "".join(
                c for c in page.book.full_title
                if c.isalnum() or c in keepcharacters).rstrip()

            book_path = os.path.join(
                            images_path,
                            book_title
                        )

            page_path = os.path.join(book_path, "extract")
            image_path = os.path.join(page_path, page.uuid) + "_"
            image_path += str(extractedImage.page_coordinate_TL_x) + "-"
            image_path += str(extractedImage.page_coordinate_TL_y) + "-"
            image_path += str(extractedImage.page_coordinate_BR_x) + "-"
            image_path += str(extractedImage.page_coordinate_BR_y) + ".jpg"

            if os.path.isfile(image_path):
                to_label.append((extractedImage.id, image_path))

        # Now call the Tensorflow code...
        for i in range(0, len(to_label), BATCH_SIZE):

            labels = run_classification_batch(to_label[i:i+BATCH_SIZE])

            print("Labelling through %d finished, writing to db..." % (i+BATCH_SIZE))
            for extract_id in labels:

                extractImage = ExtractedImage.get(ExtractedImage.id == extract_id)
                extractImage.label = str(labels[extract_id])
                extractImage.save()

                #  query = models.ExtractedImage.select().where(extract_id == models.ExtractedImage.id)
                #  for extractedImage in query:
                #      extractedImage.label = str(labels[extract_id])
                #      extractedImage.save()


def run_classification_batch(inputFiles):

    file_list = []
    id_list = []
    labels = {}

    p = re.compile("\d\) ([\w\s]+)")

    for extract_id, fil in inputFiles:
        file_list.append(fil)
        id_list.append(extract_id)
        labels[extract_id] = []

    for i in range(0, len(file_list), 100):
        classification_output = check_output(
            RUN_INFERENCE_PATH + " --checkpoint_path=" + CHECKPOINT_PATH +
            " --vocab_file=" + VOCAB_FILE + " --input_files=" +
            str(file_list[i:i+100])[1:-1].replace(", ", ",") + "",
            shell=True
        )

        img_output = classification_output.decode("utf-8").split("Captions for image")
        img_output = list(filter(None, img_output))

        for extract_id, img_out in zip(id_list, img_output):
            for match in re.findall(p, img_out):
                labels[extract_id].append(match)

    return labels
