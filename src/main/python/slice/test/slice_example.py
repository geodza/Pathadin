from common_urllib.core import load_gdrive_file

if __name__ == '__main__':
    import pathlib
    import sys

    import matplotlib.pyplot as plt

    plt.rcParams['figure.figsize'] = (20, 10)
    # Install required binaries and packages
    #
    # !apt-get install openslide-tools
    # !pip install scikit-image opencv-python shapely h5py openslide-python dataclasses pydantic
    #
    # We need to clone project and add it to sys.path (we haven't installable packages yet)
    # Git clone will work after opening access
    # !git clone git@gitlab.com:Digipathology/dieyepy.git
    path_to_project = r'D:\projects\dieyepy\src\main\python'
    # path_to_project = 'dieyepy/src/main/python'
    sys.path.append(str(pathlib.Path(path_to_project).resolve()))

    # We define working root folder for convenience
    root_path = pathlib.Path.home().joinpath("temp/slice_example3")
    root_input_path = root_path.joinpath("input")
    root_output_path = root_path.joinpath("output")
    root_input_path.mkdir(parents=True, exist_ok=True)
    root_output_path.mkdir(parents=True, exist_ok=True)

    # Original mrxs slide is about 4gb memory.
    # To make example more reproducible and lightweight we cut a small region from it and interpret it as a real slide.
    # Define paths to slides and annotations
    slide1_path = str(root_input_path.joinpath("slide1.jpeg").resolve())
    slide1_annotations_path = str(root_input_path.joinpath("slide1_annotations.json").resolve())
    slide2_path = str(root_input_path.joinpath("slide2.jpeg").resolve())
    slide2_annotations_path = str(root_input_path.joinpath("slide2_annotations.json").resolve())


    # Original big-size slides.
    # slide1_path = r"D:\temp\slides\slide1.mrxs"
    # slide1_annotations_path = r"D:\temp\slides\slide1_annotations.json"
    # slide2_path = r"D:\temp\slides\slide5.mrxs"
    # slide2_annotations_path = r"D:\temp\slides\slide5_annotations.json"

    def load_images_and_annotations():
        load_gdrive_file('1n8TDA-4gnNSb0fUFhm5i7J5FitfcJVoH', slide1_path)
        load_gdrive_file('1He8XhiRTw6zGiVqlYLtqSGeHiI4th1LX', slide1_annotations_path)
        load_gdrive_file('1BrpN42SZoaz46CjqUQNy2rn5seRBui0w', slide2_path)
        load_gdrive_file('1itDFGs83HiGuSGLNV-G1BVJUOuv1LPtO', slide2_annotations_path)


    load_images_and_annotations()
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
    level = 0
    # stride of slicer - distance between subsequent patches
    stride_x, stride_y = patch_size[0] // 2, patch_size[1] // 2

    from slice.model.patch_image_config import PatchImageConfig
    from slice.model.patch_image_source_config import PatchImageSourceConfig

    configs = [
        PatchImageSourceConfig(
            slide_path=slide1_path,
            level=level,
            target_color_mode='L',
            annotations_path=slide1_annotations_path,
            metadata={"name": "label"},
            patch_size=patch_size,
            stride_x=stride_x,
            stride_y=stride_y,
            dependents=[
                PatchImageConfig(
                    slide_path=slide1_path,
                    level=level,
                    target_color_mode='RGB',
                    metadata={"name": "image"}
                )
            ]
        ),
        PatchImageSourceConfig(
            slide_path=slide2_path,
            level=level,
            target_color_mode='L',
            annotations_path=slide2_annotations_path,
            metadata={"name": "label"},
            patch_size=patch_size,
            stride_x=stride_x,
            stride_y=stride_y,
            dependents=[
                PatchImageConfig(
                    slide_path=slide2_path,
                    level=level,
                    target_color_mode='RGB',
                    metadata={"name": "image"}
                )
            ]
        )
    ]

    # PatchResponseGenerator processes configs one by one generating patches and puts these patches into
    # one data-flow: Iterable[PatchResponse]
    from slice.generator.response.patch_response_generator import PatchResponseGenerator

    patch_responses = PatchResponseGenerator().create(configs)

    # Then we convert every patch_response to named_ndarray - Tuple[str, np.ndarray]
    # We select name format convenient for saving/loading to/from disk.
    from slice.patch_response_utils import patch_responses_to_named_ndarrays

    format_str = r"{cfg.slide_path}/{cfg.patch_size[0]},{cfg.patch_size[1]}/{cfg.metadata[name]}/{pos[1]},{pos[0]}_{cfg.level}_{cfg.metadata[name]}.png"
    named_ndarrays = patch_responses_to_named_ndarrays(patch_responses, format_str)


    # Lets collect data-flow to list and print some info
    def print_named_ndarrays_info(named_ndarrays):
        print(f"arrays count: {len(named_ndarrays)}")
        if len(named_ndarrays):
            print(f"1-st array (name,shape): {(named_ndarrays[0][0], named_ndarrays[0][1].shape)}")


    named_ndarrays = list(named_ndarrays)
    print_named_ndarrays_info(named_ndarrays)

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
    #
    from ndarray_persist.ndarray_persist_utils import save_named_ndarrays

    # data_path = root_output_path.joinpath("results")
    # data_path = root_output_path.joinpath("results.zip")
    data_path = root_output_path.joinpath("slice_example_results2.hdf5")
    save_named_ndarrays(named_ndarrays, str(data_path), delete_if_exists=True, verbosity=1)

    # We have just saved both labels and images.
    # Now we can load both labels and images from data store as one data-flow: load_named_ndarrays(data_path)
    # But it is common case to load labels and images separately, so here is example.
    from ndarray_persist.ndarray_persist_utils import load_named_ndarrays

    named_labels = load_named_ndarrays(str(data_path), name_pattern=f'.*/{patch_size[0]},{patch_size[1]}/label/.*')
    named_images = load_named_ndarrays(str(data_path), name_pattern=f'.*/{patch_size[0]},{patch_size[1]}/image/.*')
    named_labels, named_images = list(named_labels), list(named_images)
    print_named_ndarrays_info(named_labels)
    print_named_ndarrays_info(named_images)

    # Lets plot (patch_image, patch_label) pairs
    from common_matplotlib.core import plot_named_ndarrays_tuples_by_batches

    image_tuples = zip(named_images, named_labels)
    plot_named_ndarrays_tuples_by_batches(image_tuples, ncols=10, tuples_per_plot=20)
