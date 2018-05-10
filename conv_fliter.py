from ma_fn import obtain_data
# from scipy.ndimage import filters
from scipy import ndimage
import numpy as np
import matplotlib.pyplot as plt
from texture import tex, postProcedure




def direction_filter(filepath):
    img, sv = obtain_data(filepath)
    img_0 = ndimage.prewitt(img, 1)
    img_180 = ndimage.prewitt(-img, 1)
    img_90 = ndimage.prewitt(img, 0)
    img_270 = ndimage.prewitt(-img, 0)
    return sv, img, img_0, img_90, img_180, img_270


def show_dir_filter():
    fz = 'D:/modisNew/detailedW/MoWI.tif'
    _, _, img_0, img_90, img_180, img_270 = direction_filter(fz)
    fg = plt.figure()
    ax1 = fg.add_subplot(221)
    ax1.imshow(img_0)
    ax1.set_title('img 0')
    ax2 = fg.add_subplot(222)
    ax2.imshow(img_90)
    ax2.set_title('img 90')
    ax3 = fg.add_subplot(223)
    ax3.imshow(img_180)
    ax3.set_title('img 180')
    ax4 = fg.add_subplot(224)
    ax4.imshow(img_270)
    ax4.set_title('img 270')
    plt.show()


def main_function(inputfile):
    filepath = inputfile.split('.tif')
    dataFiles = direction_filter(inputfile)
    sv, ewi, *dataFile = dataFiles
    directions = [0, 90, 180, 270]
    out = []
    for dir, file in zip(directions, dataFile):
        print(dir, ' is now direction')
        texture = tex(file, ewi, dir)
        sv(texture.out, filepath[0] + '_' + str(dir) + '_.tif')
        out.append(texture.outfile)
        # timeBar(4 - len(dataFile))
    # file = list(set(out))[0]
    pP = postProcedure()
    res = pP.finalImage(out)
    sv(res, filepath[0] + '_final__.tif')


if __name__ == "__main__":
    # show_dir_filter()
    ewi = 'D:/modisNew/detailedW/MoWI.tif'
    ewi = 'D:/modisNew/test/ndwi.tif'
    main_function(ewi)
    print('o')
