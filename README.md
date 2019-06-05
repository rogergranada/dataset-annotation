# Annotation for datasets

This repository contains annotations, such as objects, actions *etc*. for datasets that originally do not have it.

---
# Datasets:

## KSCGR

The Kitchen Scene Context based Gesture Recognition ([KSCGR](http://www.murase.m.is.nagoya-u.ac.jp/KSCGR/)) dataset [[1](#references)] is a fine-grained kitchen action dataset released as a challenge in [ICPR 2012](http://www.icpr2012.org). The dataset contains scenes captured by a kinect sensor fixed on the top of the kitchen, providing synchronized color and depth image sequences. Each video is 5 to 10 minutes long, containing 9,000 to 18,000 frames. The organizers of the dataset assigned labels to each frame indicating the type of gesture performed by the actors. There are 8 cooking gestures in the dataset: *breaking*, *mixing*, *baking*, *turning*, *cutting*, *boiling*, *seasoning*, *peeling*, and *none*, where *none* means that there is no action being performed in the current frame. These gestures are performed in five different menus for cooking eggs in Japan: *ham and eggs*, *omelet*, *scrambled egg*, *boiled egg*, and *kinshi-tamago*. A total of 7 different subjects perform each menu. The ground truth data contains the frame id and the action being performed within the frame.

Our annotation for this dataset consists in identifying objects that appear in the scenes.

## MPII Fine-grained Kitchen Activity

The MPII Fine-grained Kitchen Activity dataset ([MPII](https://www.mpi-inf.mpg.de/departments/computer-vision-and-multimodal-computing/research/human-activity-recognition/mpii-cooking-activities-dataset/)) [[2](#references)] contains 65 different cooking activities, named as: *lid: put on*, *open tin*, *cut stripes*, *taste*, *cut apart*, *spread*, *shake*, *open/close cupboard*, *stir*, *strew*, *take & put in fridge*, *put on cutting-board*, *rip open*, *change temperature*, *pull out*, *screw open*, *mix*, *stamp*, *take out from drawer*, *wash hands*, *take & put in drawer*, *take & put in spice holder*, *put on bread/dough*, *unroll dough*, *smell*, *wash objects*, *take & put in cupboard*, *take out from spice holder*, *take ingredient apart*, *put in bowl*, *whisk*, *take out from oven*, *peel*, *take out from cupboard*, *read*, *cut slices*, *put in pan/pot*, *package X*, *lid: remove*, *cut in*, *wipe clean*, *open/close drawer*, *cut out inside*, *grate*, *move from X to Y*, *squeeze*, *spice*, *dry*, *plug in/out*, *fill water from tap*, *take out from fridge*, *open/close fridge*, *put on plate*, *take & put in oven*, *open/close oven*, *pour*, *scratch off*, *cut off ends*, *throw in garbage*, *puree*, *cut dice*, *screw close*, *remove from package*, *open egg* and *background activity*, where in *background activity* there is not any other action occurring. Actions were recorded from 12 participants and in total there are 44 videos with a total length of more than 8 hours or 881,755 frames. It contains a total of 5,609 annotations of 65 activity categories.

---
## Acknowledgment

This study was financed in part by the Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES) and Fundação de Amparo à Pesquisa do Estado do Rio Grande do Sul (FAPERGS) agreement (DOCFIX 04/2018). We gratefully acknowledge the support of NVIDIA Corporation with the donation of the Titan Xp GPU used for this research.

---
## References

[1] A. Shimada, K. Kondo, D. Deguchi, G. Morin, and H. Stern, "Kitchen Scene Context based Gesture Recognition: A contest in ICPR 2012". In Advances in Depth Image Analysis and Applications. Springer, pp. 168-185, 2013.

[2] M. Rohrbach, S. Amin, M. Andriluka, and B. Schiele, "A Database for Fine Grained Activity Detection of Cooking Activities". In CVPR 2012, pp. 1194-1201, 2012.
