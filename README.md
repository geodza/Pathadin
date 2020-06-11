# Pathadin

Pathadin is tool for quick and simple quantitative pathology. It is developed in close collaboration between programmists and pathologists of the Estonian Digital Pathology Association ([EDIPA](https://pathology.ee/)).

The concept of Pathadin differs from other desktop WSI alternatives: in contrast to unitary solutions, which require rather powerful machines, it is a combinatory toolset, where each part can be separately updated and modified; this also includes the opportunity of the A.I. training without strict linkage to the local computer, as described further. Such an approach gives a better understanding of functional elements of modern computer-assisted image analysis, makes the program more flexible in the context of modification, updating and testing different models, and allows users to run digital pathology on the basic hardware.

Among Java solutions, Pathadin is entirely Python 3.6 software built with PyQT5 GUI. Pathadin is based on the openslide library. The central analytic libraries include Keras, Skimage/ Sklearn, and Histomics TK.

Pathadin project provides:
* Main graphical user interface (GUI)-application
* Tool for slicing digital slides – a convenient feature for dataset generation for machine learning or usage in alternative software
* Simply reproducable example of U- net model training.


The U-net model training is performed separately from GUI due to training been computationally heavy and excessively dynamic, thus irrational to be enclosed by GUI.

Minimum system requirements for adequate experience for provided binaries include
* Monitor resolution 1280 × 720
* Operation system Windows 7 SP1 or newer
* CPU Intel DualCore, RAM 4 GB

**Supports all the Openslide formats for Whole Slide Imaging (WSI), as the main image formats.**

**Getting started**
* Pathadin [Wiki](https://gitlab.com/Digipathology/Pathadin/-/wikis/home) on GitLab
* http://www.pathadin.eu/
* Latest release ([10.06.2020][Google Drive](https://drive.google.com/file/d/1cdsMnvA7apIe_uVluG4WS0goSyEHVEJC/view?usp=sharing
))
* [Updates](https://gitlab.com/Digipathology/Pathadin/-/wikis/Updates)

**Stroma and gland seprataion for manuscript "Pathadin – a simple tool for quantitative pathology."**
* [Dataset](https://www.pathadin.eu/pathadin/slice_example_patches.zip)
* [Trained model](https://www.pathadin.eu/pathadin/Stroma&Glands.h5)
* [Segmentation example](https://colab.research.google.com/drive/1kc9mKy1ldCQCFXIzy8l_tqGC2FGLcqOd)
* [Generating dataset](https://colab.research.google.com/drive/107Pyqbz2FIkyQTAAXsebK-nkWh0O5BQN)

**Full-size examples (.mrxs):**
* [Biopsy H&E, 40x (0,5 GB)](https://www.pathadin.eu/pathadin/biopsy(40x).zip)
* [H&E (1.1 GB)](https://www.pathadin.eu/pathadin/H&E.zip)
* [H&E(2 GB)](https://www.pathadin.eu/pathadin/HemEosin.zip)
* [Ki67(2.2 GB)](https://www.pathadin.eu/pathadin/Ki67.zip)
* [Masson`s trichrome (1.8 GB)](https://www.pathadin.eu/pathadin/Massons.zip).

