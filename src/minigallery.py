#!/usr/bin/env python2
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

IMG_MAXBLOCK = 10000000

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
        lexifinfo = img._getexif
        orientation = lexifinfo[EXIF_ORIENTATION_TAG]
    except TypeError:
        raise ValueError("Image file has no EXIF orientation data.")
    if orientation in [3, 6, 8]:
        degrees = ORIENTATIONS[orientation][1]
        img = img.rotate(degrees)
        if save_over and path is not None:
            try:
                img.MAXBLOCK = IMG_MAXBLOCK
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
            <!-- Galleria is a GPLv3 script available from http://galleria.aino.se/ -->\n\
            <link rel="stylesheet" href="https://github.com/aino/galleria/raw/master/src/themes/classic/galleria.classic.css" />\n\
            <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"></script>\n\
            <script type="text/javascript" src="https://github.com/aino/galleria/raw/master/src/galleria.js"></script>\n\
        </head>\n\
        <body style="background-color: black;">\n\
            <script type="text/javascript">Galleria.loadTheme(\'https://github.com/aino/galleria/raw/master/src/themes/classic/galleria.classic.js\')</script>\n\
            <div id="images" style="width: ' + str(IMG_WIDTH) + 'px; height: '\
                + str(IMG_HEIGHT) + 'px; margin-left: auto; \
                margin-right: auto;">\n\
%(listimg)\
            </div>\n\
            <script type="text/javascript">$("#images").galleria();</script>\n\
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
                # Rotate from EXIF data
                try:
                    fix_orientation(lFullImagePath, True)
                except ValueError:
                    if(DEBUG):
                        print('Image file has no EXIF data.')

                lImage = Image.open(lFullImagePath).convert('RGB')
                if(DEBUG):
                    print('Name : ' + lFullImagePath \
                            + ' - Mode : ' + lImage.mode)

                # Reduce original image
                lImage.thumbnail((IMG_WIDTH, IMG_HEIGHT), Image.ANTIALIAS)
                lImagePath = os.path.join(IMG_DIR, lFile + '-mini.jpg')

                # Raise buffer size to avoid "Suspension not allowed" errors
                # (see 
                # http://mail.python.org/pipermail
                # /image-sig/1999-August/000816.html) 
                lImage.MAXBLOCK = IMG_MAXBLOCK

                lImage.save(lImagePath, 'JPEG', quality = 75)

                lImageFile = open(lImagePath, 'rb')
                lImageData = lImageFile.read()

                lPilImage = Image.open(lImagePath)

                # Full image to base64
                lImageEncoded = base64.b64encode(lImageData)

                IMG_HTML_CODE += '\
                <img src="data:' + lFileType + ';base64,' + str(lImageEncoded) \
                + '" height="' + str(lPilImage.size[1]) + '" width="'\
                + str(lPilImage.size[0]) + '" alt="' + lFile + '" />\n'

                # Close file
                lImageFile.close()

                # Kill temp file
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
