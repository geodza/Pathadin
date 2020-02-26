import pathlib

from ndarray_persist.ndarray_persist_utils import save_named_ndarrays
from slice.generator.response.patch_response_generator import PatchResponseGenerator
from slice.model.patch_image_config import PatchImageConfig
from slice.model.patch_image_source_config import PatchImageSourceConfig
from slice.patch_response_utils import patch_responses_to_named_ndarrays

if __name__ == '__main__':
    # image=np.random.rand(1000,1000,3)
    # data_folder = pathlib.Path.home().joinpath("temp/slice")
    # io.imsave(str(pathlib.Path(data_folder, 'test_image')), image, check_contrast=False, format='png')
    # data_path = str(pathlib.Path(data_folder, 'data.hdf5'))
    # data_path = data_folder
    # named_ndarrays = list(load_named_ndarrays(str(data_path)))
    # named_ndarrays=named_ndarrays[:10]
    # plot_named_ndarrays_by_batches(zip(named_ndarrays), 10, 50)
    # plot_named_ndarrays(zip(named_ndarrays), 10)
    # plot_named_ndarrays(zip(named_ndarrays), 5)
    # plot_named_ndarrays(zip(named_ndarrays), 2)
    # plot_named_ndarrays(zip(named_ndarrays), 1)

    # named_labels = filter(lambda named_ndarray: named_ndarray[0].endswith("_label"), named_ndarrays)
    # named_images = filter(lambda named_ndarray: named_ndarray[0].endswith("_image"), named_ndarrays)
    # plot_named_ndarrays_tuples_by_batches(zip(named_images, named_labels), 8, 80)

    # named_ndarrays = load_named_ndarrays_from_hdf5(h5py_file_path)
    # named_ndarrays = list(named_ndarrays)
    level = 2
    patch_size = (256, 256)
    # grid_length = 128 * (level) ** 2
    stride = patch_size[0]
    configs = [
        PatchImageSourceConfig(
            r"D:\temp\slides\slide1.mrxs",
            0,
            True,
            r"D:\temp\slides\slide1_annotations.json",
            metadata={"name": "label"},
            patch_size=patch_size,
            stride_x=stride,
            stride_y=stride,
            dependents=[
                PatchImageConfig(
                    r"D:\temp\slides\slide1.mrxs",
                    2,
                    True,
                    metadata={"name": "image"}
                )
            ]
        ),
        PatchImageSourceConfig(r"D:\temp\slides\slide5.mrxs",
                               level,
                               True,
                               r"D:\temp\slides\slide5_annotations.json",
                               metadata={"name": "label"}, patch_size=patch_size,
                               stride_x=stride,
                               stride_y=stride,
                               dependents=[
                                   PatchImageConfig(r"D:\temp\slides\slide5.mrxs",
                                                    level, metadata={"name": "image"}),
                               ]),
    ]
    patch_responses = PatchResponseGenerator().create(configs[1:])
    # format_str = r"{cfg.slide_path}/{cfg.level}/{cfg.grid_length}/{cfg.metadata[name]}/({pos[0]},{pos[1]})_{cfg.level}_{cfg.metadata[name]}.png"
    # format_str = r"{cfg.slide_path}/{cfg.grid_length}/{cfg.metadata[name]}/({pos[0]},{pos[1]})_{cfg.level}_{cfg.metadata[name]}.png"
    format_str = r"{cfg.slide_path}/{cfg.patch_size}/{cfg.metadata[name]}/({pos[1]},{pos[0]})_{cfg.level}_{cfg.metadata[name]}"
    named_ndarrays = patch_responses_to_named_ndarrays(patch_responses, format_str)

    data_folder = pathlib.Path.home().joinpath("temp/slice/256")
    # Choose data storage type (one of hdf5, zip, folder)
    data_path = pathlib.Path(data_folder, 'data.hdf5')
    # data_path = pathlib.Path(data_folder, 'data.zip')
    # data_path = data_folder
    print(data_path)
    named_ndarrays = list(named_ndarrays)
    save_named_ndarrays(named_ndarrays, str(data_path), delete_if_exists=True, verbosity=1)

    # save_named_ndarrays_to_hdf5(named_ndarrays, h5py_file_path, "w", verbosity=1)
    # save_named_ndarrays(named_ndarrays, r"D:\temp", verbosity=1)
    # save_named_ndarrays(named_ndarrays, r"D:\temp\data.hdf5", verbosity=1)
    # save_ndarray_groups_to_zip(pig, format_str, zip_file_path)
    # save_ndarray_groups_to_folder(pig, format_str, folder_path, delete_working_folder=True)
