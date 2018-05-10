from ma_fn import obtain_data
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import numpy as np


def train_wb(X, Y):
    # X = X.reshape(-1, 1)
    wb = np.polyfit(X, Y, 1)
    a = np.linspace(np.min(X), np.max(X))  # 横坐标的取值范围
    b = a * wb[0] + wb[1]
    return a, b, wb


def get_data(gt_, origin_, adjacent_, Is_diff=0):
    gt, sv = obtain_data(gt_)
    origin, _ = obtain_data(origin_)
    adjacent, _ = obtain_data(adjacent_)
    if Is_diff:
        origin -= gt
        adjacent -= gt
    x = origin[np.where(origin != 0)]
    y = adjacent[np.where(adjacent != 0)]

    # definitions for the axes
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left + width + 0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]
    # start with a rectangular Figure
    plt.figure(1, figsize=(8, 8))

    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)

    nullfmt = NullFormatter()
    # no labels
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)
    # now determine nice limits by hand:
    binwidth = 0.02
    bins = np.arange(np.min(x), np.max(x) + binwidth, binwidth)
    axHistx.hist(x, bins=bins)
    axHisty.hist(y, bins=bins, orientation='horizontal')

    axHistx.set_xlim(axScatter.get_xlim())
    axHisty.set_ylim(axScatter.get_ylim())

    # the scatter plot:
    axScatter.scatter(x, y, marker='x')
    axScatter.set_xlim((np.min(x), np.max(x)))
    axScatter.set_ylim((np.min(y), np.max(y)))

    a, b, wb = train_wb(x, y)
    axScatter.plot(a, b, 'r')
    axScatter.set_xlabel('ground truth minus origin image')
    axScatter.set_ylabel('ground truth minus removed adjacent effect image')
    axHistx.set_title('difference maps', fontsize=14)
    axScatter.text(-0.8, 0.9, r'y={:.3f}x+{:.4f}'.format(wb[0], wb[1]))
    plt.show()


def draw_regress(file):
    gt_ = file + 'groundTruth.tif'
    origin_ = file + 'MA1_2015_209.sur_refl_b02_ndwicm_LU_EdgeLine.tif'
    adjacent_ = file + 'noAdjacentcm_LU_EdgeLine.tif'
    # get_data(gt_, origin_, adjacent_)
    get_data(gt_, origin_, adjacent_, 1)


def draw_hist(file):
    pr = file + 'different_proposed.tif'
    lu = file + 'different_LU.tif'
    pr, _ = obtain_data(pr)
    lu, _ = obtain_data(lu)
    pr = pr[np.where(pr != 0)]
    lu = lu[np.where(lu != 0)]
    fig, (ax0, ax1) = plt.subplots(nrows=2)
    ax0.hist(pr, 40)
    ax0.set_title('Difference between proposed method and ground truth')
    ax1.hist(lu, 40)
    ax1.set_title('Difference between LAU method and ground truth')
    fig.subplots_adjust(hspace=0.4)
    plt.show()


file = 'D:/modisNew/DW_magnitude/process/'

# draw_regress(file)
draw_hist(file)
# print('o')
