if __name__ == '__main__':
    # Install required binaries and packages
    # !apt-get install openslide-tools
    # !pip install scikit-image opencv-python shapely h5py openslide-python dataclasses pydantic
    #
    # We need to clone project and add it to sys.path (we haven't installable packages yet)
    # !git clone https://gitlab.com/Digipathology/Pathadin.git
    #
    path_to_project = r'D:\projects\Pathadin\src\main\python'
    # path_to_project = 'Pathadin/src/main/python'
    import pathlib, sys

    sys.path.append(str(pathlib.Path(path_to_project).resolve()))

    # We define working root folder for convenience
    root_path = pathlib.Path.home().joinpath("temp/pathadin_examples/data")
    root_path.mkdir(parents=True, exist_ok=True)


    # In this example we will show how to generate label/image patches from slide images.
    # We will generate:
    # 1) patch_slide_image - color patch image from slide
    # 2) patch_label_image - binary patch image as result of drawing annotation region with color specified in annotation
    # To better explain idea of annotation-drawing we will show screenshot from main application.
    # In this screenshot we have 2 annotations: one stroma(red) annotation and one glands(blue) annotation.
    # Attribute user_attrs.label_color in annotation specifies with what color this annotation will be drawn.
    def show_app_slide1_annotations_screenshot():
        from common_urllib.core import load_gdrive_file

        app_slide1_annotations_screenshot_path = str(root_path.joinpath('app_slide1_annotations_screenshot_path.png'))
        load_gdrive_file('1bO9a0LSdXsuvt9o4wkpBw-zldOrIMQBM', app_slide1_annotations_screenshot_path)
        from IPython.display import Image, display
        img = Image(filename=app_slide1_annotations_screenshot_path, width=800)
        print("Screenshot of slide1 annotations in main application:")
        display(img)


    # show_app_slide1_annotations_screenshot()

    # Lets begin our example itself.
    # Define paths to slides and annotations.
    # Choose one method below to use your data or example data.
    from slice.slide_path import SlidePath


    def define_example_data():
        # Original mrxs slide is about 4gb memory.
        # To make example more reproducible and lightweight we cut a small region from it and interpret it as a real slide.
        slide_paths = []
        slide1_path = str(root_path.joinpath("slide1.jpeg").resolve())
        slide1_annotations_path = str(root_path.joinpath("slide1_annotations.json").resolve())
        slide2_path = str(root_path.joinpath("slide2.jpeg").resolve())
        slide2_annotations_path = str(root_path.joinpath("slide2_annotations.json").resolve())
        slide_paths.append(SlidePath(slide1_path, slide1_annotations_path))
        slide_paths.append(SlidePath(slide2_path, slide2_annotations_path))

        def load_images_and_annotations():
            from common_urllib.core import load_gdrive_file
            load_gdrive_file('1n8TDA-4gnNSb0fUFhm5i7J5FitfcJVoH', slide1_path)
            load_gdrive_file('1He8XhiRTw6zGiVqlYLtqSGeHiI4th1LX', slide1_annotations_path)
            load_gdrive_file('1BrpN42SZoaz46CjqUQNy2rn5seRBui0w', slide2_path)
            load_gdrive_file('1itDFGs83HiGuSGLNV-G1BVJUOuv1LPtO', slide2_annotations_path)

        load_images_and_annotations()
        return slide_paths


    def define_my_custom_data():
        # Original big-size slides.
        slide_paths = []
        slide_paths.append(SlidePath(r"D:\temp\slides\slide1.mrxs", r"D:\temp\slides\annotations2\slide1_annotations.json"))
        # slide_paths.append(SlidePath(r"D:\temp\slides\slide5.mrxs", r"D:\temp\slides\annotations2\slide5_annotations.json"))
        # slide_paths.append(SlidePath(r"D:\temp\slides\slide3.mrxs", r"D:\temp\slides\annotations2\slide3_annotations.json"))
        # slide_paths.append(SlidePath(r"D:\temp\slides\slide4.mrxs", r"D:\temp\slides\annotations2\slide4_annotations.json"))
        # slide_paths.append(SlidePath(r"D:\temp\slides\slide6.mrxs", r"D:\temp\slides\annotations2\slide6_annotations.json"))
        return slide_paths


    # slide_paths = define_example_data()
    slide_paths = define_my_custom_data()

    # There are several use-cases for slicing slide-images.
    # 1) Generating patch_label_images together with generating patch_slide_images. Where
    #    a) patch_label_image is a result of drawing annotation with label color stored in annotation
    #    b) patch_slide_image is just a corresponding region from the same slide
    # 2) Generate patch_label_images together with generating patch_slide_images. Where
    #    a) patch_label_image is a region from some specifically stained slide
    #    b) patch_slide_image is the same region from (possibly a bit shifted) corresponding H&E slide
    # 3) Do not generate patch_label_images but generate just patch_slide_images.
    #    It can be useful when you want:
    #    - label patches manually in some graphics editor
    #    - label patches with your custom script
    #
    # Here we will consider the use-case 1.
    # We will generate patch_label_images and then generate corresponding patch_slide_images.
    #
    # High-level api for generating patches operates on dict-like config objects.
    # There are 2 types of config: PatchImageSourceConfig, PatchImageConfig.
    # PatchImageSourceConfig defines params for generating patches from slide.
    # It is named "source" because it initiates data-flow:
    # patch_pos->patch_geometry->patch_label_image->patch_slide_image.
    # It is designed so to allow hooks.
    # Different hooks can be placed in this data-flow such that irrelevant
    # and uninteresting positions/resulting label images will be filtered out.
    # At this moment PatchResponseGenerator uses such hooks that
    # it skips patch geometry if it doesn't fully contained by some roi annotation.
    # You can add your hooks to this data-flow. For example you can add hook to filter out patch label images
    # that are uninteresting in sense of class distribution - ignore fully
    # white or fully black resulting label images but take only label image containing both classes.
    #
    # Grid positions and label images can be filtered out in data-flow so
    # ONLY AFTER generating patch_label_image and confirming it as "interesting"(means not filtering it out)
    # it make sense to generate corresponding patch_slide_image.
    # It means that process of generating patch_slide_images depends on process
    # of generating patch_label_images. This dependence is represented with attribute
    # "dependents" in PatchImageSourceConfig.
    #
    # Lets define parameters for configs.
    # Patch size in pixels. Resulting patches will have this size.
    patch_size = (512, 512)
    # Level of slide. Can be interpreted as level of detail(resolution) with the best detail at 0-level.
    level = 2
    # Stride of slicer - distance between subsequent patches.
    stride_x, stride_y = patch_size[0], patch_size[1]

    from slice.model.patch_image_config import PatchImageConfig
    from slice.model.patch_image_source_config import PatchImageSourceConfig


    def build_config_for_slide_path(slide_path: SlidePath) -> PatchImageSourceConfig:
        return PatchImageSourceConfig(
            slide_path=slide_path.slide_path,
            level=level,
            target_color_mode='L',
            annotations_path=slide_path.annotations_path,
            metadata={"name": "label"},
            patch_size=patch_size,
            stride_x=stride_x,
            stride_y=stride_y,
            dependents=[
                PatchImageConfig(
                    slide_path=slide_path.slide_path,
                    level=level,
                    target_color_mode='RGB',
                    metadata={"name": "image"}
                )
            ]
        )


    configs = [build_config_for_slide_path(slide_path) for slide_path in slide_paths]

    # PatchResponseGenerator processes configs one by one generating patches and puts these patches into
    # one data-flow: Iterable[PatchResponse]
    from slice.generator.response.patch_response_generator import PatchResponseGenerator

    patch_responses = PatchResponseGenerator().create(configs)

    # Then we convert every patch_response to named_ndarray - Tuple[str, np.ndarray]
    # We select name format convenient for saving/loading to/from disk.
    from slice.patch_response_utils import patch_responses_to_named_ndarrays

    format_str = r"{cfg.metadata[name]}/{cfg.metadata[name]}/{pos[1]},{pos[0]}_{cfg.level}_{cfg.metadata[name]}.jpg"
    named_ndarrays = patch_responses_to_named_ndarrays(patch_responses, format_str)

    # We often want to store results of generating patches.
    # We will save arrays as image files inside zip archive.
    from ndarray_persist.save import save_named_ndarrays

    patches_path = root_path.joinpath("slice_patches.zip")
    save_named_ndarrays(named_ndarrays, str(patches_path), delete_if_exists=True, verbosity=1)

    # We have just saved both labels and images.
    # Now we can load both labels and images from data store as one data-flow.
    # But it is common case to load labels and images separately, so here is example.
    from ndarray_persist.load.ndarray_loader_factory import NdarrayLoaderFactory

    labels_loader = NdarrayLoaderFactory.from_name_filter(str(patches_path), name_pattern=f'.*label.*')
    images_loader = NdarrayLoaderFactory.from_name_filter(str(patches_path), name_pattern=f'.*image.*')
    labels_names = list(labels_loader.load_names())
    images_names = list(images_loader.load_names())
    print(f"label patches: {len(labels_names)}, image patches: {len(images_names)}")

    # Lets plot (patch_image, patch_label) pairs
    import matplotlib.pyplot as plt
    import itertools
    from common_matplotlib.core import plot_named_ndarrays_tuples_by_batches

    plt.rcParams['figure.figsize'] = (10, 5)
    named_images = images_loader.load_named_ndarrays()
    named_labels = labels_loader.load_named_ndarrays()
    image_tuples = zip(named_images, named_labels)
    image_tuples = itertools.islice(image_tuples, 300)
    print("Image-label pairs:")
    plot_named_ndarrays_tuples_by_batches(image_tuples, ncols=6, tuples_per_plot=12)

    # To download file to localhost you can download it as "Browser download file"
    # or mount your google drive and copy file to it:
    # https://colab.research.google.com/notebooks/io.ipynb
    # Another option is to mount google drive in the beginning of example
    # and make all io in some directory of gdrive.
    #
    # We will mount gdrive and copy file to gdrive directory.
    # from google.colab import drive
    # drive.mount('/content/drive')
    # gdrive_path = pathlib.Path('/content/drive/My Drive/pathadin_examples/data', patches_path.name)
    # gdrive_path.parent.mkdir(parents=True, exist_ok=True)
    # import shutil
    # shutil.copy2(str(patches_path), gdrive_path)
