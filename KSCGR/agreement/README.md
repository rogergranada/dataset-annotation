# Agreement between annotation for KSCGR datasets

In order to measure the inter-annotator agreement, both subjects annotated the same video containing an entire recipe. The annotated video contains 4,983 frames of a person doing the *ham egg* recipe. The files of each annotation are [annotator_1.txt](annotator_1.txt) and [annotator_2.txt](annotator_2.txt). Using the annotation of both subjects, we assess the annotation process by measuring the correctness of the semantic label (*e.g*, *shell egg*, *bowl*, *knife*) and the agreement of each object's bounding box placement in the image. 

For evaluating the agreement of the semantic label, we use the Cohen's Kappa agreement [[1](#references)] in category labels for each image. Cohen's Kappa (&kappa;) is a robust statistic useful for inter-annotator reliability testing. It ranges from -1 to +1, where 0 represents the amount of agreement expected from random chance, and 1 represents a perfect agreement between the annotators.
Cohen's kappa may be calculated according to Equation below. 

<img src="https://latex.codecogs.com/svg.latex?%5Cinline%20%5Clarge%20%5Ckappa%20%3D%20%5Cfrac%7Bp_o%20-%20p_e%7D%7B1%20-%20p_e%7D" align="center"/>

where p<sub>o</sub> represents the actual observed agreement, and p<sub>e</sub> represents the chance agreement. 

Computing the agreement between the two annotators, we achieve a &kappa;*=0.99*. As suggested by Cohen, values between 0.81 and 0.99 indicate almost perfect agreement. A further analysis on annotations indicates that most divergence in annotation occurs due to occlusion of objects, *i.e.*, in which frame the annotator decides to stop annotating the object due to occlusion. A total of 61,653 objects were annotated, where 197 object instances are annotated only by one of the subject, 29 only by the other subject, and 61,427 by both subjects. The image below illustrates a frame where (a) the annotator still includes the annotation for *ham* object (highlighted in red) and (b) the annotator does not consider annotating the object due to occlusion.  Other factors of disagreement include objects that are leaving or entering the frame, *i.e*, objects that do not appear complete in the image. For example, the image below illustrates a frame where (c) the annotator included the object that is entering the scene (object highlighted in red), while (d) the annotator still does not consider the object in the scene. 

<img src="https://raw.githubusercontent.com/rogergranada/dataset-annotation/master/KSCGR/images/occlusion.svg" align="center" width="100%"/>

---
## Acknowledgment

This study was financed in part by the Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES) and Fundação de Amparo à Pesquisa do Estado do Rio Grande do Sul (FAPERGS) agreement (DOCFIX 04/2018). We gratefully acknowledge the support of NVIDIA Corporation with the donation of the Titan Xp GPU used for this research.

---
## References

[1] Jacob Cohen. 1960. [A Coefficient of Agreement for Nominal Scales](https://doi.org/10.1177/001316446002000104). Educational and Psychological Measurement, 20, 1(1960), 37–46.  
