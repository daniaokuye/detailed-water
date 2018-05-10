# coding:utf-8
import gdal


# from PIL import ImageFilter,Image
# import numpy as np

class cRaster(object):
    def __init__(self):
        super(cRaster, self).__init__()

    def __del__(self):
        pass

    def Iread(self, filename):
        'open a image by the filename'
        dataset = gdal.Open(filename)  # open imagery

        im_width = dataset.RasterXSize  # column of image
        im_height = dataset.RasterYSize  # row of image
        self.im_bands = dataset.RasterCount  # num of bands

        im_geotrans = dataset.GetGeoTransform()
        im_proj = dataset.GetProjection()  # info of project
        im_data = dataset.ReadAsArray(0, 0, im_width, im_height)
        del dataset

        return im_data, im_geotrans, im_proj
        #
        # ["WGS 84 / UTM zone 50N",GEOGCS["WGS 84"
        # ,DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,
        # AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],
        # PRIMEM["Greenwich",0],UNIT["degree",
        # (409294.88697, 27.37648, 0.0, 4423871.08338, 0.0, -27.37648)

    def Iwrite(self, *var):
        'wirte data to image file'
        ImData, ImGeoTrans, ImProj, filename = var
        print('saving the image by the procedure:', __name__, filename)
        if 'int8' in ImData.dtype.name:
            datatype = gdal.GDT_Byte
        elif 'int16' in ImData.dtype.name:
            datatype = gdal.GDT_Int16
        else:
            datatype = gdal.GDT_Float32

        if len(ImData.shape) == 3:
            ImBands, ImHeight, ImWidth = ImData.shape
        else:
            ImBands, (ImHeight, ImWidth) = 1, ImData.shape

        # create a new file
        driver = gdal.GetDriverByName("GTiff")
        dataset = driver.Create(filename, ImWidth, ImHeight, ImBands, datatype)
        dataset.SetGeoTransform(ImGeoTrans)  # head information
        dataset.SetProjection(ImProj)  # project
        if ImBands == 1:
            dataset.GetRasterBand(1).WriteArray(ImData)  # data
        else:
            for i in range(ImBands):
                dataset.GetRasterBand(i + 1).WriteArray(ImData[i])
        del dataset


if __name__ == "__main__":
    filename = "D:/modisNew/modis/EWI121.tif"
    savefile = "D:/modisNew/proposedMethod/d000.tif"
    # a=cRaster()
    # b=a.Iread(filename)
    # img=b[0]

    # img=img.astype(np.float32)
    # print type(img),img.dtype
    # img = Image.fromarray(img,mode='F')
    # #img=Image.open("D:/modisNew/modis/EWI121.tif",'tiff')
    # im1 = img.filter(ImageFilter.Kernel((3,3),[-1.0, 0.0, 1.0]*3))
    # im1 = np.array(im1)
    # c=[im1]+list(b[1:])+[savefile]
    # a.Iwrite(*c)
