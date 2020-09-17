from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import barcode
import sys
import io

LABEL_HEIGHT = 94
LABEL_WIDTH = 307
CANVAS_COLOR_RGB = (255, 255, 255)
BARCODE_IMAGE_MAX_SIZE = (175, 175)

LABEL_FONT_SIZE = 8
PATIENT_NAME_LABEL_POS = (145, 5)
DOB_LABEL_POS = (145, 33)
DATETIME_LABEL_POS = (145, 61)

TEXT_FONT_SIZE = 11
BARCODE_TEXT_POS = (200, 2)
PATIENT_NAME_TEXT_POS = (145, 19)
DOB_TEXT_POS = (145, 47)
DATETIME_TEXT_POS = (145, 75)


def generate_label(barcode_text, name_text, dob_text, timestamp_text):
    try:
        curr_file = Path(__file__)
        font_path = curr_file.parent.parent.joinpath('fonts')

        label_image = Image.new('RGB', (LABEL_WIDTH, LABEL_HEIGHT), color=CANVAS_COLOR_RGB)
        draw = ImageDraw.Draw(label_image)

        code128 = barcode.get(
            'code128',
            barcode_text,
            writer=barcode.writer.ImageWriter()
        )
        barcode_image = code128.render()
        maxsize = BARCODE_IMAGE_MAX_SIZE
        barcode_image.thumbnail(maxsize, Image.ANTIALIAS)
        label_image.paste(barcode_image, (0, 0))

        fnt = ImageFont.truetype('{}/ARIALBD.TTF'.format(font_path), LABEL_FONT_SIZE)

        draw.text(PATIENT_NAME_LABEL_POS, "Patient Name:", font=fnt, fill=(0, 0, 0))
        draw.text(DOB_LABEL_POS, "DOB:", font=fnt, fill=(0, 0, 0))
        draw.text(DATETIME_LABEL_POS, "Date/Time Received:", font=fnt, fill=(0, 0, 0))

        fnt = ImageFont.truetype('{}/ARIAL.TTF'.format(font_path), TEXT_FONT_SIZE)
        draw.text(BARCODE_TEXT_POS, barcode_text, font=fnt, fill=(0, 0, 0))
        draw.text(PATIENT_NAME_TEXT_POS, name_text, font=fnt, fill=(0, 0, 0))
        draw.text(DOB_TEXT_POS, dob_text, font=fnt, fill=(0, 0, 0))
        draw.text(DATETIME_TEXT_POS, timestamp_text, font=fnt, fill=(0, 0, 0))
        
        #If writing to Disk
        #label_image.save(file_name)

        #Instead return image in memory
        image_buffer = io.BytesIO()
        label_image.save(image_buffer, format="png")
        image_buffer.seek(0)
        return image_buffer

    except Exception as err:
        print("Error generating label: {}".format(err))
