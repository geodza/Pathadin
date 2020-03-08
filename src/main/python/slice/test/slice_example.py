if __name__ == '__main__':
    # Install required binaries and packages
    # !apt-get install openslide-tools
    # !pip install scikit-image opencv-python shapely h5py openslide-python dataclasses pydantic
    #
    # !ssh-keygen -R gitlab.com
    # !ssh-keyscan -t rsa gitlab.com >> ~/.ssh/known_hosts
    # !ssh-keygen -t rsa -b 4096 -C gitlab2
    # !cat ~/.ssh/id_rsa.pub
    # Git clone will work without ssh after opening access
    # !git clone git@gitlab.com:Digipathology/dieyepy.git
    # !git -C dieyepy pull
    #
    # We need to clone project and add it to sys.path (we haven't installable packages yet)
    path_to_project = r'D:\projects\dieyepy\src\main\python'
    # path_to_project = 'dieyepy/src/main/python'
    import pathlib, sys

    sys.path.append(str(pathlib.Path(path_to_project).resolve()))

    # We define working root folder for convenience
    root_path = pathlib.Path.home().joinpath("temp/slice_example1")
    root_input_path = root_path.joinpath("input")
    root_output_path = root_path.joinpath("output")
    root_input_path.mkdir(parents=True, exist_ok=True)
    root_output_path.mkdir(parents=True, exist_ok=True)

    # Define paths to slides and annotations.
    # Choose one method below to use your data or example data.
    from slice.slide_path import SlidePath

    slide_paths = []


    def define_example_data():
        # Original mrxs slide is about 4gb memory.
        # To make example more reproducible and lightweight we cut a small region from it and interpret it as a real slide.

        slide1_path = str(root_input_path.joinpath("slide1.jpeg").resolve())
        slide1_annotations_path = str(root_input_path.joinpath("slide1_annotations.json").resolve())
        slide2_path = str(root_input_path.joinpath("slide2.jpeg").resolve())
        slide2_annotations_path = str(root_input_path.joinpath("slide2_annotations.json").resolve())
        slide_paths.append(SlidePath(slide1_path, slide1_annotations_path))
        slide_paths.append(SlidePath(slide2_path, slide2_annotations_path))

        def load_images_and_annotations():
            from common_urllib.core import load_gdrive_file
            load_gdrive_file('1n8TDA-4gnNSb0fUFhm5i7J5FitfcJVoH', slide1_path)
            load_gdrive_file('1He8XhiRTw6zGiVqlYLtqSGeHiI4th1LX', slide1_annotations_path)
            load_gdrive_file('1BrpN42SZoaz46CjqUQNy2rn5seRBui0w', slide2_path)
            load_gdrive_file('1itDFGs83HiGuSGLNV-G1BVJUOuv1LPtO', slide2_annotations_path)

        load_images_and_annotations()


    def define_my_custom_data():
        # Original big-size slides.
        slide_paths.append(SlidePath(r"D:\temp\slides\slide1.mrxs", r"D:\temp\slides\slide1_annotations.json"))
        slide_paths.append(SlidePath(r"D:\temp\slides\slide5.mrxs", r"D:\temp\slides\slide5_annotations.json"))


    define_example_data()
    # define_my_custom_data()

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
    # The configs defined below specify to:
    # generate patch_label_images from slide1 based on slide1_annotations
    # generate corresponding(geometrically) patch_slide_images from slide1
    # generate patch_label_images from slide2 based on slide2_annotations
    # generate corresponding(geometrically) patch_slide_images from slide2

    # patch size in pixels. Resulting patches will have this size
    patch_size = (512, 512)
    # level of slide. Can be interpreted as level of detail(resolution) with the best detail at 0-level.
    level = 2
    # stride of slicer - distance between subsequent patches
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

    format_str = r"{cfg.slide_path}/{cfg.patch_size[0]},{cfg.patch_size[1]}/{cfg.metadata[name]}/{pos[1]},{pos[0]}_{cfg.level}_{cfg.metadata[name]}"
    # format_str = r"{cfg.slide_path}/{cfg.patch_size[0]},{cfg.patch_size[1]}/{pos[1]},{pos[0]}_{cfg.level}_{cfg.metadata[name]}.png"
    named_ndarrays = patch_responses_to_named_ndarrays(patch_responses, format_str)

    from common.numpy_utils import named_ndarrays_info_str

    # Lets collect data-flow to list and print some info
    named_ndarrays = list(named_ndarrays)
    print(named_ndarrays_info_str(named_ndarrays))

    # We often want to store results of generating patches.
    # It is convenient to store data hierarchically.
    # 3 hierarchial data storages are supported:
    # 1) hdf5 (patches are stored as arrays in a single file)
    # 2) zip archive (patches are stored as arrays in a single file)
    # 3) file system folders (patches are stored as image files in folders)
    #
    # Single file with arrays VS folders with image files.
    # Single file with arrays is easier and faster to:
    # a) manage(delete, copy)
    # b) transfer and synchronize with remote storage (like google disk which can be used from google colab)
    # c) use in processing later (for examplle training model with keras)
    # File system folder with image files is easier to:
    # a) explore
    # b) image-compression often is better than zip-compression for arrays

    from ndarray_persist.save import save_named_ndarrays

    data_path = root_output_path.joinpath("slice_example_results")
    # data_path = root_output_path.joinpath("slice_example_results.zip")
    # data_path = root_output_path.joinpath("slice_example_results.hdf5")
    save_named_ndarrays(named_ndarrays, str(data_path), delete_if_exists=True, verbosity=1)

    # We have just saved both labels and images.
    # Now we can load both labels and images from data store as one data-flow.
    # But it is common case to load labels and images separately, so here is example.
    from ndarray_persist.load.ndarray_loader_factory import NdarrayLoaderFactory

    labels_loader = NdarrayLoaderFactory.from_name_filter(str(data_path), name_pattern=f'.*/{patch_size[0]},{patch_size[1]}/label/.*')
    images_loader = NdarrayLoaderFactory.from_name_filter(str(data_path), name_pattern=f'.*/{patch_size[0]},{patch_size[1]}/image/.*')
    named_labels = list(labels_loader.load_named_ndarrays())
    named_images = list(images_loader.load_named_ndarrays())
    print(named_ndarrays_info_str(named_labels))
    print(named_ndarrays_info_str(named_images))

    # Lets plot (patch_image, patch_label) pairs
    import matplotlib.pyplot as plt
    from common_matplotlib.core import plot_named_ndarrays_tuples_by_batches

    plt.rcParams['figure.figsize'] = (10, 5)

    image_tuples = zip(named_images, named_labels)
    plot_named_ndarrays_tuples_by_batches(image_tuples, ncols=6, tuples_per_plot=12)
