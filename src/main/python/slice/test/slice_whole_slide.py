import matplotlib.pyplot as plt

from slice.generator.response.patch_response_generator import PatchResponseGenerator
from slice.model.patch_image_source_config import PatchImageSourceConfig
from slice.patch_response_utils import patch_responses_to_named_ndarrays

if __name__ == '__main__':
    # (-1,-1) means whole image
    patch_size = (-1, -1)
    patch_responses = PatchResponseGenerator().create([
        PatchImageSourceConfig(r"D:\temp\slides\slide1.mrxs", 4, 'RGB', False, None, patch_size=patch_size)
    ])
    format_str = r"{cfg.slide_path}/whole_image_from_{cfg.level}_level.jpeg"
    named_ndarrays = list(patch_responses_to_named_ndarrays(patch_responses, format_str))
    # data_path = pathlib.Path.home().joinpath("temp/slice")
    # save_named_ndarrays(named_ndarrays, str(data_path), delete_if_exists=False, verbosity=1)
    image = named_ndarrays[0][1]
    plt.imshow(image)
    plt.show()
