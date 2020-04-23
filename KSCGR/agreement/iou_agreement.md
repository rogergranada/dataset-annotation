# Annotators agreement using Intersection over Union

In order to evaluate the agreement of bounding box placement, we use the ratio of equally placed bounding boxes and the total of bounding boxes. A perfect match of a bounding box drawn by two different annotators is very unlikely, since some annotations may have very tight bounding boxes, while other boxes may include additional background pixels due to non rigidity of some objects. 
Hence, we use *Intersection over Union* (IoU) measure to identify equally placed bounding boxes. IoU, also known as Jaccard index, is the most commonly used metric for comparing the similarity between two arbitrary shapes, since it is invariant to the scale of the problem under consideration [[1](#references)]. It is a simple ratio that takes into account the shape properties of the objects under comparison to calculate the area of overlap between two bounding boxes in the numerator, and the area of union in the denominator. 

Using IoU, we consider not only the perfect match between the two bounding boxes as correct, but also the overlap between the two above some threshold. A typical IoU threshold is set to 0.5 and a high quality agreement can be considered when the IoU is greater than 0.7. Using the IoU >= 0.7 criteria, we achieve the ratio of correct bounding boxes *r*=0.99. The distribution of IoU between both annotators considering all instances has an IoU mean &mu;=0.92 and &sigma;=0.07, which indicates a high agreement between the annotators. 

Below, we have the distribution of IoU considering all objects, where the *y* axis contains the number of objects with a certain IoU.

<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/occlusion.svg" align="center" width="100%"/>

We also generate the distribution of IoU for each object as follows:

![alt-text-1](https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_person.svg "IoU-Person") ![alt-text-2](https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/iou_shell_egg.svg "IoU-Shell-egg")

---
## Acknowledgment

This study was financed in part by the Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES) and Fundação de Amparo à Pesquisa do Estado do Rio Grande do Sul (FAPERGS) agreement (DOCFIX 04/2018). We gratefully acknowledge the support of NVIDIA Corporation with the donation of the Titan Xp GPU used for this research.

---
## References

[1] Rezatofighi, Hamid and Tsoi, Nathan and Gwak, JunYoung and Sadeghian, Amir and Reid, Ian and Savarese, Silvio. 2019. [Generalized Intersection Over Union: A Metric and a Loss for Bounding Box Regression](https://doi.org/10.1109/CVPR.2019.00075). Proceedings of the 2019 IEEE Conference on Computer Vision and Pattern Recognition (CVPR 2019), pp. 658-666.  


