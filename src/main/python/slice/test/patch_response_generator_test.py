from ndarray_persist.ndarray_persist_utils import save_named_ndarrays
from slice.generator.response.patch_response_generator import PatchResponseGenerator
from slice.model.patch_image_config import PatchImageConfig
from slice.model.patch_image_source_config import PatchImageSourceConfig
from slice.patch_response_utils import collect_responses_to_named_ndarrays

if __name__ == '__main__':
    # named_ndarrays = load_named_ndarrays_from_hdf5(h5py_file_path)
    # named_ndarrays = list(named_ndarrays)
    level = 2
    grid_length = 128 * (level) ** 2
    stride = grid_length / 2
    configs = [
        PatchImageSourceConfig(r"D:\temp\slides\slide1.mrxs",
                               level,
                               r"D:\temp\slides\slide1_annotations.json",
                               metadata={"name": "label"}, grid_length=grid_length, stride=stride,
                               dependents=[
                                   PatchImageConfig(r"D:\temp\slides\slide1.mrxs",
                                                    level, metadata={"name": "image"}),
                               ]),
        PatchImageSourceConfig(r"D:\temp\slides\slide5.mrxs",
                               level,
                               r"D:\temp\slides\slide5_annotations.json",
                               metadata={"name": "label"}, grid_length=grid_length, stride=stride,
                               dependents=[
                                   PatchImageConfig(r"D:\temp\slides\slide5.mrxs",
                                                    level, metadata={"name": "image"}),
                               ]),
    ]
    patch_responses = PatchResponseGenerator().create(configs)
    format_str = r"{cfg.slide_path}/{cfg.level}/{cfg.grid_length}/{cfg.metadata[name]}/({pos[0]},{pos[1]})_{cfg.level}_{cfg.metadata[name]}"
    named_ndarrays = collect_responses_to_named_ndarrays(patch_responses, format_str)
    # save_named_ndarrays_to_hdf5(named_ndarrays, h5py_file_path, "w", verbosity=1)
    # save_named_ndarrays(named_ndarrays, r"D:\temp", verbosity=1)
    save_named_ndarrays(named_ndarrays, r"D:\temp\data.hdf5", verbosity=1)
    # save_ndarray_groups_to_zip(pig, format_str, zip_file_path)
    # save_ndarray_groups_to_folder(pig, format_str, folder_path, delete_working_folder=True)
