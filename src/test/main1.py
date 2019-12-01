from operator import itemgetter

from PIL import Image, ImageStat

img_path = r'C:\Users\User\GoogleDisk\Pictures\Mountains\1.jpg'

if __name__ == '__main__':
    im = Image.open(img_path)
    # im.show()
    imgq = im.quantize(10)
    im2=imgq.convert("RGB")
    # im2.show()
    # imgq.show()
    # colors = imgq.getcolors(256 * 256 * 256)
    # sorted_colors = sorted(colors, key=itemgetter(0), reverse=True)
    # top_colors = sorted_colors[:5]
    # print(top_colors)
    print(im2.getcolors())
    print(ImageStat.Stat(im2).count)
