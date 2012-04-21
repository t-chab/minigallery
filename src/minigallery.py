#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Takes one directory, and converts all images files into it to one 
single html files.

Images are Base64 encoded
"""

import base64
import mimetypes
import os
import sys
from PIL import Image
from PIL.ExifTags import TAGS
from PySide import QtGui

#======================================================================
# CONFIG
#======================================================================
DEBUG = True

OUT_FILE_NAME = "gallerie.html"

IMG_WIDTH = 840
IMG_HEIGHT = 630

IMG_QUALITY = 75

IMG_MAXBLOCK = 10000000

#======================================================================
# END CONFIG
#======================================================================

# Creating Frame extending QWidget 
class Frame(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        # Window Size
        self.resize(600, 500)

        # Verdana as default font 
        self.setFont(QtGui.QFont("Verdana"))

        # Window title 
        self.setWindowTitle("Minigallery : the html gallery generator")

        # Add launch button
        self.quit_0 = QtGui.QPushButton("Run", self)

        # Button geometry
        self.quit_0.setGeometry(490, 450, 100, 30)

        # Bind button to click event and action
        self.quit_0.clicked.connect(quit)

        #À noter que quit est un slot prédéfini et qu'il permet de quitter l'application proprement.
        #Slot est un terme propre à Qt. Certains sont prédéfinis, d'autres seront créés directement par vous. 
        #Dans ce cas-là, il s'agira ni plus ni moins que des fonctions que vous avez rencontrées dans votre 
        #apprentissage de Python.



        # Set icon if exists 
#        try:
#            self.setWindowIcon(QtGui.Icon("icon.png"))
#        except:pass

class ImageTools():
    #def fix_orientation(self, img, save_over = False):
    def fix_orientation(self, pImg):
        """
        `lImg` can be an Image instance or a path to an image file.
        `save_over` indicates if the original image file should be replaced by the new image.
        * Note: `save_over` is only valid if `lImg` is a file path.
        """
        path = pImg
        lImg = Image.open(pImg)
        lExif = lImg._getexif()
        if lExif != None:
            for tag, value in lExif.items():
                decoded = TAGS.get(tag, tag)
                if decoded == 'Orientation':
                    if value == 3: lImg = lImg.rotate(180)
                    if value == 6: lImg = lImg.rotate(270)
                    if value == 8: lImg = lImg.rotate(90)
                    break

        lImg.save(path, quality = 95)

    #======================================================================
    # END OF IMPORTED CODE 
    #======================================================================

    def buildGallery(self):
            OUT_FILE_CONTENT = '\
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n\
            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr">\n\
                <head>\n\
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n\
                    <title>Gallerie</title>\n\
                    <!-- Galleria is a GPLv3 script available from http://galleria.aino.se/ -->\n\
                    <!-- 3.css == galleria.classic.css (https://github.com/aino/galleria/raw/master/src/themes/classic/galleria.classic.css) -->\n\
                    <link rel="stylesheet" href="http://galleria.io/static/themes/3/3.css" />\n\
                    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"></script>\n\
                    <script type="text/javascript" src="https://github.com/aino/galleria/raw/master/src/galleria.js"></script>\n\
                </head>\n\
                <body style="background-color: black;">\n\
                    <script type="text/javascript">Galleria.loadTheme(\'https://github.com/aino/galleria/raw/master/src/themes/classic/galleria.classic.js\')</script>\n\
                    <div id="images" style="width: ' + str(IMG_WIDTH) + 'px; height: '\
                        + str(IMG_HEIGHT) + 'px; margin-left: auto; margin-right: auto;">\n\
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
                            self.fix_orientation(lFullImagePath)
                        except ValueError:
                            if(DEBUG):
                                print('FileType=' + lFileType)

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

                        lImage.save(lImagePath, 'JPEG', quality = IMG_QUALITY)

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

if __name__ == "__main__":
    #app = QtGui.QApplication(sys.argv)
    #frame = Frame()
    #frame.show()
    #sys.exit(app.exec_())
    lGallery = ImageTools()
    lGallery.buildGallery()
