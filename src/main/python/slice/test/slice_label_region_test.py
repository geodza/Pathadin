import pathlib

from ndarray_persist.ndarray_persist_utils import save_named_ndarrays
from slice.generator.response.patch_response_generator import PatchResponseGenerator
from slice.model.patch_image_config import PatchImageConfig
from slice.model.patch_image_source_config import PatchImageSourceConfig
from slice.patch_response_utils import patch_responses_to_named_ndarrays

if __name__ == '__main__':
    slide1_path = r"C:\Users\User\temp\slice\patches\slide1_region.jpg"
    slide1_annotations_path = r"C:\Users\User\temp\slice\patches\slide1_annotations46.json"
    responses = PatchResponseGenerator().create([
        PatchImageSourceConfig(
            slide_path=slide1_path,
            level=0,
            annotations_path=slide1_annotations_path,
            metadata={"name": "label"},
            patch_size=(-1, -1),
            dependents=[
                PatchImageConfig(
                    slide_path=slide1_path,
                    level=0,
                    metadata={"name": "image"}
                )
            ])
    ])
    data_path = str(pathlib.Path.home().joinpath("temp/slice"))
    format_str = "({pos[1]},{pos[0]})_{cfg.patch_size}_{cfg.metadata[name]}.jpeg"
    named_ndarrays = list(patch_responses_to_named_ndarrays(responses, format_str))
    save_named_ndarrays(named_ndarrays, data_path, delete_if_exists=False)
