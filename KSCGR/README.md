# Annotation for datasets

This repository contains annotations, such as objects, actions *etc*. for datasets that originally do not have it.

---
# Datasets:

## KSCGR

The Kitchen Scene Context based Gesture Recognition [KSCGR](http://www.murase.m.is.nagoya-u.ac.jp/KSCGR/) dataset [[1](#references)] is a fine-grained kitchen action dataset released as a challenge in [ICPR 2012](http://www.icpr2012.org). The dataset contains scenes captured by a kinect sensor fixed on the top of the kitchen, providing synchronized color and depth image sequences. Each video is 5 to 10 minutes long, containing 9,000 to 18,000 frames. The organizers of the dataset assigned labels to each frame indicating the type of gesture performed by the actors. There are 8 cooking gestures in the dataset: *breaking*, *mixing*, *baking*, *turning*, *cutting*, *boiling*, *seasoning*, *peeling*, and *none*, where *none* means that there is no action being performed in the current frame. These gestures are performed in five different menus for cooking eggs in Japan: *ham and eggs*, *omelet*, *scrambled egg*, *boiled egg*, and *kinshi-tamago*. A total of 7 different subjects perform each menu. The ground truth data contains the frame id and the action being performed within the frame.

Our annotation for this dataset consists in identifying objects that appear in the scenes.


## References

[1] A. Shimada, K. Kondo, D. Deguchi, G. Morin, and H. Stern, "Kitchen Scene Context based Gesture Recognition: A contest in ICPR 2012". In Advances in Depth Image Analysis and Applications. Springer, pp. 168-185, 2013.
