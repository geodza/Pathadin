

if __name__ == '__main__':
    # %tensorflow_version 1.x
    # !git clone https://gitlab.com/Digipathology/Pathadin.git
    # We need to clone project and add it to sys.path (we haven't installable packages yet)
    # path_to_project = r'D:\projects\Pathadin\src\main\python'
    path_to_project = 'Pathadin/src/main/python'
    import pathlib, sys

    sys.path.append(str(pathlib.Path(path_to_project).resolve()))

    # Warning.
    # Model-training process is computationally heavy.
    # We recommend you to run it on machine with powerful GPU.
    # This example runs in 15 minutes on google-colab while on laptop it may take hours.
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
    # It means that in main application you can specify keras model as a filter for annotation
    # and it will perform segmentation(stroma/gldands) of region of this annotation on slide in real-time.
    import numpy as np

    # We define working root folder for convenience
    root_path = pathlib.Path.home().joinpath("temp/pathadin_examples/data")
    root_path.mkdir(parents=True, exist_ok=True)

    # Define path to patches (both images and labels).
    # Example of generating and storing patches from slide images can be found in "slice_example".
    # patches_path = root_path.joinpath("slice_patches.h5")
    patches_path = root_path.joinpath("slice_patches")
    patches_path.parent.mkdir(parents=True, exist_ok=True)


    # In case you haven't results from "slice_example" we have some predefined patches that you can load.
    def load_example_patches():
        from common_urllib.core import load_gdrive_file
        load_gdrive_file("1-8nFK5Q0QbR9pW3u_bB83MQRtHJl2qae", str(patches_path))


    # load_example_patches()

    from common.itertools_utils import peek
    # Recipe for training neural networks: http://karpathy.github.io/2019/04/25/recipe/
    # states: "Become one with the data".
    # It is super important. So ALWAYS check your data.
    # At least you should:
    # 1. Check shape, dtype, min, max
    # 2. Check Y classes distribution.
    #       If there is a big class imbalance then you probably should perform some balancing of your data.
    #       The simplest methods are undersampling and oversampling: https://machinelearningmastery.com/data-sampling-methods-for-imbalanced-classification/
    # We prepare our example to be augmentation-ready (using ImageDataGenerator).
    # But for simplicity we do not use augmentation here.

    # Now we define u-net model with quite common settings.
    from keras.optimizers import Adam
    from common_keras.assert_utils import assert_model_input, assert_model_output
    from common_keras.unet import get_unet
    from keras_preprocessing.image import ImageDataGenerator

    augment_kwargs = dict()
    target_size=(512,512)
    batch_size = 20
    seed = 1

    labels_name_pattern = f'.*/label/.*'
    images_name_pattern = f'.*/image/.*'

    named_labels = NdarrayLoaderFactory.from_name_filter(str(patches_path), name_pattern=labels_name_pattern).load_named_ndarrays()
    named_images = NdarrayLoaderFactory.from_name_filter(str(patches_path), name_pattern=images_name_pattern).load_named_ndarrays()
    solid_uniques = defaultdict(list)
    mixed_label_image_names=[]
    for named_label, named_image in zip(named_labels, named_images):
        u = np.unique(named_label[1])
        if len(u) == 1:
            # uniques[u[0]] = uniques.get(u[0], 0) + 1
            solid_uniques[u[0]].append((named_label[0], named_image[0]))
        else:
            mixed_label_image_names.append((named_label[0], named_image[0]))
    print(solid_uniques)

    min_count=len(next(iter(solid_uniques.values())))
    for color, names in solid_uniques.items():
        n=len(names)
        if n<min_count:
            min_count=n

    import random
    random.seed=seed
    label_image_names=[]
    for color in solid_uniques:
        random.shuffle(solid_uniques[color])
        label_image_names.extend(solid_uniques[color][:min_count])
    label_image_names.extend(mixed_label_image_names)
    label_names=[n[0] for n in label_image_names]
    image_names=[n[1] for n in label_image_names]


    import pandas
    imagedf=pandas.DataFrame(image_names, columns=['filename'])
    labeldf=pandas.DataFrame(label_names, columns=['filename'])
    image_generator = ImageDataGenerator(rescale=1./255,**augment_kwargs) \
        .flow_from_dataframe(imagedf, str(patches_path.joinpath('patches')), target_size=target_size,
                             color_mode='rgb', class_mode=None, batch_size=batch_size, seed=seed)
    label_generator = ImageDataGenerator(rescale=1./255, **augment_kwargs) \
        .flow_from_dataframe(labeldf, str(patches_path.joinpath('patches')), target_size=target_size,
                             color_mode='grayscale', class_mode=None, batch_size=batch_size, seed=seed)
    # image_generator = ImageDataGenerator(**augment_kwargs)\
    #     .flow_from_directory(str(patches_path.joinpath('patches/train_image')),target_size=target_size,
    #                          color_mode='rgb', class_mode=None, batch_size=batch_size,seed=seed)
    # label_generator = ImageDataGenerator(**augment_kwargs)\
    #     .flow_from_directory(str(patches_path.joinpath('patches/train_label')),target_size=target_size,
    #                          color_mode='grayscale', class_mode=None, batch_size=batch_size,seed=seed)
    sample_generator = zip(image_generator,label_generator)


    first_sample_batch, samples_train=peek(sample_generator)
    first_sample_batch=list(first_sample_batch)
    # patch_shape = X.shape[-3:]
    patch_shape = first_sample_batch[0].shape[-3:]
    n_filters = 8
    model = get_unet(patch_shape, n_filters=n_filters)
    model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    # One more check. Ensure our data is compatible with model definition.
    # These statements asserts ndarrays shapes and dtypes.
    # assert_model_input(model, X)
    # assert_model_output(model, Y)

    # Define path where the model will be saved.
    # You can load it afterwards in another program and use it for prediction.
    model_path = root_path.joinpath('segmentation_model.h5')

    from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

    callbacks = [
        ReduceLROnPlateau(factor=0.1, patience=5, min_lr=0.000001, verbose=1, monitor='val_loss'),
        ModelCheckpoint(str(model_path), verbose=1, monitor='val_loss', save_best_only=True, save_weights_only=False),
        EarlyStopping(patience=10, verbose=1, monitor='val_loss'),
    ]

    epochs = 50
    steps_per_epoch = len(label_image_names) / batch_size
    # samples = data_generator.flow(X_train, Y_train, batch_size=batch_size, shuffle=True)
    history = model.fit_generator(samples_train, steps_per_epoch=steps_per_epoch, epochs=epochs, callbacks=callbacks)

    # Plot learning process.
    # We dont seek for excellent results.
    # We just want to check some basic indicators of doing things right like:
    # 1) Train and test losses should decrease
    # 2) Train and test losses should not too diverge
    # 3) Train and test losses should not be too similar
    import matplotlib.pyplot as plt
    from common_matplotlib.core import plot_image_tuples_by_batches

    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()

    # And finally we will check results visually.
    # Let's visualize predictions on train data
    plt.rcParams['figure.figsize'] = (10, 5)

    # Y_tain_predict = model.predict(X_train)
    # print("Training data(image, true label, predicted label):")
    # plot_image_tuples_by_batches(zip(X_train, Y_train, Y_tain_predict), ncols=6, tuples_per_plot=8)
    #
    # # Let's visualize predictions on test data
    # Y_test_predict = model.predict(X_test)
    # print("Test data(image, true label, predicted label):")
    # plot_image_tuples_by_batches(zip(X_test, Y_test, Y_test_predict), ncols=6, tuples_per_plot=8)

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

