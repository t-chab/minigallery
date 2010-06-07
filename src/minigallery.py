#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Takes one directory, and converts all images files into it to one 
single html files.

Images are Base64 encoded
"""

import Image
import base64
import mimetypes
import os
import sys

#======================================================================
# CONFIG
#======================================================================
DEBUG = True

OUT_FILE_NAME = "gallerie.html"

IMG_WIDTH = 640
IMG_HEIGHT = 480

THUMB_WIDTH = 160
THUMB_HEIGHT = 120
#======================================================================
# END CONFIG
#======================================================================

#======================================================================
# Following code is from : 
# http://github.com/kylefox/python-image-orientation-patch
#======================================================================

# The EXIF tag that holds orientation data.
EXIF_ORIENTATION_TAG = 274

# Obviously the only ones to process are 3, 6 and 8.
# All are documented here for thoroughness.
ORIENTATIONS = {
    1: ("Normal", 0),
    2: ("Mirrored left-to-right", 0),
    3: ("Rotated 180 degrees", 180),
    4: ("Mirrored top-to-bottom", 0),
    5: ("Mirrored along top-left diagonal", 0),
    6: ("Rotated 90 degrees", -90),
    7: ("Mirrored along top-right diagonal", 0),
    8: ("Rotated 270 degrees", -270)
}

def fix_orientation(img, save_over = False):
    """
