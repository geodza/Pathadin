from ndarray_persist.ndarray_persist_utils import save_named_ndarrays_to_hdf5, save_named_ndarrays
from slice.generator.response.patch_response_generator import process_pisc, PatchResponseGenerator
from slice.model.patch_image_config import PatchImageConfig
from slice.model.patch_image_source_config import PatchImageSourceConfig
from slice.patch_response_utils import collect_responses_to_named_ndarrays

if __name__ == '__main__':
    # TODO consider image and mask slide shifts
    # TODO consider (level, grid_length, stride) collection?
    # TODO consider imbalanced data
    # TODO consider different objective-powers of slides? Do rescale to some target objective-power?
    # TODO consider color mode conversion hooks (at least at start we dont need RGBA)
    slide_path = r"D:\temp\slides\slide-2019-09-19T18-08-52-R28-S3.mrxs"
    slide_path = r"D:\temp\slides\slide-2019-09-19T18-08-52-R28-S3.mrxs"
    # annotations_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3_annotations5.json"
    annotations_path = r"D:\temp\slides\slide-2019-09-19T18-08-52-R28-S3_annotations8.json"
    # named_ndarrays = load_named_ndarrays_from_hdf5(h5py_file_path)
    # named_ndarrays = list(named_ndarrays)
    level = 2
    grid_length = 256 * (level) ** 2
    stride = grid_length / 4
    # cfg = PatchImageSourceConfig(slide_path, level, annotations_path, metadata={"name": "label"},
    #                              grid_length=grid_length, stride=stride, dependents=[
    #         # PatchImageConfig(slide_path, 0, metadata={"name": "image"}),
    #         # PatchImageConfig(slide_path, 1, metadata={"name": "image"}),
    #         PatchImageConfig(slide_path, level, metadata={"name": "image"}),
    #     ])
    configs = [
        PatchImageSourceConfig(r"D:\temp\slides\slide1.mrxs",
                               level,
                               r"D:\temp\slides\slide1_annotations.json",
                               metadata={"name": "label"}, grid_length=grid_length, stride=stride,
                               dependents=[
                                   PatchImageConfig(r"D:\temp\slides\slide1.mrxs",
                                                    level, metadata={"name": "image"}),
                               ]),
        PatchImageSourceConfig(r"D:\temp\slides\slide2.mrxs",
                               level,
                               r"D:\temp\slides\slide2_annotations.json",
                               metadata={"name": "label"}, grid_length=grid_length, stride=stride,
                               dependents=[
                                   PatchImageConfig(r"D:\temp\slides\slide2.mrxs",
                                                    level, metadata={"name": "image"}),
                               ]),
    ]
    prg = PatchResponseGenerator().create()
    pig = process_pisc(cfg)
    # pig = islice(pig, 10)
    pig = list(pig)
    format_str = r"{cfg.slide_path}/{cfg.level}/{cfg.grid_length}/{cfg.metadata[name]}/({pos[0]},{pos[1]})_{cfg.level}_{cfg.metadata[name]}"
    named_ndarrays = collect_responses_to_named_ndarrays(pig, format_str)
    h5py_file_path = r"D:\temp\data.hdf5"
    zip_file_path = r"D:\temp\data_zip.npz"
    folder_path = r"D:\temp"
    # save_named_ndarrays(,delete_if_ex)
    save_named_ndarrays_to_hdf5(named_ndarrays, h5py_file_path, "w")
    # save_ndarray_groups_to_zip(pig, format_str, zip_file_path)
    # save_ndarray_groups_to_folder(pig, format_str, folder_path, delete_working_folder=True)
    # collect_responses_hdf5(pig, format_str, h5py_file_path)

    # for p in pig:
    #     print(p[0])
