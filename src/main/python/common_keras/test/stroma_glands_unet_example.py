

if __name__ == '__main__':
    # Warning.
    # Model-learning process is computationally heavy.
    # We recommend you to run it on machine with powerful GPU.
    # This example runs in minutes on google-colab while on laptop it may take hours.
    #
    # Warning.
    # Our goal is not to investigate (research) some problem with some deep-learning method.
    # Our goal is to show how deep-learning can be applied to our main application and how it can be used in pathologist workflow.
    #
    # To achieve the goal we have chosen a rather simple task of stroma/glands segmentation.
    # Here stroma/glands segmentation means giving image predict label (stroma or glands) for every pixel in image.
    # Quite common model for segmentation task is u-net.
    # Good introduction and implementation of u-net can be found here: https://towardsdatascience.com/understanding-semantic-segmentation-with-unet-6be4f42d4b47
    #
    # Model will be trained on samples where sample is a (patch_image, patch_label) tuple.
    # patch_label - binary image as a result of labeling annotation regions on a slide.
    # patch_image - corresponding(geometrically) color image from slide.
    # After trained model will be saved you can then load it from main application and use it as an image filter.
    # It means that in application you can specify keras model as a filter for annotation
    # and it will perform segmentation(stroma/gldands) of region of this annotation on slide.
    import matplotlib.pyplot as plt
    import pathlib, sys
    import numpy as np
    from urllib.request import urlretrieve

    plt.rcParams['figure.figsize'] = (20, 10)

    # We need to clone project and add it to sys.path (we haven't installable packages yet)
    # Git clone will work after opening access
    # !git clone git@gitlab.com:Digipathology/dieyepy.git
    path_to_project = r'D:\projects\dieyepy\src\main\python'
    # path_to_project = 'dieyepy/src/main/python'
    sys.path.append(str(pathlib.Path(path_to_project).resolve()))

    # We define working root folder for convenience
    root_path = pathlib.Path.home().joinpath("temp/slice_example1")

    # Define path to patches (both images and labels).
    # Example of generating and storing patches from slide images can be found in "slice_example".
    patches_path = root_path.joinpath("slice_example_results.hdf5")
    patches_path.mkdir(parents=True, exist_ok=True)

    # In case you haven't results from "slice_example" we have some predefined patches that you can load.
    def load_patches():
        if not pathlib.Path(patches_path).exists():
            urlretrieve("https://drive.google.com/uc?id=1q842Tv1DZ3vp7068465JNujcencLSZWS", str(patches_path))


    load_patches()

    from ndarray_persist.ndarray_persist_utils import load_named_ndarrays, NamedNdarray

    patch_size = (512, 512)
    # Images and labels were saved as named ndarrays in one file.
    # To load labels and images separately we can load them by name pattern.
    labels_name_pattern = f'.*/{patch_size[0]},{patch_size[1]}/label/.*'
    images_name_pattern = f'.*/{patch_size[0]},{patch_size[1]}/image/.*'
    named_labels = list(load_named_ndarrays(str(patches_path), name_pattern=labels_name_pattern))
    named_images = list(load_named_ndarrays(str(patches_path), name_pattern=images_name_pattern))

    from common.numpy_utils import print_named_ndarrays_info

    # Let's print what we have load.
    print_named_ndarrays_info(named_labels)
    print_named_ndarrays_info(named_images)


    # Named ndarrays are convenience for storing.
    # But now we need to prepare data for keras.
    def convert_label(named_ndarray: NamedNdarray) -> np.ndarray:
        label = named_ndarray[1]
        return np.atleast_3d(np.squeeze(label[..., 0] // 255)).astype(np.float32)


    def convert_image(named_ndarray: NamedNdarray) -> np.ndarray:
        image = named_ndarray[1]
        return np.atleast_3d(np.squeeze(image / 255)).astype(np.float32)


    labels = np.asarray([convert_label(label) for label in named_labels])
    images = np.asarray([convert_image(image) for image in named_images])

    from common.numpy_utils import print_ndarrays_info

    # Always check your data.
    # 1. Check shape, dtype, min, max
    # 2. Check Y classes distribution.
    #       If there is a big class imbalance then you probably should perform some balancing of your data.
    #       The simplest methods are undersampling and oversampling: https://machinelearningmastery.com/data-sampling-methods-for-imbalanced-classification/
    print_ndarrays_info(labels)
    print_ndarrays_info(images)

    # We will
    from sklearn.model_selection import train_test_split

    X, Y = images, labels
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25)

    # Now we define u-net model with quite common settings.
    from keras.optimizers import Adam
    from common_keras.assert_utils import assert_model_input, assert_model_output
    from common_keras.unet import get_unet

    patch_shape = X.shape[-3:]
    model = get_unet(patch_shape, n_filters=1)
    model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    # One more check. Ensure our data is compatible with model definition.
    # These statements asserts ndarrays shapes and dtypes.
    assert_model_input(model, X)
    assert_model_output(model, Y)

    # Define path where the model will be saved.
    # You can load it afterwards in another script and use it for prediction.
    model_path = root_path.joinpath('unet_model.h5')

    from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

    # We define callbacks to:
    callbacks = [
        ReduceLROnPlateau(factor=0.1, patience=5, min_lr=0.00001, verbose=1, monitor='val_loss'),
        ModelCheckpoint(str(model_path), verbose=1, monitor='val_loss', save_best_only=True, save_weights_only=False),
        EarlyStopping(patience=10, verbose=1, monitor='val_loss'),
    ]

    from keras.preprocessing.image import ImageDataGenerator

    # We prepare our example to be augmentation-ready (using ImageDataGenerator).
    # But for simplicity we do not use augmentation here.
    augment_kwargs = dict()
    data_generator = ImageDataGenerator(**augment_kwargs)

    batch_size = 3
    # batch_size=6
    epochs = 3
    steps_per_epoch = len(X_train) / batch_size
    samples = data_generator.flow(X_train, Y_train, batch_size=batch_size, shuffle=True)
    history = model.fit_generator(samples, steps_per_epoch=steps_per_epoch, epochs=epochs, callbacks=callbacks,
                                  validation_data=(X_test, Y_test))

    # Plot learning process.
    # We dont seek for excellent results.
    # We just want to check some basic indicators of doing things right like:
    # 1) Train and test losses should decrease
    # 2) Train and test losses should not too diverge
    # 3) Train and test losses should not be too similar
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()

    # And finally we will check results visually.
    # Let's visualize predictions on train data
    from common_matplotlib.core import plot_image_tuples_by_batches
    Y_tain_predict = model.predict(X_train)
    plot_image_tuples_by_batches(zip(X_train, Y_train, Y_tain_predict), ncols=6, tuples_per_plot=20)

    # Let's visualize predictions on test data
    Y_test_predict = model.predict(X_test)
    plot_image_tuples_by_batches(zip(X_test, Y_test, Y_test_predict), ncols=6, tuples_per_plot=20)
