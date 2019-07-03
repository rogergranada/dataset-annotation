# Keras-Yolo3 Annotation

This annotation is performed to [keras-yolo3](https://github.com/qqwweee/keras-yolo3) training. It has the form:

Row format: `image_file_path box1 box2 ... boxN`
Box format: `x_min,y_min,x_max,y_max,class_id` (no space)

For example:

```
path/to/img1.jpg 50,100,150,200,0 30,50,200,120,3
path/to/img2.jpg 120,300,250,600,2
...
```

Annotations are divided into two files:

- `annotation.txt` contains the annotation explained above
- `classes.txt` contains the id and the name of each class

Annotation file contains all images of the dataset, *i.e.*, it is not divided into training, validation and test sets.

File `annotation_416.txt.zip` contains the annotation for the KSCGR dataset with images of size 416x416 pixels.
