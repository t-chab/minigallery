#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Image
import base64
import mimetypes
import os
import sys
from PIL.ExifTags import TAGS

#======================================================================
# CONFIG
#======================================================================
OutFileName = "gallerie.html"

ImgWidth = 640
ImgHeight = 480

ThumbWidth = 160
ThumbHeight = 120
#======================================================================
# END CONFIG
#======================================================================

lOutfile = '\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n\
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr">\n\
    <head>\n\
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n\
        <title>Gallerie</title>\n\
        <!-- CSS style -->\n\
        <style type="text/css">\n\
            <!--\n\
            body {{\n\
                background-color: black;\n\
                color: #00FF00;\n\
                text-align: center;\n\
            }}\n\
\
            a {{ border: none 0px; color: #00FF00; }}\n\
\
            a:hover {{\n\
                background: #900;\n\
                color: #FFF;\n\
                text-decoration: none;\n\
            }}\n\
\
            #page-container {{\n\
            }}\n\
\
            .pg {{\n\
                list-style: none none;\n\
            }}\n\
\
            .pg:after {{\n\
                clear: both;\n\
                display: block;\n\
                content: ".";\n\
                height: 0;\n\
                visibility: hidden;\n\
            }}\n\
\
            .pg li {{\n\
                list-style: none none;\n\
                margin : 2px;\n\
            }}\n\
\
            .pg li a {{\n\
                margin: 4px;\n\
                padding: 4px;\n\
                position: relative;\n\
                float: left;\n\
                display: block;\n\
                border: dashed 2px #FF7500;\n\
                width: ' + str(ThumbWidth) + 'px;\n\
                height: ' + str(ThumbHeight) + 'px;\n\
            }}\n\
\
            .pg li a:hover {{\n\
                font-size: 100%;\n\
                z-index: 2;\n\
            }}\n\
\
            .pg li a img {{\n\
                border: 0 none;\n\
                width: ' + str(ThumbWidth) + 'px;\n\
                height: ' + str(ThumbHeight) + 'px;\n\
            }}\n\
\
            .pg li a:hover img,.pg li a:active img,.pg li a:focus img {{\n\
                width: ' + str(ThumbWidth * 2) + 'px;\n\
                height: ' + str(ThumbHeight * 2) + 'px;\n\
                left: -50px;\n\
                top: -40px;\n\
                z-index: 1;\n\
            }}\n\
            -->\n\
        </style>\n\
    </head>\n\
    <body>\n\
        <div id="page-container">\n\
            <ul class="pg">\n\
{listimg}\
            </ul>\n\
        </div>\n\
    </body>\n\
</html>'


lDir = sys.argv[1]
lImgList = ''
for lFile in os.listdir(lDir):
    lFullImagePath = os.path.join(lDir, lFile)
    if os.path.isfile(lFullImagePath):

        lFullImage = open(lFullImagePath, 'rb')

        lFileType = mimetypes.guess_type(lFullImagePath)[0]
        if lFileType != None and lFileType.startswith('image'):

            lImage = Image.open(lFullImagePath).convert('RGB')
#            print('Name : ' + lFullImagePath + ' - Mode : ' + lImage.mode)

            # Reduce original image
            lImage.thumbnail((ImgWidth, ImgHeight), Image.ANTIALIAS)
            lImagePath = os.path.join(lDir, lFile + '-mini.jpg')
            lImage.save(lImagePath, 'JPEG', quality = 75)
            lImageFile = open(lImagePath, 'rb')
            lImageData = lImageFile.read()
            # Full image to base64
            lImageEncoded = base64.b64encode(lImageData)

            # Create a thumbnail
            lImage.thumbnail((ThumbWidth, ThumbHeight), Image.ANTIALIAS)
            lThumbPath = os.path.join(lDir, lFile + '-thumb.jpg')
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

            lImgList += '\
                <li>\n\
                    <a href="data:' + lFileType + ';base64,'\
                        + str(lImageEncoded) + '">\n\
                        <img src = "data:' + lFileType + ';base64,'\
                            + str(lThumbEncoded) + '" alt="' + lFile + '" /> \n\
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
lCurrentDir = os.getcwd()
lOutFilePath = os.path.join(lCurrentDir, OutFileName)
print('File saved to ' + lOutFilePath)
lOutFile = open(lOutFilePath, 'w')
lOutFile.write(lOutfile.format(listimg = lImgList))
lOutFile.close()
