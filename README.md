# Pathadin

Pathadin is a tool for quick and simple quantitative pathology. Main developers @dimathe47, @Digipathology (concept)

The concept of Pathadin differs from other desktop WSI alternatives: in contrast to unitary solutions, which require rather powerful machines, it is a combinatory toolset, where each part can be separately updated and modified; this also includes the opportunity of the A.I. training without strict linkage to the local computer, as described further. Such an approach gives a better understanding of functional elements of modern computer-assisted image analysis, makes the program more flexible in the context of modification, updating and testing different models, and allows users to run digital pathology on the basic hardware.

Among Java solutions, Pathadin is entirely Python 3.6 software built with PyQT5 GUI. Pathadin is based on the openslide library. The central analytic libraries include Keras, Skimage/ Sklearn, and Histomics TK.

Pathadin project provides:
- Main graphical user interface (GUI)-application
- Tool for slicing digital slides – a convenient feature for dataset generation for machine learning or usage in alternative software
- Simply reproducable example of U-net model training.
- Supports all the Openslide formats for Whole Slide Imaging (WSI), as the main image formats.

The U-net model training can be performed separately from GUI due to training been computationally heavy and excessively dynamic, thus irrational to be enclosed by GUI.

##### DOWNLOAD: latest release 11.12.2020
- [From pathadin.eu server (204 MB)](http://pathadin.eu/pathadin/temp/11_12_2020/PathadinSetup.exe)
- [Previous release (from Google Drive)](https://drive.google.com/file/d/1cdsMnvA7apIe_uVluG4WS0goSyEHVEJC/view?usp=sharing)
- [Information about updates](https://gitlab.com/Digipathology/Pathadin/-/wikis/Update-information)

##### Minimum system requirements for adequate experience for provided binaries include
* Monitor resolution 1280 × 720
* Operation system Windows 7 SP1 or newer
* CPU Intel DualCore, RAM 4 GB

##### Getting started
* Pathadin [Wiki](https://gitlab.com/Digipathology/Pathadin/-/wikis/home) on GitLab
* http://www.pathadin.eu/
* https://doi.org/10.1016/j.acthis.2020.151619

##### **Additional infrotmation for the manuscript: "How to create an applied multiclass machine learning model in histology: a prostate based example"**
- **Dataset generation ([Google Colab](https://colab.research.google.com/drive/1gY4rloBJj1xqR325AJDM_8CC6hDrqsl7?usp=sharing))
- Model training ([Google Colab](https://colab.research.google.com/drive/1NMo3vjvpE_CGbXZLGSTa3pOwKYsAtCdX?usp=sharing))**



##### **Addtional information for the manuscript:"[Pathadin – The essential set of tools to start with whole slide analysis](https://doi.org/10.1016/j.acthis.2020.151619)"**
* [Example of generating dataset - slice_example](https://colab.research.google.com/drive/1ZWul3MWKwKVNJXz6S1AsMeDifrSWpkla?usp=sharing)
* [Dataset - archive of patches generated in slice_example](https://www.pathadin.eu/pathadin/pathadin_examples/segmentation_example/data/slice_example_patches.zip)
* [Screenshot of dataset archive structure](https://www.pathadin.eu/pathadin/pathadin_examples/segmentation_example/slice_example_patches_screen.png)
* [Example of U-net model training - segmentation_example](https://colab.research.google.com/drive/19uCd12Ru9Gu3Mk9wOgTPmJ6ItKyy1pWl?usp=sharing)
* [Trained model - h5 keras model trained in segmentation_example](https://www.pathadin.eu/pathadin/Stroma&Glands.h5)
* [Screenshot of trained model usage as filter in Pathadin main app](https://www.pathadin.eu/pathadin/Stroma&Glands.h5)

**[NB! Adding atributes for annotations (for dataset generation)](https://gitlab.com/Digipathology/Pathadin/-/wikis/Annotations)**

**[Json validator](https://www.jsonschemavalidator.net/)**.
**Download schema from [Google Drive](https://drive.google.com/file/d/1HNBHM_bFZ4ySrucATiyi6MBIDosCg4oX/view?usp=sharing).**
**Thanks to @alegvo**

##### Original mrxs slides used for dataset generation in slice_example:
* [slide1.zip](https://www.pathadin.eu/pathadin/pathadin_examples/slice_example/original_data/slide1.zip)
* [slide2.zip](https://www.pathadin.eu/pathadin/pathadin_examples/slice_example/original_data/slide2.zip)
* [slide3.zip](https://www.pathadin.eu/pathadin/pathadin_examples/slice_example/original_data/slide3.zip)
* [slide4.zip](https://www.pathadin.eu/pathadin/pathadin_examples/slice_example/original_data/slide4.zip)
* [slide5.zip](https://www.pathadin.eu/pathadin/pathadin_examples/slice_example/original_data/slide5.zip)
* [slide1_annotations.json](https://www.pathadin.eu/pathadin/pathadin_examples/slice_example/original_data/slide1_annotations.json)
* [slide2_annotations.json](https://www.pathadin.eu/pathadin/pathadin_examples/slice_example/original_data/slide2_annotations.json)
* [slide3_annotations.json](https://www.pathadin.eu/pathadin/pathadin_examples/slice_example/original_data/slide3_annotations.json)
* [slide4_annotations.json](https://www.pathadin.eu/pathadin/pathadin_examples/slice_example/original_data/slide4_annotations.json)
* [slide5_annotations.json](https://www.pathadin.eu/pathadin/pathadin_examples/slice_example/original_data/slide5_annotations.json)


##### Full-size examples (.mrxs):
* [Biopsy H&E, 40x (0,5 GB)](https://www.pathadin.eu/pathadin/biopsy(40x).zip)
* [H&E (1.1 GB)](https://www.pathadin.eu/pathadin/H&E.zip)
* [H&E(2 GB)](https://www.pathadin.eu/pathadin/HemEosin.zip)
* [Ki67(2.2 GB)](https://www.pathadin.eu/pathadin/Ki67.zip)
* [Masson`s trichrome (1.8 GB)](https://www.pathadin.eu/pathadin/Massons.zip).

