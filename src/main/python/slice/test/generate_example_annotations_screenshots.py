import pathlib

from shapely.geometry import box

from ndarray_persist.save import save_named_ndarrays
from slice.generator.image.config_patch_image_generator import ConfigPatchImageGenerator
from slice.model.patch_image_config import PatchImageConfig
from slice.patch_response_utils import patch_images_to_named_ndarrays

if __name__ == '__main__':
	pos = (41472 - 256 * 4, 62976 - 256 * 4)
	rect = box(*pos, 43520 + 256 * 4, 65536 + 256 * 4)
	generator = ConfigPatchImageGenerator(
		PatchImageConfig(r"D:\temp\slides\slide1.mrxs", 0, 'RGB', rescale_result_image=False))
	images = list(generator.create([(pos, rect)]))
	data_path = str(pathlib.Path.home().joinpath("temp/slice"))
	named_ndarrays = list(patch_images_to_named_ndarrays(images, "region1.jpeg"))
	save_named_ndarrays(named_ndarrays, data_path)

	pos = (30720 - 256 * 4, 129536 - 256 * 4)
	rect = box(*pos, 33530 + 256 * 4, 132096 + 256 * 4)
	generator = ConfigPatchImageGenerator(
		PatchImageConfig(r"D:\temp\slides\slide5.mrxs", 0, 'RGB', rescale_result_image=False))
	images = list(generator.create([(pos, rect)]))
	data_path = str(pathlib.Path.home().joinpath("temp/slice"))
	named_ndarrays = list(patch_images_to_named_ndarrays(images, "region5.jpeg"))
	save_named_ndarrays(named_ndarrays, data_path)
