from slide_viewer.ui.slide.widget.annotation_filter_processor import load_keras_model

if __name__ == '__main__':
    model_path = r"D:\slide_cbir_47\temp\slides\MobileNet_Gleason_weights.h5"
    model = load_keras_model(model_path)
    model_summary = model.summary()
    print(model_summary)
