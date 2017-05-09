import colorsys
# import imghdr
import os
import random

import numpy as np
from keras import backend as K
from keras.models import load_model
from PIL import Image, ImageDraw, ImageFont

from .models.keras_yolo import yolo_eval, yolo_head


FONT_PATH = "/home/eth/lorisal/lorisal/tagger/font/FiraMono-Medium.otf"
MODEL_PATH = "/home/eth/lorisal/lorisal/tagger/model_data/yolo.h5"
ANCHORS_PATH = "/home/eth/lorisal/lorisal/tagger/model_data/yolo_anchors.txt"
CLASSES_PATH = "/home/eth/lorisal/lorisal/tagger/model_data/coco_classes.txt"
SCORE_THRESHOLD = 0.3
IOU_THRESHOLD = 0.5

WRITE_TAGS = True

BATCH_SIZE = 100


def tagExtracts(database, repository, models):

    ExtractedImage = models.ExtractedImage

    images_path = os.path.join(
                    os.getcwd(),
                    "data",
                    repository.shortname
                )

    if WRITE_TAGS:
        # Setup of images to tag
        keepcharacters = (' ', '.', '_')
        query = ExtractedImage.select()

        to_tag = []

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
                to_tag.append((extractedImage.id, image_path))

        print("%d extracts to tag." % (len(to_tag)))

        # Prepare YOLO model using YAD2K

        print("Loading YOLO model...")
        model_path = MODEL_PATH
        assert model_path.endswith('.h5'), 'Keras model must be a .h5 file.'

        if ANCHORS_PATH:
            anchors_path = ANCHORS_PATH
        else:
            anchors_path = 'model_data/yolo_anchors.txt'

        if CLASSES_PATH:
            classes_path = CLASSES_PATH
        else:
            classes_path = 'model_data/coco_classes.txt'

        sess = K.get_session()  # TODO: Remove dependence on Tensorflow session.

        with open(classes_path) as f:
            class_names = f.readlines()
            class_names = [c.strip() for c in class_names]

        with open(anchors_path) as f:
            anchors = f.readline()
            anchors = [float(x) for x in anchors.split(',')]
            anchors = np.array(anchors).reshape(-1, 2)

        yolo_model = load_model(model_path)

        # Verify model, anchors, and classes are
        # compatible
        num_classes = len(class_names)
        num_anchors = len(anchors)
        # TODO: Assumes dim ordering is channel
        # last
        model_output_channels = yolo_model.layers[-1].output_shape[-1]
        assert model_output_channels == num_anchors * (num_classes + 5), \
            'Mismatch between model and given anchor and class sizes. ' \
            'Specify matching anchors and classes with --anchors_path and ' \
            '--classes_path flags.'
        print('{} model, anchors, and classes loaded.'.format(model_path))

        # Check if model is fully convolutional, assuming channel last order.
        model_image_size = yolo_model.layers[0].input_shape[1:3]
        is_fixed_size = model_image_size != (None, None)

        # Generate colors for drawing bounding boxes.
        hsv_tuples = [
            (x / len(class_names), 1., 1.) for x in range(len(class_names))
        ]
        colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        colors = list(
            map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
                colors))
        random.seed(10101)  # Fixed seed for consistent colors across runs.
        random.shuffle(colors)  # Shuffle to decorrelate adjacent classes.
        random.seed(None)  # Reset seed to default.

        # Generate output tensor targets for filtered bounding boxes.
        # TODO: Wrap these backend operations with Keras layers.
        yolo_outputs = yolo_head(yolo_model.output, anchors, len(class_names))
        input_image_shape = K.placeholder(shape=(2, ))
        boxes, scores, classes = yolo_eval(
            yolo_outputs,
            input_image_shape,
            score_threshold=SCORE_THRESHOLD,
            iou_threshold=IOU_THRESHOLD)

        # Now call the YAD2K code...
        for i in range(0, len(to_tag), BATCH_SIZE):

            print("Starting to tag %d to %d ..." % (i, i+BATCH_SIZE))

            tags = tag_batch(to_tag[i:i+BATCH_SIZE], sess, yolo_model, boxes,
                             scores, classes, class_names, input_image_shape,
                             is_fixed_size, model_image_size, colors)

            print("Tagging to %d finished, writing to db..." % (i+BATCH_SIZE))

            for extract_id in tags:
                extractImage = ExtractedImage.get(
                    ExtractedImage.id == extract_id)
                extractImage.tags = str(tags[extract_id])
                extractImage.save()

            print("db entries to %d finished..." % (i+BATCH_SIZE))

    sess.close()


def tag_batch(to_tag, sess, yolo_model, boxes,
              scores, classes, class_names, input_image_shape,
              is_fixed_size, model_image_size, colors):

    results = {}

    for extract_id, image_file in to_tag:

        # I believe this was code for making sure items in a folder were
        # actually an image and if not skipping them in the loop.

        #  try:
        #      image_type = imghdr.what(os.path.join(test_path, image_file))
        #      if not image_type:
        #          continue
        #  except IsADirectoryError:
        #      continue

        out_file = image_file.replace("extract", "yolo")
        output_path = os.path.dirname(out_file)

        if not os.path.exists(output_path):
            print('Creating output path {}'.format(output_path))
            os.mkdir(output_path)

        image = Image.open(image_file)
        if is_fixed_size:  # TODO: When resizing we can use minibatch input.
            resized_image = image.resize(
                tuple(reversed(model_image_size)), Image.BICUBIC)
            image_data = np.array(resized_image, dtype='float32')
        else:
            new_image_size = (image.width - (image.width % 32),
                              image.height - (image.height % 32))
            resized_image = image.resize(new_image_size, Image.BICUBIC)
            image_data = np.array(resized_image, dtype='float32')

        image_data /= 255.
        image_data = np.expand_dims(image_data, 0)  # Add batch dimension.

        #  print("Starting img: %s" % (image_file))

        out_boxes, out_scores, out_classes = sess.run(
            [boxes, scores, classes],
            feed_dict={
                yolo_model.input: image_data,
                input_image_shape: [image.size[1], image.size[0]],
                K.learning_phase(): 0
            })

        font = ImageFont.truetype(
            font=FONT_PATH,
            size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
        thickness = (image.size[0] + image.size[1]) // 300

        labels = []
        for i, c in reversed(list(enumerate(out_classes))):
            predicted_class = class_names[c]
            box = out_boxes[i]
            score = out_scores[i]

            label = '{} {:.2f}'.format(predicted_class, score)

            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label, font)

            top, left, bottom, right = box
            top = max(0, np.floor(top + 0.5).astype('int32'))
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
            right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
            #  print(label, (left, top), (right, bottom))
            label_details = (label, (left, top), (right, bottom))
            labels.append(label_details)

            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=colors[c])
            draw.rectangle(
                [tuple(text_origin), tuple(text_origin + label_size)],
                fill=colors[c])
            draw.text(text_origin, label, fill=(0, 0, 0), font=font)
            del draw

        image.save(out_file, quality=60)
        results[extract_id] = labels

    return results
