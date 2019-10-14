#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
This script plays the sequence of frames from a file, drawing the bounding boxes of
each object. At each line, the input file must to have the following sequence:

```
path_to_image.jpg xmin,ymin,xmax,ymax,class xmin,ymin,xmax,ymax,class xmin,ymin,xmax,ymax,class
```

Where xmin, ymin, xmax and ymax refer to the bounding box position that will be drawn. Class
represents the bounding box color.
""" 

import os
from os.path import join, splitext, basename
from os.path import realpath

import argparse
# Python 2
from Tkinter import Tk, Label, Listbox, END, N, S, W
# Python 3
#from tkinter import Tk, Label, Listbox, END, N, S, W
from PIL import Image, ImageTk, ImageDraw
import ast
from matplotlib import colors

class ImageManager(object):
    """
    Class to manage the frames
    """
    def __init__(self, input):
        """
        Initiates the class ImageManager
    
        Parameters:
        -----------
        input : string
            path to the input file containing the paths to the images
            as well as the true values and the predicted values
        """
        self.input = realpath(input)
        self.imgdata = []
        self.index = 0
        self.width = 0
        self.height = 0
        self._loadImages()


    def __iter__(self):
        """
        Iterates over the images yielding the path of the image,
        the name of the image, the true label and the predicted label.
        """
        for path, name in self.imgdata:
            yield path, name

    
    def _check_size(self, pathimg):
        """Check the size of an image"""
        im = Image.open(pathimg)
        self.width, self.height = im.size


    def _loadImages(self):
        """
        Extract the content from the file and stores into an array.
        """
        self.imgdata = []
        with open(self.input) as fin:
            for line in fin:
                arr = line.strip().split()
                path = arr[0]
                positions = []
                for i, pos_label in enumerate(arr[1:]):
                    pos_label = ast.literal_eval(pos_label)
                    #xmin, ymin, xmax, ymax, class_id = pos_label
                    positions.append(pos_label)
                self.imgdata.append((path, positions))
                self._check_size(path)
        return self.imgdata


    def nextImage(self):
        """
        Return the path, true label and predicted label of the next image 
        in the list of images.
        """
        path, positions = self.imgdata[self.index]
        name, _ = splitext(basename(path))
        if self.index < len(self.imgdata)-1:
            self.index += 1
        
        im = Image.open(path)
        draw = ImageDraw.Draw(im)
        for xmin, ymin, xmax, ymax, class_id in positions:
            cname = colors.cnames.keys()[class_id]
            draw.rectangle(((xmin, ymin), (xmax, ymax)), outline=cname)
        return name, im
#End of class ImageManager


class DemoWindow(Tk):
    """
    Class to manage the window of the demo
    """
    def __init__(self, fileinput):
        """
        Build the visual interface with images and fields to the images data
        """
        fileinput = realpath(fileinput)
        self.imgs = ImageManager(fileinput)
        Tk.__init__(self)
        self.title("Frame sequence")
        # width x height + x_offset + y_offset:
        self.geometry(str(self.imgs.width+20)+"x"+str(self.imgs.height+30)+"+1+1")
        self.i = 0
        self.prev = 0

        self.frame = Label(self, text="")
        self.frame.grid(row=0, column=1, padx=10, pady=2, sticky=N+S+W)

        self.image = Label(self, image=None)
        self.image.grid(row=1, column=1, padx=10, pady=2, sticky=N+S+W)

        self.update_window()


    def updateImage(self, img):
        """
        Update the Label containing the image
        """
        self.tkimage = ImageTk.PhotoImage(img)
        self.image.configure(image=self.tkimage)


    def updateLabelFrame(self, text):
        """
        Update the label containing the number of the frame
        """
        self.frame.configure(text='Frame: '+text)


    def update_window(self):
        """
        Update the window and its elements every second
        """
        name, fimg = self.imgs.nextImage()
        self.updateImage(fimg)
        self.updateLabelFrame(name)
        self.after(1, self.update_window)
#End of class DemoWindow


if __name__== "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('inputfile', metavar='file_input', 
                        help='file or folder containing images.')
    args = parser.parse_args()
    
    window = DemoWindow(args.inputfile)
    window.mainloop()
    
