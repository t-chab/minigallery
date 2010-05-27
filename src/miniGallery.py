#!/usr/bin/env python
# -*- coding: utf-8 -*-

from string import Template
from PIL.ExifTags import TAGS
import base64
import mimetypes
import os
import sys
import Image

imgWidth=640
imgHeight=480

thumbWidth=160
thumbHeight=120

options = { }
options["optimize"] = 1
options["quality"] = 75
options["progression"] = 1

outfile = '\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n\
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr">\n\
    <head>\n\
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n\
        <title>Gallerie</title>\n\
        <!-- CSS style -->\n\
        <style type="text/css">\n\
            body {{ background-color: black; color: #00FF00; }}\n\
            a {{ border: none 0px; color: #00FF00; }}\n\
            img {{ border: dashed 2px #FF7500; margin: 5px; }}\n\
            p {{ float: left; }}\n\
            .thumb {{ margin : 2px; }}\n\
            ul {{ list-style-type: circle; }}\n\
        </style>\n\
    </head>\n\
    <body>\n\
        <div>\n\
{listimg}\
        </div>\n\
    </body>\n\
</html>'


rep = sys.argv[1]
imglist = ''
for f in os.listdir(rep):
    fullpath = os.path.join(rep, f)
    if os.path.isfile(fullpath):
        fic = open(fullpath, 'rb')
        filetype = mimetypes.guess_type(fullpath)[0]
        if filetype != None and filetype.startswith('image'):

            # Create thumbnail
            im = Image.open(fullpath).convert('RGB')
#            print('Name : ' + fullpath + ' - Mode : ' + im.mode)
            im.thumbnail((imgWidth, imgHeight), Image.ANTIALIAS)
            miniature = os.path.join(rep, f + '-mini.jpg')
            im.save(miniature, 'JPEG', quality=75)

            # TODO : Read exif data, and rotate img
#def get_exif(fn):
#ret = {}
#i = Image.open(fn)
#info = i._getexif()
#for tag, value in info.items():
#decoded = TAGS.get(tag, tag)
#ret[decoded] = value
#return ret

            # Base64 encoding
#            print(miniature)
            fmini = open(miniature, 'rb')
            fdata = fmini.read()
            data = base64.b64encode(fdata)
            imglist += '            <p>'
            imglist += '                <img src="data:' + filetype + ';base64,' + str(data) + '" width="' + str(thumbWidth) + '" height="' + str(thumbHeight)  + '" />\n'
            imglist += '            </p>'
            fmini.close()
            os.remove(miniature)
        fic.close()

print(outfile.format(listimg=imglist))
