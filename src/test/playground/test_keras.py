import itertools

import numpy as np
import skimage
from keras_preprocessing.image import array_to_img
import matplotlib.pyplot as plt
from common_matplotlib.core import plot_named_ndarrays_tuples_by_batches
from filter.keras.keras_model_filter import load_keras_model


def convert_image(ndarray: np.ndarray) -> np.ndarray:
	# return np.atleast_3d(np.squeeze(ndarray / 255)).astype(np.float32)
	return np.atleast_3d(np.squeeze(ndarray)).astype(np.float32)


if __name__ == '__main__':
	# patch_path = r'E:\slides\patches\63488,41984_2_image.jpg'
	# img = Image.open(patch_path)
	# ndimg = np.array(img)
	# print(ndimg)

	model_path = r'C:\Users\DIMA\Downloads\softmax_4_classes.h5'
	model_path2 = r'C:\Users\DIMA\Downloads\Stroma&Glands.h5'
	keras_model = load_keras_model(model_path)
	keras_model2 = load_keras_model(model_path2)

	print(keras_model.summary())
	print(keras_model2.summary())
	input_shape = keras_model.input_shape[1:]
	input_size = input_shape[:2]

	patches_path = r'E:\slides\patches\slice_example_patches.zip'
	from ndarray_persist.load.ndarray_loader_factory import NdarrayLoaderFactory

	images_loader = NdarrayLoaderFactory.from_name_filter(str(patches_path), name_pattern=f'.*image.*')
	named_images = images_loader.load_named_ndarrays()

	named_masks = []
	for i, (name, ndimg) in enumerate(itertools.islice(named_images, 50)):
		patch_ndarray = convert_image(ndimg)
		patch_images_batch = np.array([patch_ndarray])
		patch_masks_batch = keras_model.predict(patch_images_batch)
		patch_mask = patch_masks_batch[0]
		patch_mask = np.argmax(patch_mask, axis=-1).astype(dtype=np.float32)
		patch_mask = np.expand_dims(patch_mask, axis=-1)
		print(f'{i}:{name}, np.count_nonzero(patch_mask != 3)', np.count_nonzero(patch_mask != 3))
		if np.count_nonzero(patch_mask != 3) > 100:
			print(patch_mask)
		patch_label_max = np.max(patch_mask)
		if patch_label_max != 0:
			patch_mask /= patch_label_max

		# Get the color map by name:
		cm = plt.get_cmap('viridis')
		# Apply the colormap like a function to any array:
		colored_image = cm(patch_mask)
		skimage_patch = skimage.img_as_ubyte(patch_mask)
		plt.imshow(np.squeeze(skimage_patch))
		plt.show()
		print(1)
		patch_img = array_to_img(patch_mask)
		# patch_img.show()
		patch_img_arr = np.array(patch_img)
		named_masks.append((name, patch_img_arr))

	image_tuples = zip(named_images, named_masks)
	image_tuples_limit = 300
	image_tuples = itertools.islice(image_tuples, image_tuples_limit)
	print(f"Image-label pairs (limit by {image_tuples_limit}):")
	plot_named_ndarrays_tuples_by_batches(image_tuples, ncols=6, tuples_per_plot=12)
