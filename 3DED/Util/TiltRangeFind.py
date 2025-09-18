# Corrected class definition
from PIL import Image
import numpy as np
from temscript import Microscope
import math


class TiltRangeFinder:
    def __init__(self, microscope, intensity_factor=0.01, fineInc=0.1, start_tilt=20, start_inc=10, tilt_max=85):
        # 构造函数，初始化一些变量和传入的显微镜对象
        self.start_tilt = start_tilt  # 开始倾斜角度
        self.start_inc = start_inc  # 倾斜增量
        self.tilt_max = tilt_max  # 最大倾斜角度
        self.microscope = microscope  # 显微镜对象
        self.intensity_factor = intensity_factor
        self.fineInc = fineInc

    def TiltTo(self, tilt):
        # 设置显微镜的倾斜角度
        arcangle = tilt * math.pi / 180
        self.microscope.set_stage_position(a=arcangle, method='GO', speed=1)

    def ImageProperties(self):
        # 获取显微镜的图像属性，比如图像的尺寸
        # 假设 get_camera_param 函数返回一个带有 'x_size' 和 'y_size' 键的字典

        namelist = self.microscope.get_cameras().keys()
        for name in namelist:
            cameraName = name
        img = self.microscope.acquire(cameraName)[cameraName]
        # 将NumPy数组转换为PIL图像
        pil_image = Image.fromarray(img)
        # 获取图像的原始大小
        self.x_size, self.y_size = pil_image.size

    def SubareaMean(self, xstart, xend, ystart, yend):
        # 获取指定子区域的平均强度
        # 首先获取全图

        # get camera name
        namelist = self.microscope.get_cameras().keys()
        for name in namelist:
            cameraName = name
        img = self.microscope.acquire(cameraName)[cameraName]  # 假设 'acquire' 函数返回一个包含像素强度的 NumPy 数组
        # 然后取出子区域
        pil_image = Image.fromarray(img)
        subarea = pil_image.crop((xstart, ystart, xend, yend))  # 使用 crop 方法获取子区域
        # 将 PIL 图像转换回 NumPy 数组以便计算平均值
        subarea_np = np.array(subarea)
        # 计算并返回子区域的平均强度
        self.center_ref = subarea_np.mean()

    def CallFunction(self, function_name):
        # 根据给定的函数名调用对应的函数
        if function_name == 'ExtremeTilt':
            # 寻找最大倾斜角度
            tilt = self.start_tilt  # 开始的倾斜角度
            while abs(tilt) < self.tilt_max:  # 当当前倾斜角度小于最大倾斜角度时，继续
                self.TiltTo(tilt)  # 设置显微镜的倾斜角度
                self.SubareaMean(0.4 * self.x_size, 0.6 * self.x_size, 0.4 * self.y_size,
                                 0.6 * self.y_size)  # 计算子区域的平均强度
                if self.center_ref <= self.intensity:  # 如果中心参考值小于或等于一定的比例，则退出循环
                    if self.start_inc > 0:
                        inc = self.fineInc
                    else:
                        inc = -1 * self.fineInc
                    tilt = tilt - self.start_inc  # 回退角度
                    while self.center_ref <= self.intensity:
                        tilt += inc
                        self.TiltTo(tilt)  # 设置显微镜的倾斜角度
                        self.SubareaMean(0.4 * self.x_size, 0.6 * self.x_size, 0.4 * self.y_size,
                                         0.6 * self.y_size)  # 计算子区域的平均强度
                        if self.center_ref <= self.intensity:
                            break
                    break

                tilt += self.start_inc  # 否则，增加倾斜角度
            self.ex_tilt = tilt  # 记录极端倾斜角度
        else:
            # 如果函数名未实现，抛出异常
            raise NotImplementedError(f"{function_name} is not implemented.")

    def find_tilt_range(self) -> tuple:
        # 找到最大和最小的倾斜角度
        self.TiltTo(0)  # 将倾斜角度设置为0
        self.ImageProperties()  # 获取图像属性
        self.SubareaMean(0.4 * self.x_size, 0.6 * self.x_size, 0.4 * self.y_size, 0.6 * self.y_size)  # 计算子区域的平均强度
        centerref = self.center_ref  # 记录中心参考值
        self.intensity = self.intensity_factor * centerref
        self.CallFunction('ExtremeTilt')  # 调用极端倾斜函数，寻找最大倾斜角度
        maxtilt = self.ex_tilt  # 记录最大倾斜角度
        self.start_tilt = -1 * self.start_tilt  # 倾斜开始角度取反，为寻找最小倾斜角度做准备
        self.start_inc = -1 * self.start_inc  # 倾斜增量取反，为寻找最小倾斜角度做准备
        self.CallFunction('ExtremeTilt')  # 调用极端倾斜函数，寻找最小倾斜角度
        mintilt = self.ex_tilt  # 记录最小倾斜角度
        return (maxtilt, mintilt, self.start_inc)  # 返回最大和最小的倾斜角度和角速度