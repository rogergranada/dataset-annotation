# Annotators agreement using Intersection over Union

In order to evaluate the agreement of bounding box placement, we use the ratio of equally placed bounding boxes and the total of bounding boxes. A perfect match of a bounding box drawn by two different annotators is very unlikely, since some annotations may have very tight bounding boxes, while other boxes may include additional background pixels due to non rigidity of some objects. 
Hence, we use *Intersection over Union* (IoU) measure to identify equally placed bounding boxes. IoU, also known as Jaccard index, is the most commonly used metric for comparing the similarity between two arbitrary shapes, since it is invariant to the scale of the problem under consideration [[1](#references)]. It is a simple ratio that takes into account the shape properties of the objects under comparison to calculate the area of overlap between two bounding boxes in the numerator, and the area of union in the denominator. 

Using IoU, we consider not only the perfect match between the two bounding boxes as correct, but also the overlap between the two above some threshold. A typical IoU threshold is set to 0.5 and a high quality agreement can be considered when the IoU is greater than 0.7. Using the IoU >= 0.7 criteria, we achieve the ratio of correct bounding boxes *r*=0.99. The distribution of IoU between both annotators considering all instances has an IoU mean &mu;=0.92 and &sigma;=0.07, which indicates a high agreement between the annotators. 

Below, we have the distribution of IoU considering all objects, where the *y* axis contains the number of objects with a certain IoU.

<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_all.svg" align="center" width="60%"/>

We also generate the distribution of IoU for each object as follows:

<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_person.svg" align="center" width="48%"/><img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_broken_egg.svg" align="center" width="48%"/><br>
<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_shell_egg.svg" align="center" width="48%"/><img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_ham_egg.svg" align="center" width="48%"/><br>
<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_ham.svg" align="center" width="48%"/><img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_frying_pan.svg" align="center" width="48%"/><br>
<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_pan_lid.svg" align="center" width="48%"/><img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_bowl.svg" align="center" width="48%"/><br>
<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_chopstick.svg" align="center" width="48%"/><img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_cutting_board.svg" align="center" width="48%"/><br>
<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_glass.svg" align="center" width="48%"/><img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_knife.svg" align="center" width="48%"/><br>
<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_oil_bottle.svg" align="center" width="48%"/><img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_plate.svg" align="center" width="48%"/><br>
<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_saltshaker.svg" align="center" width="48%"/><img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_spoon.svg" align="center" width="48%"/><br>
<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_turner.svg" align="center" width="48%"/><img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_table.svg" align="center" width="48%"/><br>
<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_stove.svg" align="center" width="48%"/>


# Statistics for annotations

Finally, we show the data extracted from annotations:

**Input file 1**: annotator_1.txt<br>
**Input file 2**: annotator_2.txt

### Statistics for Objects

**Total number of object**: 61427<br>
**Object person**: 4700<br>
**Object broken_egg**: 648<br>
**Object shell_egg**: 1226<br>
**Object ham_egg**: 2954<br>
**Object ham**: 1947<br>
**Object frying_pan**: 4977<br>
**Object pan_lid**: 3988<br>
**Object bowl**: 4976<br>
**Object chopstick**: 291<br>
**Object cutting_board**: 4983<br>
**Object glass**: 4834<br>
**Object knife**: 628<br>
**Object oil_bottle**: 4961<br>
**Object plate**: 1389<br>
**Object saltshaker**: 4962<br>
**Object spoon**: 2594<br>
**Object turner**: 1403<br>
**Object table**: 4983<br>
**Object stove**: 4983

### General Intersection over Union (IoU)

**Mean Iou**: 0.917036482329<br>
**Std Iou**: 0.0659221219828

**Correct bboxes IoU>=0.5**: 61409<br>
**Ratio correct bboxes IoU>=0.5**: 0.99<br>
**Correct bboxes IoU>=0.7**: 61055<br>
**Ratio correct bboxes IoU>=0.7**: 0.99

### Intersection over Union (IoU) for objects

**Object person**:
- Correct bboxes IoU>=0.5: 4700
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 4699
- Ratio correct bboxes IoU>=0.7: 0.99

**Object broken_egg**:
- Correct bboxes IoU>=0.5: 648
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 641
- Ratio correct bboxes IoU>=0.7: 0.98

**Object shell_egg**:
- Correct bboxes IoU>=0.5: 1224
- Ratio correct bboxes IoU>=0.5: 0.99
- Correct bboxes IoU>=0.7: 1173
- Ratio correct bboxes IoU>=0.7: 0.95

**Object ham_egg**:
- Correct bboxes IoU>=0.5: 2954
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 2935
- Ratio correct bboxes IoU>=0.7: 0.99

**Object ham**:
- Correct bboxes IoU>=0.5: 1944
- Ratio correct bboxes IoU>=0.5: 0.99
- Correct bboxes IoU>=0.7: 1923
- Ratio correct bboxes IoU>=0.7: 0.98

**Object frying_pan**:
- Correct bboxes IoU>=0.5: 4977
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 4977
- Ratio correct bboxes IoU>=0.7: 1.0

**Object pan_lid**:
- Correct bboxes IoU>=0.5: 3988
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 3988
- Ratio correct bboxes IoU>=0.7: 1.0

**Object bowl**:
- Correct bboxes IoU>=0.5: 4976
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 4976
- Ratio correct bboxes IoU>=0.7: 1.0

**Object chopstick**:
- Correct bboxes IoU>=0.5: 291
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 287
- Ratio correct bboxes IoU>=0.7: 0.98

**Object cutting_board**:
- Correct bboxes IoU>=0.5: 4983
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 4983
- Ratio correct bboxes IoU>=0.7: 1.0

**Object glass**:
- Correct bboxes IoU>=0.5: 4834
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 4833
- Ratio correct bboxes IoU>=0.7: 0.99

**Object knife**:
- Correct bboxes IoU>=0.5: 623
- Ratio correct bboxes IoU>=0.5: 0.99
- Correct bboxes IoU>=0.7: 580
- Ratio correct bboxes IoU>=0.7: 0.92

**Object oil_bottle**:
- Correct bboxes IoU>=0.5: 4961
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 4953
- Ratio correct bboxes IoU>=0.7: 0.99

**Object plate**:
- Correct bboxes IoU>=0.5: 1389
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 1389
- Ratio correct bboxes IoU>=0.7: 1.0

**Object saltshaker**:
- Correct bboxes IoU>=0.5: 4962
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 4962
- Ratio correct bboxes IoU>=0.7: 1.0

**Object spoon**:
- Correct bboxes IoU>=0.5: 2586
- Ratio correct bboxes IoU>=0.5: 0.99
- Correct bboxes IoU>=0.7: 2507
- Ratio correct bboxes IoU>=0.7: 0.96

**Object turner**:
- Correct bboxes IoU>=0.5: 1403
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 1283
- Ratio correct bboxes IoU>=0.7: 0.91

**Object table**:
- Correct bboxes IoU>=0.5: 4983
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 4983
- Ratio correct bboxes IoU>=0.7: 1.0

**Object stove**:
- Correct bboxes IoU>=0.5: 4983
- Ratio correct bboxes IoU>=0.5: 1.0
- Correct bboxes IoU>=0.7: 4983
- Ratio correct bboxes IoU>=0.7: 1.0


---
## Acknowledgment

This study was financed in part by the Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES) and Fundação de Amparo à Pesquisa do Estado do Rio Grande do Sul (FAPERGS) agreement (DOCFIX 04/2018). We gratefully acknowledge the support of NVIDIA Corporation with the donation of the Titan Xp GPU used for this research.

---
## References

[1] Rezatofighi, Hamid and Tsoi, Nathan and Gwak, JunYoung and Sadeghian, Amir and Reid, Ian and Savarese, Silvio. 2019. [Generalized Intersection Over Union: A Metric and a Loss for Bounding Box Regression](https://doi.org/10.1109/CVPR.2019.00075). Proceedings of the 2019 IEEE Conference on Computer Vision and Pattern Recognition (CVPR 2019), pp. 658-666.  


