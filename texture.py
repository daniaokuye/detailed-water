# coding:utf-8

import numpy as np
from Img import cRaster
from noise_rid import noiseRid
import os, pickle


class tex(object):
    def __init__(self, inputfile, ewi, dir):  #
        'inputfile: the input file;ewi:enhanced water index;dir: the direction of filter'
        super(tex, self).__init__()
        # self.IMG = cRaster()
        # self.inputfile = inputfile
        self.ewi = ewi
        self.dir = dir
        # data = inputfile
        data = self.readImg(inputfile)
        self.limit = np.std(data)  # 应该有更好的办法，先用经验值替代，另外数据对此阈值不敏感，因为差异比较大3000
        data = self.smooth(data)
        self.selectedZone(data)

    def readImg(self, data):
        # Numdata = self.IMG.Iread(file)  # return a tuple:im_data,im_geotrans,im_proj
        # self.proj = Numdata[1:]
        # data = Numdata[0]
        # if data.dtype == np.int16:
        #     data = data.astype(np.int32)
        if self.dir == 270:
            data = np.swapaxes(data, 0, 1)
        elif self.dir == 90:
            data = np.swapaxes(data[::-1, :], 0, 1)
        elif self.dir == 0:
            data = data[:, ::-1]
        else:
            pass
        return data

    def smooth(self, data, fusionCol=2, fusionLine=1):
        '平缓普通区域的差异,fusionCol=2#列上的大小,fusionLine=1#行上的大小'
        # makes the profile more smooth. the method is used for deleting noises of Water index'
        # a kernel is used for the proceed. 'fusionCol' is columns of kernel while 'text' is lines.

        # 这个计算并存储的是把纹理暗区模糊化的数据
        # 'new_data' is used for saving smoothed data
        new_data = data
        line, col = data.shape
        text = 2 * fusionLine + 1  # 上下行数
        for l in range(line):
            for i in range(col):
                # every line will calculate within certain range.
                if (i - fusionCol <= 0) or (i + fusionCol >= (col - 1)):
                    # '处理图像边界范围内数据'
                    continue

                temp = np.mean(data[l][i - fusionCol:i + fusionCol + 1])  # 均值

                # limit调整,只保留差异化大的地方
                if (l - fusionLine < 0):
                    limit_zone = data[0:text, i - fusionCol:i + fusionCol + 1]
                elif (l + fusionLine + 1 > line):
                    limit_zone = data[-text:, i - fusionCol:i + fusionCol + 1]
                else:
                    limit_zone = data[l - fusionLine:l + fusionLine + 1, i - fusionCol:i + fusionCol + 1]
                LMin = np.min(limit_zone)
                LMax = np.max(limit_zone)
                LMean = np.mean(limit_zone)
                # this alpha is very important.here it equals 4.5
                if (LMean - LMin > 4.5 * self.limit):  # which is used to protect the zone not being smoothed
                    Ldiv = 0.1
                else:
                    Ldiv = 1

                if abs(data[l][i] - temp) < (self.limit * Ldiv):
                    new_data[l][i] = temp  # 使用均值替代
                # else:#多此一举
                # new_data[l][i]=data[l][i]

            if l % 500 == 0:
                print(l)
        return new_data

    def selectedZone(self, data):
        '''特点：1.极小值小于0；2.区间是极小值到极大值；3.变化陡峭
        获得斜率为正的区域，并对该区域计算 
        '''
        Noise = noiseRid()
        slop_data = data * 0
        ratioD = self.readImg(self.ewi)  # 读取EWI影像
        h_, w_ = data.shape
        # these three can be output as imagery
        mnf_data = ratioD  # 需要做调整的ewi
        per_data = np.zeros((2, h_, w_))  # 用来存储水体占比
        extract_data = data.astype(np.int) * 0

        line, col = data.shape
        for l in range(line):
            end = 0
            dataL = data[l]
            for i in range(col - 1):
                if i <= end:  # 去掉第一列，没什么用
                    continue
                start = i  # 如果程序能够进入while循环，则，start为
                while True:
                    temp = dataL[i + 1] - dataL[i]  # 梯度temp
                    if (temp <= 0 or i >= col - 2): break
                    i = i + 1
                end = i
                if (start != end):
                    zone = dataL[start:end + 1]  # zone
                    if (zone[0] > 0):  # 满足极小值小于0
                        continue
                    tempZone = np.hstack((zone[0], zone[:-1]))  # 批量做地图运算
                    slop = zone - tempZone  # slop
                    if (np.max(slop) < self.limit):  # 满足变化陡峭的特点
                        continue
                    slop_data[l, start:end + 1] = zone

                    reflect = list(ratioD[l, start:end + 1])
                    # '对符合要求的区域进行“恢复”计算'
                    mnf = Noise.mnf(reflect, list(zone))
                    # 调整值落在【-1,1】之间。
                    adjust = np.where(mnf < -1, -1, mnf)
                    adjust = np.where(mnf > 1, 1, adjust)
                    # 计算百分比
                    percent = Noise.percent(adjust)

                    try:
                        per_data[:, l, start:end + 1] = percent
                        # if (np.sum(percent) > 0.8 and np.max(percent) > 0.5):
                        #     extract_data[l, start:end + 1] = 1
                    except Exception as e:
                        print("ppp:", e)
                    try:
                        mnf_data[l, start:end + 1] = adjust
                    except Exception as e:
                        print("ooo:", e)
                    # print 'ok',start,end

            if l % 500 == 0:
                print(l, 'l')
        # outfile = self.inputfile.split('.')
        # outfile = outfile[0] + '_out.' + outfile[-1]
        # self.out = outfile
        self.outPut(data, per_data, mnf_data)  # extract_data, outfile

    def outPut(self, extract_data, per_data, mnf_data):  # , outfile
        # out = np.concatenate([extract_data[np.newaxis, :], per_data[np.newaxis, :], mnf_data[np.newaxis, :]], axis=0)
        out = np.concatenate([per_data, mnf_data[np.newaxis, :]], axis=0)
        if self.dir == 270:
            out = np.swapaxes(out, 1, 2)
        elif self.dir == 90:
            out = np.swapaxes(out, 1, 2)
            out = out[:, ::-1, :]
        elif self.dir == 0:
            out = out[:, :, ::-1]
        else:
            pass
        self.out = out
        self.outfile = os.path.join(os.getcwd(), str(self.dir) + '_dir.pkl')
        # mnf_data=np.swapaxes(mnf_data,0,1)
        # print 'now',np.min(data)
        # c = [out] + list(self.proj) + [outfile]
        # self.IMG.Iwrite(*c)
        # res = {}
        # res[self.dir] = out
        with open(self.outfile, 'wb') as f:
            pickle.dump(out, f)


