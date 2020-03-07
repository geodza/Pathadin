import pathlib

from ndarray_persist.ndarray_persist_utils import save_named_ndarrays
from slice.generator.response.patch_response_generator import PatchResponseGenerator
from slice.model.patch_image_config import PatchImageConfig
from slice.model.patch_image_source_config import PatchImageSourceConfig
from slice.patch_response_utils import patch_responses_to_named_ndarrays

if __name__ == '__main__':
    patch_size = (10000, 10000)
    patch_responses = PatchResponseGenerator().create([
        PatchImageSourceConfig(r"D:\temp\slides\slide5.mrxs",
                               2,
                               'L',
                               False,
                               r"D:\temp\slides\slide5_annotations.json",
                               patch_size=patch_size,
                               metadata={"name": "label"},
                               dependents=[
                                   PatchImageConfig(
                                       r"D:\temp\slides\slide5.mrxs",
                                       2,
                                       'RGB',
                                       False,
                                       metadata={"name": "image"},
                                   )
                               ])
    ])
    format_str = r"{cfg.slide_path}/{pos[1]},{pos[0]}_{cfg.level}_level_{cfg.metadata[name]}.jpeg"
    named_ndarrays = list(patch_responses_to_named_ndarrays(patch_responses, format_str))
    data_path = pathlib.Path.home().joinpath("temp/slice5")
    save_named_ndarrays(named_ndarrays, str(data_path), delete_if_exists=False, verbosity=1)
