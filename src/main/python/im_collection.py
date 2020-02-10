import imageio
from skimage.io import imread_collection, find_available_plugins

if __name__ == '__main__':
    plugins = find_available_plugins(loaded=True)
    print(plugins)
    grid_length=256
    image_dir = f'{grid_length}/train/image/'
    # image_dir=r"D:/dieyepy/srimcc/main/python/256/train_images_zip_manual.zip"
    # imc=imread_collection(imageio.core.urlopen(image_dir))
    imc=imread_collection(f'{image_dir}/*.png')
    # mi=imageio.mimread(image_dir)
    # imageio.core.urlopen()
    # print(imc)
    imcc=imc.concatenate()
    print(imcc.shape)

