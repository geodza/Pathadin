from img_utils import *
from model import *

if __name__ == '__main__':
    # ds = r"C:\Users\User\GoogleDisk\datasets\stroma_glands"
    ds = r"."
    grid_length = 256
    model = unet(f"{ds}/{grid_length}/weigths_new2.h5", input_size=(256, 256, 3))
    model.save(f"{ds}/{grid_length}/weigths_new2_model.h5")
    for img_path, img in flow_ndimgs_from_directory(f"{grid_length}/test/image",False):
        image_name = os.path.basename(img_path)
        img=img_as_float(img)
        img=np.atleast_3d(img)
        img_batch = np.expand_dims(img,axis=0)
        predicted_label_batch = model.predict(img_batch)
        predicted_label = predicted_label_batch[0]
        io.imsave(f"{grid_length}/test/predicted_label/{image_name}.png", predicted_label)