class postProcedure(object):
    def __init__(self):
        super(postProcedure, self).__init__()
        # self.IMG = cRaster()
        # self.proj = []

    def finalImage(self, outFile):
        d = np.array(0)
        c = 3
        for file in outFile:
            with open(file, 'rb') as f:
                # print('add 4: ', file)
                # Numdata = self.IMG.Iread(file)  # return a tuple:im_data,im_geotrans,im_proj
                # data = Numdata[0]
                data = pickle.load(f)
                # if len(self.proj) == 0: self.proj = Numdata[1:]
                if d.shape:  # (3, _, _) c==3
                    temp = np.concatenate([d, data])
                    t0 = np.min(temp[[0, c]], axis=0)[np.newaxis, :]
                    t1 = np.max(temp[[1, 1 + c]], axis=0)[np.newaxis, :]
                    t2 = np.mean(temp[[2, 2 + c]], axis=0)[np.newaxis, :]
                    d = np.concatenate([t0, t1, t2])
                else:
                    d = data
                print(d.shape)
            os.remove(file)
        d[1] = np.where(d[1] < 0.1, 1e5, d[1])
        ratio = 1.0 * (d[2] - d[0]) / (d[1] - d[0])
        ratio = np.where(ratio > 1, 1.0, ratio)
        ratio = np.where(ratio < 0, 0.0, ratio)
        res = np.concatenate([ratio[np.newaxis, :], d[2][np.newaxis, :]])
        # outPut = outFile[0] if outFile[0] else self.out
        # outPut = outPut.split('.')
        # outPut = outPut[0] + '_final_.' + outPut[-1]
        # c = [d] + list(self.proj) + [outPut]
        # self.IMG.Iwrite(*c)
        # self.final = outPut
        return res

    # def thres(self, threshold):
    #     Numdata = self.IMG.Iread(self.final)  # return a tuple:im_data,im_geotrans,im_proj
    #     data = Numdata[0]  # the type of data's number is float
    #     data[1, :, :] = data[1, :, :] > threshold
    #     data[0, :, :] *= data[1, :, :]
    #     data = np.min(data, axis=0)
    #
    #     outPut = self.final.split('.')
    #     outPut = outPut[0] + repr(threshold) + '.' + outPut[-1]
    #     c = [data[1:, :, :]] + list(self.proj) + [outPut]
    #     self.IMG.Iwrite(*c)


if __name__ == "__main__":
    inputfile = 'D:/360Downloads/test/beiJ_90_new.tif'  # one result of directional spatial opertor
    ewi = 'D:/360Downloads/test/beiJ_EWI.tif'  # EWI
    texture = tex(inputfile, ewi, 0)
