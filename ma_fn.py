from Img import cRaster
import numpy as np
import cv2
import matplotlib.pyplot as plt

kernel = [3, 5]


class mabaodong(object):
    # return a collection of tuples
    # its neighbour pixels && kernels of distance
    def __init__(self):
        super(mabaodong, self).__init__()

    def cnn(self, img, kernels=kernel):
        # convlution this img with a kernel size
        # img should be and only to be 2 dimensions
        ma = []
        for k in kernels:
            conv_ft, x, y = self.prepare_kernel(k)
            out = list(map(self.prepare_img(img), zip(x, y)))
            out = np.vstack(out)
            # conv_ft = conv_ft[:, np.newaxis, np.newaxis]
            ma.append((out, conv_ft))
        return ma

    def prepare_kernel(self, kernel_size):
        # arrange a list of kernel according to distance of point to center
        if kernel_size == 1:
            return [0]
        center = kernel_size // 2
        x = np.tile(np.arange(kernel_size), (kernel_size, 1)) - center
        y = np.tile(np.arange(kernel_size), (kernel_size, 1)).T - center
        xy = 1 / ((x ** 2 + y ** 2) ** 0.5)
        xy[center, center] = 0
        xy /= np.sum(xy)
        return xy.reshape(-1), x.reshape(-1), y.reshape(-1)

    def prepare_img(self, img):
        # for map; move image
        def adjust_img(x):
            i, j = x
            out = self.move_img(img, i, j)
            return out[np.newaxis]

        return adjust_img

    def move_img(self, input, i, j):  # hor,vertical
        img = input.copy()
        print(':', i, j)
        h, w = img.shape
        if i != 0:
            h = np.zeros(h)
            u = [img, np.tile(h, (abs(i), 1)).T]
            img = np.column_stack(u[::int(np.sign(i + 0.5))])
            if i < 0:
                img = img[:, :i]
            else:
                img = img[:, i:]
        if j != 0:
            w = np.zeros(w)
            u = [img, np.tile(w, (abs(j), 1))]
            img = np.row_stack(u[::int(np.sign(j + 0.5))])
            if j < 0:
                img = img[:j, :]
            else:
                img = img[j:, :]
        return img


class ma_Unmixing(object):
    # function about unmixing
    def __init__(self):
        super(ma_Unmixing, self).__init__()

    # obtain location of pure water body & mixed pixels in one image with the help of threshold
    def pure_and_mix(self, img, threshold):
        # threshold to get pure water body
        # then dilation for mixed ones & outer is land endmembers
        # todo:threshold & < should be changed
        pure_water = (img < threshold).astype(np.uint8)
        kernel_ = np.ones((3, 3)).astype(np.uint8)
        out_dilation = cv2.dilate(pure_water, kernel_)  # the outline for mixed body
        mixed = out_dilation - pure_water
        # land=0,mixed=1,pure water=2
        return mixed + pure_water * 2

    # check those pixels that cannot be satisfied by size of kernel
    def check_case(self, ends, idx_origin):
        # 3*3 5*5 nearest to deteminate end members
        img, _ = ends
        img = img[:, idx_origin[0], idx_origin[1]]  # only return a flatten array for every dims=3
        # deter = img.reshape(-1)
        # idx_origin = np.where(deter == 1)
        miniest_idx_origin = np.min(img, axis=0)
        # those mixed pixels where they can not find land (land==0)
        idx = np.where(miniest_idx_origin != 0)
        y = [x[idx[0]] for x in idx_origin]
        return y


def obtain_data(filename):
    a = cRaster()
    b = a.Iread(filename)
    img = b[0]
    img = img.astype(np.float32)

    def save_data(data, filepath):
        c = [data] + list(b[1:]) + [filepath]
        a.Iwrite(*c)

    return img, save_data


def detemine_size_of_neighbour(img, threshold=0):
    unmixing = ma_Unmixing()
    mbd = mabaodong()
    img_endmembers = unmixing.pure_and_mix(img, threshold)  # land=0,mixed=1,pure water=2
    out = np.zeros(img_endmembers.shape).astype(np.uint8)
    idx_origin = np.where(img_endmembers == 1)
    # determination_endmembers
    for ends in mbd.cnn(img_endmembers):
        idx = unmixing.check_case(ends, idx_origin)
        # 1 can be done by 5*5,otherwise neighbour( which equals to 2)
        out[idx[0], idx[1]] += 1
    # out2 = np.zeros(img_endmembers.shape).astype(np.uint8)
    # out2[idx_origin[0], idx_origin[1]] = 1
    # 0: nothing; 1: 3*3; 3: neighbour; 2: 5*5
    return out + (img_endmembers == 1)


# give linear unmixing results by given size of neighbour
def get_ratio(LAU, kernels=kernel):
    Rft = [x[y // 2] for x, y in zip(LAU, kernels)]  # a mixed pixel
    Rou = [[np.max(x, axis=0), np.min(x, axis=0)] for x in LAU]  # pure land & pure water
    ratio_l = []
    for Rou_i, Rft_i in zip(Rou, Rft):
        land, water = Rou_i
        tmp = (land - Rft_i) / (land - water + 1e-15)
        div = np.where((land - water) == 0)
        tmp[div[0], div[1]] = 0
        ratio_l.append(tmp)
        # ratio_w = 1 - ratio_l
    return ratio_l


def average_neighour(img):
    # average of neighboring pixels
    mbd = mabaodong()
    LAU = mbd.cnn(img)
    LAU = [np.dot(np.transpose(x, (1, 2, 0)), y) for x, y in LAU]
    L = [mbd.cnn(x, [y]) for x, y in zip(LAU, kernel)]
    L = [x[0][0] for x in L]
    return L


# all process of mabaodong
def Local_adaptive_unmixing(img, threshold):
    # 1. return neighbour's pixels & kernel
    L = average_neighour(img)
    # 2. out determine the end members
    # indicator: 1,2,3 behalf the way they find end members respectively
    # for every location
    out = detemine_size_of_neighbour(img, threshold)
    # 3. the results of unmixing
    ratio = get_ratio(L)
    # 4. select suitable unmixing results one by one pixel
    ratio.append(ratio[0])
    res = np.zeros(img.shape)
    for key in [1, 2, 3]:
        res += ((out == key) * ratio[key - 1])
    return res


# all process of commom approach
def Linear_unmixing(img, threshold):
    mbd = mabaodong()
    sz_kernel = [3]
    LU = [mbd.cnn(img, sz_kernel)[0][0]]
    out = detemine_size_of_neighbour(img, threshold)
    # 3. the results of unmixing
    ratio = get_ratio(LU, sz_kernel)[0]
    res = ((out > 0) * ratio)
    return ratio# res


def main_mabaod(filename):
    MOD09A1_threshold = [308, -0.8, -0.3]
    img, sv = obtain_data(filename)
    # img = np.where(img < 0, 0, img)
    ma_LAU = Local_adaptive_unmixing(-img, MOD09A1_threshold[1])
    commom_LU = Linear_unmixing(-img, MOD09A1_threshold[1])
    sv(ma_LAU, filename[:-4] + 'ma_LAU.tif')
    # sv(commom_LU, filename[:-4] + 'cm_LU.tif')
    # sv(commom_LU,filename[:-4] + 'cm_LU.tif')


if __name__ == "__main__":
    filename = 'D:/modisNew/test/ndwi_final__2.tif'
    # filename = "D:/modisNew/test/a11.sur_refl_b02.tif"
    filename = "D:/modisNew/DW_magnitude/process/MA1_2015_209.sur_refl_b02_ndwi.tif"
    main_mabaod(filename)
    print('ok')
