# encoding:utf-8

from Img import cRaster
import numpy as np
from params import alpha

if __name__ == "__main__":
    texture = 'F:\\Landsat\\tai_hu\\direction\\L13_0_new.tif'
    ewi = 'F:\\Landsat\\tai_hu\\direction\\EWI.tif'
    outfile = 'F:\\Landsat\\tai_hu\\direction\\L13___MNF.tif'

    IMG = cRaster()
    Numdata = IMG.Iread(texture)
    ratioData = IMG.Iread(ewi)
    data = Numdata[0]  #
    ratioD = ratioData[0]
    print(data.dtype, '\n', data.shape)
    l, c = data.shape
    print(l, 'col=', c)

# ratioA=[[-4946,-4071,-3460,871,4779,6459],
#        [-4723,-1400,5269],
#        [-4407,-2756,316,696,3365,4060],
#        [-15489,-5557,1340,5044,14682]]
# 
# reflectA=[[-0.49,-0.4,-0.24,-0.18,-0.35,-0.46],
#           [-0.56,-0.45,-0.50],
#           [-0.52,-0.53,-0.54,-0.54,-0.55,-0.51],
#           [-0.25,0.03,0.03,0.03,-0.07]]
'''
for line in range(len(ratioA)):
    reflect=reflectA[line]
    ratio=ratioA[line]
    newR=[reflect[0]]
    right=reflect[-1]
    j=1;
    while(right==0):
        j=j+1
        right=reflect[-j]
    amin=min(reflect[0],reflect[-1])    
    index=reflect.index(amin )
    print amin,index
    for i in range(len(ratio)):
        if i==index:
            continue
        a=abs(1.0*ratio[index]/ratio[i])
        newR.append((reflect[index]-a*reflect[i])/(1-a))
    print reflect,"\n",newR
 '''


#   
# for line in range(l):
#     for i in range(c-1):
#         reflect=data[l]
#         ratio=ratioD[line]

