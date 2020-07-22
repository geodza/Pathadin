if __name__ == '__main__':
    # %tensorflow_version 1.x
    # !git clone https://gitlab.com/Digipathology/Pathadin.git
    # We need to clone project and add it to sys.path (we haven't installable packages yet)
    # import shutil
    # shutil.rmtree('Pathadin')
    # !git clone https://gitlab.com/Digipathology/Pathadin.git
    # !cd Pathadin && git checkout a4f1d8e378fe6b95b8475b80833049d3f0dd12c4
    path_to_project = 'Pathadin/src/main/python'
    import pathlib, sys

    sys.path.append(str(pathlib.Path(path_to_project).resolve()))

    # Warning.
    # Model-training process is computationally heavy.
    # We recommend you to run it on machine with powerful GPU.
    # This example runs in 20-30 minutes on google-colab while on laptop it may take hours.
    #
    # Warning.
    # Our goal is not to investigate (research) some problem with some deep-learning method.
    # Our goal is to show how deep-learning can be applied to our main application and how it can be used in pathologist workflow.
    #
    # To achieve the goal we have chosen a rather simple task of stroma/glands segmentation.
    # Here stroma/glands segmentation means for given image predict label (stroma or glands) for every pixel in image.
    # Quite common model for segmentation task is u-net.
    # Good introduction and implementation of u-net can be found here: https://towardsdatascience.com/understanding-semantic-segmentation-with-unet-6be4f42d4b47
    #
    # Model will be trained on samples where sample is a (patch_image, patch_label) tuple.
    # patch_label - binary image as a result of labeling annotation regions on a slide.
    # patch_image - corresponding(geometrically) color image from slide.
    # After trained model will be saved you can then load it from main application and use it as an image filter.
    # It means that in main application you can specify keras model as a filter for annotation
    # and it will perform segmentation(stroma/glands) of region of this annotation on slide in real-time.
    #
    # We define working root folder for convenience.
    root_path = pathlib.Path.home().joinpath("temp/pathadin_examples/segmentation_example/data")
    root_path.mkdir(parents=True, exist_ok=True)

    # Define path to patches (both images and labels).
    # Example of generating and storing patches from slide images can be found in "slice_example.ipynb".
    # In slice_example we have generated image/label patches and saved them in slice_example_patches.zip archive.
    # Screenshot of patches archive: https://www.pathadin.eu/pathadin/pathadin_examples/segmentation_example/slice_example_patches_screen.png
    patches_dir = root_path.joinpath("slice_example_patches")
    patches_dir.parent.mkdir(parents=True, exist_ok=True)


    # In case you haven't results from "slice_example.ipynb" you can download it (~70Mb).
    def load_example_patches():
        patches_url = 'https://www.pathadin.eu/pathadin/pathadin_examples/segmentation_example/data/slice_example_patches.zip'
        patches_archive_path = str(patches_dir) + ".zip"
        from common_urllib.core import load_file
        load_file(patches_url, patches_archive_path, force=True)
        import zipfile
        with zipfile.ZipFile(patches_archive_path, "r") as zip_ref:
            zip_ref.extractall(str(patches_dir))


    load_example_patches()

    # Recipe for training neural networks is very useful: http://karpathy.github.io/2019/04/25/recipe/
    # Now we define u-net model with quite common settings.
    from keras.optimizers import Adam
    from common_keras.unet import get_unet
    from keras_preprocessing.image import ImageDataGenerator

    # Archive with patches contains both patch_images(rgb) and patch_labels(binary) so lets define pattern to separate them.
    labels_name_pattern = f'.*/label/.*'
    images_name_pattern = f'.*/image/.*'

    import numpy as np
    import random
    import pandas
    from collections import defaultdict
    from ndarray_persist.load.ndarray_loader_factory import NdarrayLoaderFactory

    # Load patch_labels and patch_images.
    named_labels = NdarrayLoaderFactory.from_name_filter(str(patches_dir) + '.zip', name_pattern=labels_name_pattern).load_named_ndarrays()
    named_images = NdarrayLoaderFactory.from_name_filter(str(patches_dir) + '.zip', name_pattern=images_name_pattern).load_named_ndarrays()
    # If there is a class imbalance then you probably should perform some balancing of your data.
    # The simplest methods are undersampling and oversampling: https://machinelearningmastery.com/data-sampling-methods-for-imbalanced-classification/
    # We will count solid-color(fully black or fully white) patches.
    solid_label_image_names = defaultdict(list)
    mixed_label_image_names = []
    for named_label, named_image in zip(named_labels, named_images):
        label_colors = np.unique(named_label[1])
        if len(label_colors) == 1:
            solid_label_image_names[label_colors[0]].append((named_label[0], named_image[0]))
        else:
            mixed_label_image_names.append((named_label[0], named_image[0]))
    solid_counts = {color: len(names) for color, names in solid_label_image_names.items()}
    # Like some kind of class balancing we will take equal amount of fully black and fully white patches.
    min_solid_count = min(solid_counts.values())
    print(f"label_patches with both colors count: {len(mixed_label_image_names)}")
    print(f"label_patches with one color count (label_color:count): {solid_counts}")
    print(f"label_patches with one color count to keep: {min_solid_count}")

    # We prepare our example to be augmentation-ready (using ImageDataGenerator).
    # But for simplicity we do not use augmentation here.
    augment_kwargs = dict()
    seed = 1
    random.seed = seed
    label_image_names = []
    for color in solid_label_image_names:
        random.shuffle(solid_label_image_names[color])
        label_image_names.extend(solid_label_image_names[color][:min_solid_count])
    label_image_names.extend(mixed_label_image_names)
    label_names = [n[0] for n in label_image_names]
    image_names = [n[1] for n in label_image_names]

    # flow_from_dataframe is friendly for RAM - it will load images by batches in iterable style.
    imagedf = pandas.DataFrame(image_names, columns=['filename'])
    labeldf = pandas.DataFrame(label_names, columns=['filename'])
    target_size = (512, 512)
    patch_shape = (512, 512, 3)
    batch_size = 10
    image_batch_generator = ImageDataGenerator(rescale=1. / 255, **augment_kwargs) \
        .flow_from_dataframe(imagedf, str(patches_dir), target_size=target_size,
                             color_mode='rgb', class_mode=None, batch_size=batch_size, seed=seed)
    label_batch_generator = ImageDataGenerator(rescale=1. / 255, **augment_kwargs) \
        .flow_from_dataframe(labeldf, str(patches_dir), target_size=target_size,
                             color_mode='grayscale', class_mode=None, batch_size=batch_size, seed=seed)
    # Sample is an (image, label) pair
    sample_batch_generator = zip(image_batch_generator, label_batch_generator)

    n_filters = 8
    model = get_unet(patch_shape, n_filters=n_filters)
    model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])

    # Define path where the model will be saved.
    # You can load it afterwards in another program and use it for prediction.
    model_path = root_path.joinpath('segmentation_example_model.h5')

    from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

    callbacks = [
        ReduceLROnPlateau(factor=0.1, patience=5, min_lr=0.000001, verbose=1, monitor='loss'),
        ModelCheckpoint(str(model_path), verbose=1, monitor='loss', save_best_only=True, save_weights_only=False),
        EarlyStopping(patience=10, verbose=1, monitor='loss'),
    ]

    epochs = 70
    steps_per_epoch = len(label_image_names) / batch_size
    history = model.fit_generator(sample_batch_generator, steps_per_epoch=steps_per_epoch, epochs=epochs, callbacks=callbacks)

    # Plot learning process.
    # We dont seek for excellent results.
    # We just want to check some basic indicators of doing things right.
    import matplotlib.pyplot as plt

    plt.rcParams['figure.figsize'] = (10, 5)

    plt.plot(history.history['loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train'], loc='upper left')
    plt.show()

    # And finally we will check results visually.
    # Let's visualize predictions on some samples.

    import itertools

    X = itertools.chain.from_iterable(image_batch_generator)
    Y = itertools.chain.from_iterable(label_batch_generator)
    X = np.asarray(list(itertools.islice(X, 100)))
    Y = np.asarray(list(itertools.islice(Y, 100)))
    Y_predict = model.predict(X)
    print("Image, True label, Predicted label:")
    from common_matplotlib.core import plot_image_tuples_by_batches

    plot_image_tuples_by_batches(zip(X, Y, Y_predict), ncols=6, tuples_per_plot=8)

    # To download file to localhost you can download it as "Browser download file"
    # or mount your google drive and copy file to it:
    # https://colab.research.google.com/notebooks/io.ipynb
    # Another option is to mount google drive in the beginning of example
    # and make all io in some directory of gdrive.
    #
    # We will mount gdrive and copy file to gdrive directory.
    # from google.colab import drive
    # drive.mount('/content/drive')
    # gdrive_path = pathlib.Path('/content/drive/My Drive/pathadin_examples/data', model_path.name)
    # gdrive_path.parent.mkdir(parents=True, exist_ok=True)
    # import shutil
    # shutil.copy2(str(model_path), gdrive_path)