`img` can be an Image instance or a path to an image file.
`save_over` indicates if the original image file should be replaced by the new image.
* Note: `save_over` is only valid if `img` is a file path.
"""
    path = None
    if not isinstance(img, Image.Image):
        path = img
        img = Image.open(path)
    elif save_over:
        raise ValueError("You can't use `save_over` when passing \
        an Image instance. Use a file path instead.")
    try:
        orientation = img._getexif()[EXIF_ORIENTATION_TAG]
    except TypeError:
        raise ValueError("Image file has no EXIF data.")
    if orientation in [3, 6, 8]:
        degrees = ORIENTATIONS[orientation][1]
        img = img.rotate(degrees)
        if save_over and path is not None:
            try:
                img.save(path, quality = 95, optimize = 1)
            except IOError:
                # Try again, without optimization (PIL can't optimize an image
                # larger than ImageFile.MAXBLOCK, which is 64k by default).
                # Setting ImageFile.MAXBLOCK should fix this....but who knows.
                img.save(path, quality = 95)
        return (img, degrees)
    else:
        return (img, 0)

#======================================================================
# END OF IMPORTED CODE 
#======================================================================

if __name__ == "__main__":
    OUT_FILE_CONTENT = '\
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n\
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr">\n\
        <head>\n\
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n\
            <title>Gallerie</title>\n\
            <!-- CSS style -->\n\
            <style type="text/css">\n\
                <!--\n\
                body {\n\
                    background-color: black;\n\
                    color: #00FF00;\n\
                    text-align: center;\n\
                }\n\
    \
                a { border: none 0px; color: #00FF00; }\n\
    \
                a:hover {\n\
                    background: #900;\n\
                    color: #FFF;\n\
                    text-decoration: none;\n\
                }\n\
    \
                #page-container {\n\
                }\n\
    \
                .pg {\n\
                    list-style: none none;\n\
                }\n\
    \
                .pg:after {\n\
                    clear: both;\n\
                    display: block;\n\
                    content: ".";\n\
                    height: 0;\n\
                    visibility: hidden;\n\
                }\n\
    \
                .pg li {\n\
                    list-style: none none;\n\
                    margin : 2px;\n\
                }\n\
    \
                .pg li a {\n\
                    margin: 4px;\n\
                    padding: 4px;\n\
                    position: relative;\n\
                    float: left;\n\
                    display: block;\n\
                    border: dashed 2px #FF7500;\n\
                    width: ' + str(THUMB_WIDTH) + 'px;\n\
                    height: ' + str(THUMB_HEIGHT) + 'px;\n\
                }\n\
    \
                .pg li a:hover {\n\
                    font-size: 100%;\n\
                    z-index: 2;\n\
                }\n\
    \
                .pg li a img {\n\
                    border: 0 none;\n\
                    width: ' + str(THUMB_WIDTH) + 'px;\n\
                    height: ' + str(THUMB_HEIGHT) + 'px;\n\
                }\n\
    \
                .pg li a:hover img,.pg li a:active img,.pg li a:focus img {\n\
                    width: ' + str(THUMB_WIDTH * 2) + 'px;\n\
                    height: ' + str(THUMB_HEIGHT * 2) + 'px;\n\
                    left: -50px;\n\
                    top: -40px;\n\
                    z-index: 1;\n\
                }\n\
                -->\n\
            </style>\n\
        </head>\n\
        <body>\n\
            <div id="page-container">\n\
                <ul class="pg">\n\
    %(listimg)\
                </ul>\n\
            </div>\n\
        </body>\n\
    </html>'


    IMG_DIR = sys.argv[1]
    IMG_HTML_CODE = ''
    for lFile in os.listdir(IMG_DIR):
        lFullImagePath = os.path.join(IMG_DIR, lFile)
        if os.path.isfile(lFullImagePath):

            lFullImage = open(lFullImagePath, 'rb')

            lFileType = mimetypes.guess_type(lFullImagePath)[0]
            if lFileType != None and lFileType.startswith('image'):

                lImage = Image.open(lFullImagePath).convert('RGB')
                if(DEBUG):
                    print('Name : ' + lFullImagePath \
                            + ' - Mode : ' + lImage.mode)

                # Reduce original image
                lImage.thumbnail((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
                lImagePath = os.path.join(IMG_DIR, lFile + '-mini.jpg')
                lImage.save(lImagePath, 'JPEG', quality = 75)

                # Rotate from EXIF data
                try:
                    fix_orientation(lImagePath, True)
                except ValueError:
                    if(DEBUG):
                        print('Image file has no EXIF data.')

                lImageFile = open(lImagePath, 'rb')
                lImageData = lImageFile.read()
                # Full image to base64
                lImageEncoded = base64.b64encode(lImageData)

                # Create a thumbnail
                lImage.thumbnail((THUMB_WIDTH, THUMB_HEIGHT), Image.ANTIALIAS)
                lThumbPath = os.path.join(IMG_DIR, lFile + '-thumb.jpg')
                lImage.save(lThumbPath, 'JPEG', quality = 75)
                lThumbFile = open(lThumbPath, 'rb')
                lThumbData = lThumbFile.read()
                # Thumb to base64
                lThumbEncoded = base64.b64encode(lThumbData)

                # Read exif lThumbEncoded, and rotate img
    #           info = lImage._getexif()
    #            for tag, value in info.items():
    #                decoded = TAGS.get(tag, tag)
    #                print(value)

                IMG_HTML_CODE += '\
                    <li>\n\
                        <a href="data:' + lFileType + ';base64,'\
                            + str(lImageEncoded) + '">\n\
                            <img src = "data:' + lFileType + ';base64,'\
                                + str(lThumbEncoded) + '" alt="'\
                                + lFile + '" /> \n\
                        </a>\n\
                    </li>\n'

                # Close files
                lThumbFile.close()
                lImageFile.close()

                # Kill temp thumb file
                os.remove(lThumbPath)
                os.remove(lImagePath)

            # Close file
            lFullImage.close()

    # Write html to file
    CWD = os.getcwd()
    OUT_FILE_PATH = os.path.join(CWD, OUT_FILE_NAME)
    if(DEBUG):
        print('File saved to ' + OUT_FILE_PATH)
    OUT_FILE = open(OUT_FILE_PATH, 'w')
    OUT_FILE.write(OUT_FILE_CONTENT.replace('%(listimg)', IMG_HTML_CODE))
    OUT_FILE.close()