# 计算用纹理增强EWI或其他水体指数的边缘方法。
class noiseRid(object):
    def __init__(self):
        super(noiseRid, self).__init__()

    def mnf(self, reflect, ratio):
        newR = [0]
        amax = max(reflect)
        aI = reflect.index(amax)
        test, s1, s2 = 0, 0, 0
        if (aI != 0):
            s1 = max(reflect[0:aI])
            test += 1
        if (aI != len(reflect) - 1):
            s2 = max(reflect[aI + 1:])
            test += 1

        # AI和bI分别代表区间内数值最大的前两个。
        # 两次经过if，说明最值不在边缘处,但不能说明他俩ai、bi是紧挨着的
        if (test == 2):
            # print "0.0.0:",s1,s2,'ai:',aI
            # 选择边缘非水体。
            bI = reflect.index(max(s1, s2))
            if bI == aI:
                try:
                    bI = reflect.index(max(s1, s2), 0, aI)
                except Exception as x:
                    bI = reflect.index(max(s1, s2), aI + 1)
                    # print amax,reflect[bI],'bi:',bI
            if (aI < bI):  # 因为他俩ai、bi可能不是紧挨着的
                a = aI  # 设定以大为准,头二不在一起的原则
                b = aI + 1
            else:
                a = aI - 1
                b = aI

            # 纹理上的差值，看做是灰度造成的比值？？？？、
            aRatio = ratio[a] - ratio[0]
            bRatio = max(ratio) - ratio[b]  # b可能是最后一个，所以这个数为0概率大
            for i in range(a + 1):
                if i == 0:
                    continue
                slope = alpha * (ratio[i] - ratio[i - 1]) / aRatio
                net = slope * (reflect[i] - reflect[i - 1])
                newR.append(net)
            for i in range(len(reflect) - b - 1):
                index = i + b
                if (bRatio == 0):
                    print("bRatio==0")
                    print(reflect, ratio)
                    print(s1, s2, 'ai:', aI, bI)
                    print(len(reflect), b)
                slope = -1.0 * (ratio[index] - ratio[index + 1]) / bRatio
                net = slope * (reflect[index] - reflect[index + 1])
                newR.append(net)
            # print "\nnewR:",newR
            sumA = 0
            for i in range(a + 1):
                sumA += newR[i]
                newR[i] = sumA
            sumA = 0
            for i in range(len(reflect) - b - 1):
                index = len(reflect) - 2 - i
                sumA += newR[index]
                newR[index] = sumA
            # print "nowR:",newR

            newR.append(0)
            # add = map(lambda a, b: a + b, zip(newR, reflect))
            add = [a + b for a, b in zip(newR, reflect)]
            return np.array(add)  # 符合条件的将以新值返回
        else:
            return np.array(reflect)  # 不符合条件的原值返回

    # 计算水体所占比例。
    # 具体是假设可以直接获取locate非水体样本
    # 水体的样本是计算增强了的与pure water和locate非水体混合比例。
    # 是增强了的。
    # 然后上面的比例*（locate非水体和本水体混合比例）
    def percent1(self, adjust, reflect):
        print('a', adjust.shape, len(reflect))
        # 2018/3/1
        Is_same = sum([x != y for x, y in zip(adjust, reflect)])
        # if((adjust != reflect).any()):
        if (Is_same):
            print("no Equal")
            adjust = list(adjust)  # 先转成列表，reflect本身是列表
            noWater = min(adjust)  # 非水体
            Water = max(adjust)  # 水体
            adWater = reflect[adjust.index(Water)]  # 调整后的水体
            pureWater = 0.0  # 假设纯水的EWI为大于0 的一个数值。
            print('key num:', adWater, noWater, Water)
            if (adWater < pureWater):
                totalRatio = 1 - 1.0 * (adWater - noWater) / (pureWater - noWater)
            else:
                totalRatio = 1.0
            # 原始的EWI值中最值作为纯净像元的情况下的百分比
            reflect = np.array(reflect)
            ratioW = 1 - 1.0 * (reflect - noWater) / (Water - noWater)
            # 最终的百分比，是结合了总体水的形式
            percent = totalRatio * ratioW
            print('b', percent.shape)
            return percent
        else:
            return adjust * 0

    def percent(self, adjust):
        noWater = np.min(adjust)  # 非水体
        Water = 0.1 if np.max(adjust) < 0 else np.max(adjust)  # np.max(adjust)#水体
        # if Water < -0.2: Water=-0.2
        # ratio = 1.0 * (adjust - noWater) / (Water - noWater + 1e-15)
        # ratio = np.where(ratio > 1, 1.0, ratio)
        # ratio = np.where(ratio < 0, 0.0, ratio)
        w = adjust.shape[0]
        local = np.zeros((2, w))
        local[0] = noWater
        local[1] = Water
        return local

        # 探测定位相邻区域有无毗连区,并作出调整

    ##ATTENTION!!!
    # 暂时没发现邻域有什么作用，在考虑多角度 的时候倒是可以考虑邻域；
    # 对于增强来说，邻域作用不明！！！
    # 现在放弃这段代码，2016-8-19 11:08:58
    #############################
    def detect(self, l, start, end, data):
        line, col = data.shape
        [[Lstart, Lend], [Rstart, Rend]] = [[0, -1], [0, -1]]
        # 获取有效的区间
        if l - 1 > 0:
            Lstart, Lend = self.zone(l - 1, start, end, data)
        if l + 1 < col - 1:
            Rstart, Rend = self.zone(l + 1, start, end, data)
        if (Lend > 0):
            Lend = self.twoThird(Lstart, Lend, start, end)
        if (Rend > 0):
            Rend = self.twoThird(Rstart, Rend, start, end)
        # 或可以在这儿调用mnf函数,只先更改梯度比例
        neighbor = [[Lstart, Lend], [Rstart, Rend]]
        return neighbor

    def twoThird(self, s, e, start, end):
        # 验证区间相交度
        locA = s if s >= start else start
        locB = e if e <= end else end
        if (1.0 * (locB - locA) / (end - start) < 2.0 / 3 or 1.0 * (locB - locA) / (e - s) < 2.0 / 3):
            e = -1
        return e

    def zone(self, l, start, end, data):
        line, col = data.shape
        # 满足不为0，且不变号
        if (data[l, start:end + 1] != 0).any():
            zone_0 = np.where(data[l, start:end + 1] != 0)[0][0]
            loc = zone_0
            while (data[l, zone_0] - data[l, zone_0 + 1] < 0):  # 因为是开头，所以它不会是col-1
                if (zone_0 != 0):
                    zone_0 -= 1
                else:
                    zone_0 -= 1  # 因为每一次都会多减一，图像边缘也保持惯例，最小到-1
                    break
            zone_1 = loc
            while (data[l, zone_1 + 1] - data[l, zone_1] > 0):  # 这儿是位置刚好的
                if (zone_1 < col - 2):  # 这儿加以限定，最大到col-2
                    zone_1 += 1
                else:
                    zone_1 += 1  # 此时的zone是多加了一的，取切片的时候留意。
                    break
            return [zone_0 + 1, zone_1]  # 做切片的时候，后面要加1
        else:
            return [0, 0]
