import datetime
import json
import math
import os
import shutil
import time
import tkinter.messagebox
from threading import Thread
from time import sleep
import numpy as np
import psutil
import scipy.signal as sig
from PIL import Image
from temscript import NullMicroscope
from temscript import Microscope
import matplotlib.pyplot as plt
from multiprocessing import Process

TEM = NullMicroscope()

# TEM = null_microscope.NullMicroscope()

# 全局变量声明
global cameraname, exposuretime, binning, degreespeed, stepangle, rotationspeed, startangle, endangle
global filesavepath, freetime, anglerange, num, drift_step, drift_num, drift_exposuretime, drift_binning, drift_image_save, beamstop, is_save


# TODO定义全局变量
def read_input_value(filename, key):
    with open(filename, 'r') as file:
        data = json.load(file)
        return data[key]
    return None


codepath = os.getcwd()
inputfile = codepath + '/params.json'
cameraname = read_input_value(str(inputfile), 'cameraname')
# print(cameraname)
exposuretime = float(read_input_value(str(inputfile), 'Exposure_Time'))
binning = int(read_input_value(str(inputfile), 'binning'))
degreespeed = float(read_input_value(str(inputfile), 'Degree_Speed'))  # degreespeed range from 0.03 to 0.6 degrees/s
stepangle = exposuretime * degreespeed
rotationspeed = degreespeed / 29.332
startangle = int(read_input_value(str(inputfile), 'Start_Angle'))
endangle = int(read_input_value(str(inputfile), 'End_Angle'))
filesavepath = read_input_value(str(inputfile), 'filesavepath')
freetime = float(read_input_value(str(inputfile), 'Free_Time'))
anglerange = abs(startangle - endangle)
stepangle = degreespeed * exposuretime
num = int(anglerange / stepangle)
drift_step = float(read_input_value(str(inputfile), 'drift_step'))
print("drift_step", drift_step)
drift_num = int(anglerange / drift_step)
drift_exposuretime = float(read_input_value(str(inputfile), 'drift_exposuretime'))
drift_binning = int(read_input_value(str(inputfile), 'drift_binning'))
drift_image_save = int(read_input_value(str(inputfile), 'drift_image_save'))

beamstop = read_input_value(str(inputfile), 'beamstop')
is_save = read_input_value(str(inputfile), 'is_save')
# print(cameraname)
print(exposuretime)
# print(binning)
print(degreespeed)
print("cred", startangle)
print(endangle)
if startangle > endangle:
    drift_step = - drift_step
    stepangle = -stepangle
elif startangle < endangle:
    stepangle = stepangle
    drift_step = drift_step


def update_input():
    global cameraname, exposuretime, binning, degreespeed, stepangle, rotationspeed, startangle, endangle
    global filesavepath, freetime, anglerange, num, drift_step, drift_num, drift_exposuretime, drift_binning, drift_image_save, beamstop, is_save

    codepath = os.getcwd()
    inputfile = codepath + '/params.json'
    cameraname = read_input_value(str(inputfile), 'cameraname')
    # print(cameraname)
    exposuretime = float(read_input_value(str(inputfile), 'Exposure_Time'))
    binning = int(read_input_value(str(inputfile), 'binning'))
    degreespeed = float(
        read_input_value(str(inputfile), 'Degree_Speed'))  # degreespeed range from 0.03 to 0.6 degrees/s
    stepangle = exposuretime * degreespeed
    rotationspeed = degreespeed / 29.332
    startangle = int(read_input_value(str(inputfile), 'Start_Angle'))
    endangle = int(read_input_value(str(inputfile), 'End_Angle'))
    filesavepath = read_input_value(str(inputfile), 'filesavepath')
    freetime = float(read_input_value(str(inputfile), 'Free_Time'))
    anglerange = abs(startangle - endangle)
    stepangle = degreespeed * exposuretime
    print("degreespeed", degreespeed)
    print("stepangle", stepangle)
    num = int(anglerange / stepangle)
    drift_step = float(read_input_value(str(inputfile), 'drift_step'))
    drift_num = int(anglerange / drift_step)
    drift_exposuretime = float(read_input_value(str(inputfile), 'drift_exposuretime'))
    drift_binning = int(read_input_value(str(inputfile), 'drift_binning'))
    drift_image_save = int(read_input_value(str(inputfile), 'drift_image_save'))
    beamstop = read_input_value(str(inputfile), 'beamstop')
    is_save = read_input_value(str(inputfile), 'is_save')
    # print(cameraname)
    # print(exposuretime)
    print("binning", binning)
    # print(degreespeed)
    # print(startangle)
    # print(endangle)
    if startangle > endangle:
        drift_step = - drift_step
        stepangle = -stepangle
    elif startangle < endangle:
        stepangle = stepangle
        drift_step = drift_step


class initwork:
    def __init__(self):
        self.filesavepath = filesavepath

    def setup_workingpath(self):
        now = datetime.datetime.now()
        foldertime = now.strftime("%Y%m%d-%H%M%S")
        ###Setup time-dependent path in the working path###
        self.workingpath = self.filesavepath + '\\' + str(foldertime)
        # print(self.workingpath)
        os.mkdir(self.workingpath)
        # self.redpath = filesavepath
        # self.credpath = filesavepath
        # self.driftpath = filesavepath
        workingpath = self.workingpath
        return workingpath

    def setup_redpath(self, workingpath):
        self.redpath = str(workingpath) + '\\red'
        os.mkdir(self.redpath)
        redpath = self.redpath
        return redpath

    def setup_credpath(self, workingpath):
        self.credpath = workingpath + '\\cred'
        os.mkdir(self.credpath)
        credpath = self.credpath
        return credpath

    def setup_driftpath(self, workingpath):
        self.driftpath = str(workingpath) + '\\drift'
        os.mkdir(self.driftpath)
        driftpath = self.driftpath
        return driftpath

    def setup_scredpath(self, workingpath):
        self.scredpath = workingpath + '\\scred'
        os.mkdir(self.scredpath)
        scredpath = self.scredpath
        return scredpath

    def setup_edpath(self, workingpath):
        self.edpath = workingpath + '\\EDpatterns'
        os.mkdir(self.edpath)
        edpath = self.edpath
        return edpath


class messagebox:
    def before_drift_correction(self):
        top = tkinter.Tk()
        top.withdraw()
        top.update()
        r = tkinter.messagebox.askyesno(title='Warning！',
                                        message='The automatic drift measurement will be executed.' + '\n' +
                                                'Please make sure: ' + '\n' +
                                                '1) the TEM is under IMAGE mode;' + '\n' +
                                                '2) the sample is in the screen center at the start angle.' + '\n' +
                                                '3) the optical condition is suitable!' + '\n' +
                                                'YES to continue!',
                                        icon=tkinter.messagebox.WARNING)
        if r == False:
            exit()
        else:
            mode = TEM.get_projection_mode()
            if mode == 'DIFFRACTION':
                TEM.set_projection_mode('IMAGING')
                top = tkinter.Tk()
                top.withdraw()
                top.update()
                r = tkinter.messagebox.askyesno(title='Warning！',
                                                message='The TEM is not in IMAGE mode！！！' + '\n' +
                                                        'Please adjust the TEM to suitable optical conditions.' + '\n' +
                                                        'If you want to stop this run, click NO!')
                if r == False:
                    exit()

    def before_ed_acquire(self):
        top = tkinter.Tk()
        top.withdraw()
        top.update()
        r = tkinter.messagebox.askyesno(title='Warning！',
                                        message='The automatic 3DED measurement will be executed.' + '\n' +
                                                'Please make sure: ' + '\n' +
                                                '1) the TEM is under DIFFRACTION mode;' + '\n' +
                                                '2) the diffraction intensity has been checked!')
        if r == False:
            exit()
        else:
            mode = TEM.get_projection_mode()
            if mode == 'IMAGING':
                # TEM.set_projection_mode('DIFFRACTION')
                top = tkinter.Tk()
                top.withdraw()
                top.update()
                r = tkinter.messagebox.askyesno(title='Warning！',
                                                message='The TEM is not in DIFFRACTION mode！！！.' + '\n' +
                                                        'Please adjust the TEM to suitable optical conditions.' + '\n' +
                                                        'If you want to stop this run, click NO!')
                if r == False:
                    exit()

    def before_offline_correction(self):
        top = tkinter.Tk()
        top.withdraw()
        top.update()
        r = tkinter.messagebox.askyesno(title='Warning！',
                                        message='The offline corrected 3DED measurement will be executed.' + '\n' +
                                                "Please make sure that the 'drift_value.txt' file is in the "
                                                'root of the file saving path.')
        if r == False:
            exit()


class drift_measure:
    def __init__(self):
        self.cameraname = str(cameraname)
        self.exposuretime = exposuretime
        self.binning = drift_binning
        self.rotationspeed = rotationspeed
        self.startangle = startangle
        self.drift_exposuretime = drift_exposuretime
        self.drift_num = drift_num
        self.drift_step = drift_step
        self.drift_image_save = drift_image_save

    def plot_drift_value(self):
        with open(filesavepath+"/"+'drift_value.txt', 'r') as file:
            data = file.readlines()
        angle = []
        xshift = []
        yshift = []
        for line in data:
            values = line.strip().split(' ')
            print(values)
            angle.append(float(values[1]))
            xshift.append(float(values[3]))
            yshift.append(float(values[4]))
        print(angle)
        plt.figure()
        plt.plot(angle, xshift, label='x_shift')
        plt.plot(angle, yshift, label='y_shift')
        plt.xlabel('Tilt angle (degrees)')
        plt.ylabel('Drift value (nm)')
        plt.legend()
        while True:
            plt.draw()
            plt.pause(0.1)

    def get_image_xyshift(self, image1, image2):
        # 对输入的图像进行均值归一化处理
        image1 = image1 - np.mean(image1)
        image2 = image2 - np.mean(image2)
        # 利用快速傅里叶变换（FFT）计算图像的自相关和互相关，得到相关性矩阵
        fftself = sig.fftconvolve(image1, image1[::-1, ::-1], mode='same')
        fftcomp = sig.fftconvolve(image1, image2[::-1, ::-1], mode='same')
        # 找到相关性矩阵中具有最大值的位置，即相关性的峰值位置
        selfcenter = np.unravel_index(np.argmax(fftself), fftself.shape)
        # print(selfcenter[0])
        compcenter = np.unravel_index(np.argmax(fftcomp), fftcomp.shape)
        # print(compcenter[0])
        # 获取显微镜相机的像素尺寸
        pixel_size = 1
        # 读取配置文件 configuration.json
        cfgpath = codepath + '/configuration.json'
        with open(cfgpath, "r") as f:
            data = json.load(f)
        pixel_data = json.loads(json.dumps(data["pixel_data"]))
        # print(pixel_data)
        for item in pixel_data:
            # 四舍五入到整数比较，如果一样则赋值退出循环
            # print(round(TEM.get_indicated_magnification(), 0))
            # print(round(item["magnification"], 0))
            if round(item["magnification"], 0) == round(TEM.get_indicated_magnification(), 0):
                # print(round(item["magnification"], 0))
                pixel_size = item["pixel_size(nm)"] * self.binning
                # print(self.binning)
                # print(pixel_size)
                break
        # print(pixel_size)
        # 计算图像在 x 和 y 方向上的偏移量，乘以像素尺寸
        xsh = (compcenter[0] - selfcenter[0]) * pixel_size
        # print(xsh)
        ysh = (-(compcenter[1] - selfcenter[1])) * pixel_size
        # 根据偏移量计算出 u 和 v 的值。这些值代表了图像在水平和垂直方向上的偏移量
        # TODO 获取 image_shift 的系数应该要根据具体场景调试得到
        # u = 0.8904 * xsh + 0.4636 * ysh
        # v = 0.4636 * xsh - 0.8904 * ysh
        return (xsh, ysh)

    def xy_shift(self):
        log = open("exp_log", "a+")
        print('Drift Measurement start......', file=log, flush=True)
        goalangle = self.startangle
        arcgoalangle = goalangle * math.pi / 180
        TEM.set_stage_position(a=arcgoalangle, method='GO')
        init_param = TEM.get_camera_param(self.cameraname)
        param = dict(init_param)
        param["image_size"] = "FULL"
        param["exposure(s)"] = self.drift_exposuretime
        param["binning"] = self.binning
        TEM.set_camera_param(self.cameraname, param)
        acq = TEM.acquire(self.cameraname)
        img = Image.fromarray(acq[self.cameraname]).convert('I;16')
        print("drift_image_save ", drift_image_save)
        if drift_image_save == 1:
            imgfilename = '00001.tif'
            img.save(imgfilename)
            print('Image 00001.tif has been saved', file=log, flush=True)
        else:
            print('One image has been acquired, but not been saved! ', file=log, flush=True)
        # refimgfilename = imgfilename
        refimg = np.array(acq[self.cameraname])
        # refimg = Image.open(refimgfilename)
        # refimg = np.array(refimg)
        # print(refimg)
        # xyshift_array = ['xshift(nm)', 'yshift(nm)']
        # zshift_array = ['zshift(nm)']
        currentstagepos = TEM.get_stage_position()
        initialx = currentstagepos['x'] * 1e9
        # initialx = format(currentx, '.2f')
        initialy = currentstagepos['y'] * 1e9
        # initialy = format(currenty, '.2f')
        arccurrenta = currentstagepos['a']
        arccurrentb = currentstagepos['b']
        currenta = arccurrenta * 180 / math.pi
        currenta = format(currenta, '.2f')
        currentb = arccurrentb * 180 / math.pi
        currentb = format(currentb, '.2f')
        xshift = 0
        yshift = 0
        # totalshiftx = 0
        # totalshifty = 0
        writelog = "1" + ' ' + str(currenta) + ' ' + str(currentb) + ' ' + str(xshift) + " " + str(yshift) + " 0 0"
        with open(filesavepath+"/"+'drift_value.txt', 'a+') as f:
            f.write(str(writelog))
        f.close()
        # p = Process(target=self.plot_drift_value)
        # # thread.daemon = True
        # p.start()
        print("int(self.drift_num + 2)=", int(self.drift_num + 2))
        for i in range(2, int(self.drift_num + 2)):
            goalangle = goalangle + self.drift_step
            print("goalangle", goalangle)
            arcgoalangle = goalangle * math.pi / 180
            print('Stage is moving to ' + str(goalangle) + ' degrees', file=log, flush=True)
            TEM.set_stage_position(a=arcgoalangle, method='GO')
            sleep(1)
            acq = TEM.acquire(self.cameraname)
            img = Image.fromarray(acq[self.cameraname]).convert('I;16')
            if drift_image_save == 1:
                if i < 10:
                    imgfilename = '0000' + str(i) + '.tif'
                    img.save(str(imgfilename))
                elif i >= 10 and i < 100:
                    imgfilename = '000' + str(i) + '.tif'
                    img.save(str(imgfilename))
                elif i >= 100:
                    imgfilename = '00' + str(i) + '.tif'
                    img.save(imgfilename)
                print('Image ' + str(imgfilename) + ' has been saved', file=log, flush=True)
            else:
                print('One image has been acquired, but not been saved! ', file=log, flush=True)
            img0 = np.array(acq[self.cameraname])
            # print(img0)
            currentstage = TEM.get_stage_position()
            currentx = currentstage['x'] * 1e9
            currenty = currentstage['y'] * 1e9
            stageshiftx = currentx - initialx
            stageshifty = currenty - initialy
            initialx = currentx
            initialy = currenty
            stageshiftx = format(stageshiftx, '.2f')
            stageshifty = format(stageshifty, '.2f')
            xyshift = self.get_image_xyshift(refimg, img0)
            print('The measured drift values are: ' + str(xyshift), file=log, flush=True)
            xs = float(xyshift[0])
            ys = float(xyshift[1])
            xs = format(xs, '.2f')
            ys = format(ys, '.2f')
            # totalshiftx = xs + float(totalshiftx)
            # totalshifty = ys + float(totalshifty)
            # xshift = totalshiftx - stageshiftx
            # yshift = totalshifty - stageshifty
            # xshift = format(xshift, '.2f')
            # yshift = format(yshift, '.2f')
            refimg = img0
            arccurrentalpha = currentstage['a']
            arccurrentbeta = currentstage['b']
            currentalpha = arccurrentalpha * 180 / math.pi
            currentalpha = format(currentalpha, '.2f')
            currentbeta = arccurrentbeta * 180 / math.pi
            currentbeta = format(currentbeta, '.2f')
            writelog = str(i) + ' ' + str(currentalpha) + ' ' + str(currentbeta) + ' ' + str(xs) + " " + str(ys) \
                       + " " + str(stageshiftx) + " " + str(stageshifty)

            with open(filesavepath+"/"+'drift_value.txt', 'a+') as f:
                f.write('\n' + str(writelog))
            f.close()
        # self.plot_drift_value()


class synchro_tilt_acquire:
    def __init__(self):
        self.TEM = 'microscope.Microscope()'
        self.cameraname = cameraname
        self.exposuretime = exposuretime
        self.binning = binning
        self.stepangle = stepangle
        self.rotationspeed = rotationspeed
        self.freetime = freetime

    def search_pid(self):
        pidlist = psutil.pids()
        for sub_pid in pidlist:
            process_info = psutil.Process(sub_pid)
            if process_info.name() == 'cmd.exe':
                pid = sub_pid
                return pid

    def backgroundacquire(self):
        with open('backgroundcamera.py', 'w') as f:
            f.write('from temscript import null_microscope')
            f.write('\nfrom temscript import microscope')
            f.write('\nfrom PIL import Image')
            f.write('\nTEM = ' + str(self.TEM))
            f.write("\ncameraname =" + "'" + self.cameraname + "'")
            f.write("\ninit_param = TEM.get_camera_param(cameraname)")
            f.write("\nparam= dict(init_param)")
            f.write("\nparam['image_size'] = 'FULL'")
            f.write("\nparam['exposure(s)'] = " + str(self.exposuretime))
            f.write("\nparam['binning'] = " + str(self.binning))
            f.write("\nTEM.set_camera_param(cameraname, param)")
            f.write('\nacq = TEM.acquire(cameraname)')
            f.write("\nimg = Image.fromarray(acq[cameraname]).convert('I;16')")
            f.write("\nimg.save('img.tif')")

        def asyn1(f):
            def wrapper(*args, **kwargs):
                thr = Thread(target=f, args=args, kwargs=kwargs)
                thr.start()

            return wrapper

        @asyn1
        def backgroundcamera():
            os.system("python backgroundcamera.py")

        #      self.img = acq
        def killcmd1():
            pid = self.search_pid()
            os.system("taskkill /F /PID {}".format(pid))

        backgroundcamera()
        # killcmd1()
        # os.remove('backgroundcamera.py')

    def backgroundrotation(self, goalangle):
        arcgoalangle = goalangle * math.pi / 180
        with open('backgroundtilt.py', 'w') as f:
            f.write('from temscript import NullMicroscope')
            f.write('\nfrom temscript import Microscope')
            f.write('\nTEM = ' + str(self.TEM))
            f.write('\ngoalangle = ' + str(arcgoalangle))
            f.write('\nrotationspeed = ' + str(self.rotationspeed))
            f.write("\nTEM.set_stage_position(a=goalangle,method='GO',speed=rotationspeed)")

        def asyn(f):
            def wrapper(*args, **kwargs):
                thr = Thread(target=f, args=args, kwargs=kwargs)
                thr.start()

            return wrapper

        @asyn
        def backgroundtilt():
            os.system("python backgroundtilt.py")

        def killcmd():
            pid = self.search_pid()
            os.system("taskkill /F /PID {}".format(pid))

        backgroundtilt()
        # killcmd()

    def backgroundrotation_correction(self):
        arcgoalangle = endangle * math.pi / 180
        arcstartangle = startangle * math.pi / 180
        TEM.set_stage_position(a=arcstartangle, method='GO')
        with open('backgroundtilt.py', 'w') as f:
            f.write('from temscript import null_microscope')
            f.write('\nfrom temscript import microscope')
            f.write('\nTEM = ' + str(self.TEM))
            f.write('\ngoalangle = ' + str(arcgoalangle))
            f.write('\nrotationspeed = ' + str(self.rotationspeed))
            f.write("\nTEM.set_stage_position(a=goalangle,method='GO',speed=rotationspeed)")

        def asyn(f):
            def wrapper(*args, **kwargs):
                thr = Thread(target=f, args=args, kwargs=kwargs)
                thr.start()

            return wrapper

        @asyn
        def backgroundtilt():
            os.system("python backgroundtilt.py")

        def killcmd():
            pid = self.search_pid()
            os.system("taskkill /F /PID {}".format(pid))

        log = open("exp_log", "a+")
        print('Background tilt with drift correction start......', file=log, flush=True)
        drift_time = drift_step / degreespeed
        startstage = TEM.get_stage_position()
        startx = startstage['x']
        starty = startstage['y']
        backgroundtilt()
        # killcmd()
        for i in range(1, drift_num):
            sleep(drift_time)
            drift_value = np.loadtxt(filesavepath+"/"+'drift_value.txt')
            deltax = drift_value[i, 3] * 1e-9
            deltay = drift_value[i, 4] * 1e-9
            newx = startx - deltax
            newy = starty + deltay
            TEM.set_stage_position(x=newx, y=newy, method='GO')
            sleep(1)
        log.close

    def camera_delay_time(self):
        if self.binning == 1:
            camera_delay_time = 2.7568 + 0.9848 * self.exposuretime
        elif self.binning == 2:
            camera_delay_time = 1.64 + 0.99999 * self.exposuretime
        elif self.binning == 4:
            camera_delay_time = 1.3688 + 1.0005 * self.exposuretime
        elif self.binning == 8:
            camera_delay_time = 1.2925 + 1.002 * self.exposuretime
        return camera_delay_time

    def cr_acq(self, goalangle):
        # TEM = self.TEM
        TEM.set_beam_blanked(True)
        delay_time = self.camera_delay_time()
        real_delay_time = delay_time - self.freetime
        self.backgroundacquire()
        sleep(real_delay_time)
        # print(real_delay_time)
        self.backgroundrotation(goalangle=goalangle)
        TEM.set_beam_blanked(False)
        sleep(self.exposuretime)
        TEM.set_beam_blanked(True)

    def test_freetime(self):
        num = 1
        freetime_result = open("free_time_test_result.txt", "w+")
        for i in (0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5):
            self.freetime = i
            self.cr_acq(0.4 * num)
            num = num + 1
            img = Image.open('img.tif')
            img = np.array(img)
            mean_intensity = np.mean(img)
            print(str(i) + '  ' + str(mean_intensity), file=freetime_result, flush=True)


class stepwise_acquire:
    def __init__(self):
        self.cameraname = cameraname
        self.exposuretime = exposuretime
        self.binning = binning
        self.stepangle = stepangle
        self.rotationspeed = rotationspeed
        self.startangle = startangle
        self.endangle = endangle
        self.filesavepath = filesavepath
        self.num = num

    def loop_scred(self):
        log = open("exp_log", "a+")
        print('SCRED data collecting start......', file=log, flush=True)
        print('Moving to the start angle......', file=log, flush=True)
        arcstartangle = self.startangle * math.pi / 180
        TEM.set_stage_position(a=arcstartangle, method='GO')
        current_angle = self.startangle  # 当前角度
        image_counter = 1  # 图像计数器
        while True:
            goalangle = self.startangle + self.stepangle * image_counter
            print('Stage is moving to the ' + str(goalangle) +
                  ' degrees while camera exposure......', file=log, flush=True)
            synchro_tilt_acquire().cr_acq(goalangle=goalangle)
            print('Waiting ' + str(exposuretime) + ' s for the ' + str(image_counter) +
                  '/' + str(self.num) + ' exposure cycle......', file=log, flush=True)
            sleep(exposuretime)
            if image_counter < 10:
                imgfilename = '000' + str(image_counter) + '.tif'
                os.rename('img.tif', str(imgfilename))
            elif image_counter >= 10 and image_counter < 100:
                imgfilename = '00' + str(image_counter) + '.tif'
                os.rename('img.tif', str(imgfilename))
            elif image_counter >= 100 and image_counter < 1000:
                imgfilename = '0' + str(image_counter) + '.tif'
                os.rename('img.tif', str(imgfilename))
            else:
                imgfilename = str(image_counter) + '.tif'
                os.rename('img.tif', str(imgfilename))
            print('Image ' + str(imgfilename) + ' has been saved', file=log, flush=True)
            currentstage = TEM.get_stage_position()
            arccurrentalpha = currentstage['a']
            arccurrentbeta = currentstage['b']
            currentalpha = arccurrentalpha * 180 / math.pi
            currentbeta = arccurrentbeta * 180 / math.pi
            currentb = format(currentbeta, '.2f')
            # print(str(currentalpha) + '  ' + str(currentbeta))
            framealpha = currentalpha + stepangle / 2
            framealpha = format(framealpha, '.2f')
            writelog = '''EDpatterns\\''' + imgfilename + ' ' + str(framealpha) + ' ' + str(currentb)
            with open('ImageList.txt', 'a+') as f:
                f.write('\n' + str(writelog))
            print('Image file name and current alpha and beta angles have been saved to ImageList.txt',
                  file=log, flush=True)
            current_angle += self.stepangle
            # 更新图像计数器
            image_counter += 1
            # 判断是否达到结束条件
            if (self.stepangle > 0 and current_angle > self.endangle) or (
                    self.stepangle < 0 and current_angle < self.endangle):
                break

    def loop_red(self):
        log = open("exp_log", "a+")
        print('RED data collecting start......', file=log, flush=True)
        print('Moving to the start angle......', file=log, flush=True)
        init_param = TEM.get_camera_param(self.cameraname)
        param = dict(init_param)
        param["image_size"] = "FULL"
        param["exposure(s)"] = self.exposuretime
        param["binning"] = self.binning
        TEM.set_camera_param(self.cameraname, param)
        print('Moving to the start angle......', file=log, flush=True)
        arcstartangle = self.startangle * math.pi / 180
        TEM.set_stage_position(a=arcstartangle, method='GO')
        for i in range(1, int(self.num + 2)):
            print('Waiting ' + str(exposuretime) + ' s for the ' + str(i) + '/' + str(
                self.num + 1) + ' exposure cycle......', file=log, flush=True)
            TEM.set_beam_blanked(False)
            acq = TEM.acquire(self.cameraname)
            TEM.set_beam_blanked(True)
            img = Image.fromarray(acq[self.cameraname]).convert('I;16')
            if i < 10:
                imgfilename = '000' + str(i) + '.tif'
                img.save(str(imgfilename))
            elif i >= 10 and i < 100:
                imgfilename = '00' + str(i) + '.tif'
                img.save(str(imgfilename))
            elif i >= 100 and i < 1000:
                imgfilename = '0' + str(i) + '.tif'
                img.save(imgfilename)
            else:
                imgfilename = str(i) + '.tif'
                img.save(imgfilename)
            print('Image ' + str(imgfilename) + ' has been saved', file=log, flush=True)
            currentstage = TEM.get_stage_position()
            arccurrentalpha = currentstage['a']
            arccurrentbeta = currentstage['b']
            currentalpha = arccurrentalpha * 180 / math.pi
            currenta = format(currentalpha, '.2f')
            currentbeta = arccurrentbeta * 180 / math.pi
            currentb = format(currentbeta, '.2f')
            writelog = '''EDpatterns\\''' + imgfilename + ' ' + str(currenta) + ' ' + str(currentb)
            with open('ImageList.txt', 'a+') as f:
                f.write(str(writelog) + '\n')
            print('Image file name and current alpha and beta angles have been saved to ImageList.txt',
                  file=log, flush=True)
            nextangle = currentalpha + self.stepangle
            if abs(nextangle) < abs(endangle):
                print('Stage is moving to the ' + str(nextangle) + ' degrees......', file=log, flush=True)
                arcnextangle = nextangle * math.pi / 180
                TEM.set_stage_position(a=arcnextangle, method='GO')
            else:
                print('Collecting task finished! All the images have been saved!', file=log, flush=True)

    def loop_scred_drift_correct(self):
        log = open("exp_log", "a+")
        print('SCRED data collecting start......', file=log, flush=True)
        print('Moving to the start angle......', file=log, flush=True)
        arcstartangle = self.startangle * math.pi / 180
        TEM.set_stage_position(a=arcstartangle, method='GO')
        drift_count = 1
        num_ed_pre_drift = drift_step / stepangle
        startstage = TEM.get_stage_position()
        startx = startstage['x']
        starty = startstage['y']
        print('The initial stage x and y positions are: ' + str(startx) + ',' + str(starty), file=log, flush=True)
        for i in range(1, int(self.num + 1)):
            goalangle = self.startangle + self.stepangle * i
            # print(goalangle)
            print('Stage is moving to the ' + str(goalangle) +
                  ' degrees while camera exposure......', file=log, flush=True)
            synchro_tilt_acquire().cr_acq(goalangle=goalangle)
            print('Waiting ' + str(exposuretime) + ' s for the ' + str(i) +
                  '/' + str(self.num) + ' exposure cycle......', file=log, flush=True)
            sleep(exposuretime)
            if i < 10:
                imgfilename = '000' + str(i) + '.tif'
                os.rename('img.tif', str(imgfilename))
            elif i >= 10 and i < 100:
                imgfilename = '00' + str(i) + '.tif'
                os.rename('img.tif', str(imgfilename))
            elif i >= 100 and i < 1000:
                imgfilename = '0' + str(i) + '.tif'
                os.rename('img.tif', str(imgfilename))
            else:
                imgfilename = str(i) + '.tif'
                os.rename('img.tif', str(imgfilename))
            print('Image ' + str(imgfilename) + ' has been saved', file=log, flush=True)
            currentstage = TEM.get_stage_position()
            arccurrentalpha = currentstage['a']
            arccurrentbeta = currentstage['b']
            currentalpha = arccurrentalpha * 180 / math.pi
            currentbeta = arccurrentbeta * 180 / math.pi
            currentb = format(currentbeta, '.2f')
            currentx = currentstage['x']
            currenty = currentstage['y']
            # print(str(currentalpha) + '  ' + str(currentbeta))
            framealpha = currentalpha + stepangle / 2
            framealpha = format(framealpha, '.2f')
            writelog = '''EDpatterns\\''' + imgfilename + ' ' + str(framealpha) + ' ' + str(currentb)
            with open('ImageList.txt', 'a+') as f:
                f.write('\n' + str(writelog))
            print('Image file name and current alpha and beta angles have been saved to ImageList.txt',
                  file=log, flush=True)
            if int(i) % num_ed_pre_drift == 0:
                with open(filesavepath+"/"+'drift_value.txt', 'r') as file:
                    lines = file.readlines()
                    for line in lines:
                        data = line.split()
                        stored_angle = float(data[1])
                        drift_value_x = (float(data[3]) + float(data[5])) * 1e-9
                        drift_value_y = (float(data[4]) - float(data[6])) * 1e-9
                        if round(stored_angle) == round(currentalpha):
                            print('The No.' + str(drift_count) + ' drift cycle started',
                                  file=log, flush=True)
                            print('The drift values in nanometers are: ' + str(data[3]) + ',' + str(data[4]),
                                  file=log, flush=True)
                            drift_count += 1
                            newx = currentx - drift_value_x
                            newy = currenty + drift_value_y
                            TEM.set_stage_position(x=newx, y=newy, method='GO')
                            print('The corrected stage x and y positions are: ' + str(newx) + ',' + str(newy),
                                  file=log, flush=True)
                file.close()
            else:
                continue

    def loop_red_drift_correct(self):
        log = open("exp_log", "a+")
        print('RED data collecting start......', file=log, flush=True)
        print('Moving to the start angle......', file=log, flush=True)
        init_param = TEM.get_camera_param(self.cameraname)
        param = dict(init_param)
        param["image_size"] = "FULL"
        param["exposure(s)"] = self.exposuretime
        param["binning"] = self.binning
        TEM.set_camera_param(self.cameraname, param)
        arcstartangle = self.startangle * math.pi / 180
        TEM.set_stage_position(a=arcstartangle, method='GO')
        num_ed_pre_drift = drift_step / stepangle
        startstage = TEM.get_stage_position()
        startx = startstage['x']
        starty = startstage['y']
        drift_count = 1
        print('The initial stage x and y positions are: ' + str(startx) + ',' + str(starty), file=log, flush=True)
        for i in range(1, int(self.num + 2)):
            print('Waiting ' + str(exposuretime) + ' s for the ' + str(i) + '/' + str(
                self.num + 1) + ' exposure cycle......', file=log, flush=True)
            TEM.set_beam_blanked(False)
            acq = TEM.acquire(self.cameraname)
            TEM.set_beam_blanked(True)
            img = Image.fromarray(acq[self.cameraname]).convert('I;16')
            if i < 10:
                imgfilename = '000' + str(i) + '.tif'
                img.save(str(imgfilename))
            elif i >= 10 and i < 100:
                imgfilename = '00' + str(i) + '.tif'
                img.save(str(imgfilename))
            elif i >= 100 and i < 1000:
                imgfilename = '0' + str(i) + '.tif'
                img.save(imgfilename)
            else:
                imgfilename = str(i) + '.tif'
                img.save(imgfilename)
            print('Image ' + str(imgfilename) + ' has been saved', file=log, flush=True)
            currentstage = TEM.get_stage_position()
            arccurrentalpha = currentstage['a']
            arccurrentbeta = currentstage['b']
            currentalpha = arccurrentalpha * 180 / math.pi
            currenta = format(currentalpha, '.2f')
            currentbeta = arccurrentbeta * 180 / math.pi
            currentb = format(currentbeta, '.2f')
            writelog = '''EDpatterns\\''' + imgfilename + ' ' + str(currenta) + ' ' + str(currentb)
            with open('ImageList.txt', 'a+') as f:
                f.write('\n' + str(writelog))
            print('Image file name and current alpha and beta angles have been saved to ImageList.txt',
                  file=log, flush=True)
            nextangle = currentalpha + self.stepangle
            arcnextangle = nextangle * math.pi / 180
            print('Stage is moving to the ' + str(nextangle) + ' degrees......', file=log, flush=True)
            TEM.set_stage_position(a=arcnextangle, method='GO')
            currentstage = TEM.get_stage_position()
            arccurrentalpha = currentstage['a']
            currentalpha = arccurrentalpha * 180 / math.pi
            currentx = currentstage['x']
            currenty = currentstage['y']
            if int(i) % num_ed_pre_drift == 0:
                with open(filesavepath+"/"+'drift_value.txt', 'r') as file:
                    lines = file.readlines()
                    for line in lines:
                        data = line.split()
                        stored_angle = float(data[1])
                        drift_value_x = (float(data[3]) + float(data[5])) * 1e-9
                        drift_value_y = (float(data[4]) - float(data[6])) * 1e-9
                        if round(stored_angle) == round(currentalpha):
                            print('The No.' + str(drift_count) + ' drift cycle started',
                                  file=log, flush=True)
                            print('The drift values in nanometers are: ' + str(data[3]) + ',' + str(data[4]),
                                  file=log, flush=True)
                            drift_count += 1
                            newx = currentx - drift_value_x
                            newy = currenty + drift_value_y
                            TEM.set_stage_position(x=newx, y=newy, method='GO')
                            print('The corrected stage x and y positions are: ' + str(newx) + ',' + str(newy),
                                  file=log, flush=True)
                file.close()
            else:
                continue

    def loop_cred(self):
        log = open("exp_log", "a+")
        print('CRED data collecting start......', file=log, flush=True)
        print('Moving to the start angle......', file=log, flush=True)
        arcstartangle = self.startangle * math.pi / 180
        TEM.set_stage_position(a=arcstartangle, method='GO')
        sleep(3)
        print('Start to move to the end angle with the speed = ' + str(degreespeed) + ' degrees/s', file=log,
              flush=True)
        synchro_tilt_acquire().backgroundrotation(self.endangle)
        for num1 in range(0, 10000):
            print('Acquiring ' + str(num1) + ' of 10000 max frames...', file=log, flush=True)
            init_param = TEM.get_camera_param(cameraname)
            param = dict(init_param)
            param["image_size"] = "FULL"
            param["exposure(s)"] = exposuretime
            param["binning"] = binning
            TEM.set_camera_param(cameraname, param)
            acq = TEM.acquire(cameraname)
            img = Image.fromarray(acq['BM-Ceta']).convert('I;16')
            now = datetime.datetime.now()
            acquiretime = now.strftime("%Y%m%d-%H:%M:%S")
            currentstage = TEM.get_stage_position()
            arccurrentalpha = currentstage['a']
            arccurrentbeta = currentstage['b']
            currentalpha = arccurrentalpha * 180 / math.pi
            currenta = format(currentalpha, '.2f')
            currentbeta = arccurrentbeta * 180 / math.pi
            currentb = format(currentbeta, '.2f')
            if num1 < 10:
                imgfilename = '000' + str(num1) + '.tif'
                img.save(str(imgfilename))
            elif num1 >= 10 and num1 < 100:
                imgfilename = '00' + str(num1) + '.tif'
                img.save(str(imgfilename))
            elif num1 >= 100 and num1 < 1000:
                imgfilename = '0' + str(num1) + '.tif'
                img.save(imgfilename)
            else:
                imgfilename = str(num1) + '.tif'
                img.save(imgfilename)
            writelog = '''EDpatterns\\''' + imgfilename + ' ' + str(currenta) + ' ' + str(currentb)
            with open('ImageList.txt', 'a+') as f:
                f.write('\n' + str(writelog))
            print('Current tilt angle is ' + str(currentalpha), file=log, flush=True)
            print('Image file name and current alpha and beta angles have been saved to ImageList.txt',
                  file=log, flush=True)
            print('Image' + str(num1) + ' was acquired at ' + str(acquiretime), file=log, flush=True)
            if startangle > endangle:
                if currentalpha < endangle:
                    break
                else:
                    continue
            else:
                if currentalpha > endangle:
                    break
                else:
                    continue

    def loop_cred_drift_correct(self):
        log = open("exp_log", "a+")
        print('CRED data collecting with drift correction start......', file=log, flush=True)
        print('Moving to the start angle......', file=log, flush=True)
        arcstartangle = self.startangle * math.pi / 180
        TEM.set_stage_position(a=arcstartangle, method='GO')
        sleep(3)
        print('Start to move to the end angle with the speed = ' + str(degreespeed) + ' degrees/s', file=log,
              flush=True)
        synchro_tilt_acquire().backgroundrotation(self.endangle)
        drift_count = 1
        startstage = TEM.get_stage_position()
        startx = startstage['x']
        starty = startstage['y']
        for num1 in range(0, 10000):
            print('Acquiring ' + str(num1) + ' of 10000 max frames...', file=log, flush=True)
            init_param = TEM.get_camera_param(cameraname)
            param = dict(init_param)
            param["image_size"] = "FULL"
            param["exposure(s)"] = exposuretime
            param["binning"] = binning
            TEM.set_camera_param(cameraname, param)
            acq = TEM.acquire(cameraname)
            img = Image.fromarray(acq['BM-Ceta']).convert('I;16')
            now = datetime.datetime.now()
            acquiretime = now.strftime("%Y%m%d-%H:%M:%S")
            currentstage = TEM.get_stage_position()
            arccurrentalpha = currentstage['a']
            arccurrentbeta = currentstage['b']
            currentalpha = arccurrentalpha * 180 / math.pi
            currenta = format(currentalpha, '.2f')
            currentbeta = arccurrentbeta * 180 / math.pi
            currentb = format(currentbeta, '.2f')
            currentx = currentstage['x']
            currenty = currentstage['y']
            if num1 < 10:
                imgfilename = '000' + str(num1) + '.tif'
                img.save(str(imgfilename))
            elif num1 >= 10 and num1 < 100:
                imgfilename = '00' + str(num1) + '.tif'
                img.save(str(imgfilename))
            elif num1 >= 100 and num1 < 1000:
                imgfilename = '0' + str(num1) + '.tif'
                img.save(imgfilename)
            else:
                imgfilename = str(num1) + '.tif'
                img.save(imgfilename)
            writelog = '''EDpatterns\\''' + imgfilename + ' ' + str(currenta) + ' ' + str(currentb)
            with open('ImageList.txt', 'a+') as f:
                f.write('\n' + str(writelog))
            print('Current tilt angle is ' + str(currentalpha), file=log, flush=True)
            print('Image file name and current alpha and beta angles have been saved to ImageList.txt',
                  file=log, flush=True)
            print('Image' + str(num1) + ' was acquired at ' + str(acquiretime), file=log, flush=True)
            with open(filesavepath+"/"+'drift_value.txt', 'r') as file:
                lines = file.readlines()
                for line in lines:
                    data = line.split()
                    stored_angle = float(data[1])
                    drift_value_x = (float(data[3]) + float(data[5])) * 1e-9
                    drift_value_y = (float(data[4]) - float(data[6])) * 1e-9
                    if round(stored_angle) == round(currentalpha):
                        print('The No.' + str(drift_count) + ' drift cycle started',
                              file=log, flush=True)
                        print('The drift values in nanometers are: ' + str(data[3]) + ',' + str(data[4]),
                              file=log, flush=True)
                        drift_count += 1
                        newx = currentx - drift_value_x
                        newy = currenty + drift_value_y
                        TEM.set_stage_position(x=newx, y=newy, method='GO')
                        print('The corrected stage x and y positions are: ' + str(newx) + ',' + str(newy),
                              file=log, flush=True)
            file.close()
            if startangle > endangle:
                if currentalpha < endangle:
                    break
                else:
                    continue
            else:
                if currentalpha > endangle:
                    break
                else:
                    continue


class credcollecting:
    def __init__(self):
        codepath = os.getcwd()
        inputfile = codepath + '/params.json'
        cameraname = read_input_value(str(inputfile), 'cameraname')
        exposuretime = float(read_input_value(str(inputfile), 'Exposure_Time'))
        binning = int(read_input_value(str(inputfile), 'binning'))
        degreespeed = float(
            read_input_value(str(inputfile), 'Degree_Speed'))  # degreespeed range from 0.03 to 0.6 degrees/s
        stepangle = exposuretime * degreespeed
        rotationspeed = degreespeed / 29.332
        startangle = int(read_input_value(str(inputfile), 'Start_Angle'))
        endangle = int(read_input_value(str(inputfile), 'End_Angle'))
        filesavepath = read_input_value(str(inputfile), 'filesavepath')
        freetime = float(read_input_value(str(inputfile), 'Free_Time'))
        anglerange = abs(startangle - endangle)
        stepangle = degreespeed * exposuretime
        num = int(anglerange / stepangle)
        drift_step = float(read_input_value(str(inputfile), 'drift_step'))
        drift_num = int(anglerange / drift_step)
        drift_exposuretime = float(read_input_value(str(inputfile), 'drift_exposuretime'))
        drift_binning = int(read_input_value(str(inputfile), 'drift_binning'))
        drift_image_save = int(read_input_value(str(inputfile), 'drift_image_save'))

        beamstop = read_input_value(str(inputfile), 'beamstop')

        self.cameraname = cameraname
        self.exposuretime = exposuretime
        self.binning = binning
        self.stepangle = stepangle
        self.rotationspeed = rotationspeed
        self.freetime = freetime
        self.degreespeed = degreespeed
        self.startangle = startangle
        self.endangle = endangle
        self.num = num
        self.drift_num = drift_num
        self.drift_binning = drift_binning
        self.beamstop = beamstop

    def copyfile(self, srcfile, dstpath):  # 复制函数
        if not os.path.isfile(srcfile):
            print("%s not exist!" % (srcfile))
        else:
            fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
            if not os.path.exists(dstpath):
                os.makedirs(dstpath)  # 创建路径
            shutil.copy(srcfile, dstpath + '/' + fname)  # 复制文件
            # print("copy %s -> %s" % (srcfile, dstpath + fname))

    def runhead(self):
        now = datetime.datetime.now()
        starttime = now.strftime("%Y%m%d-%H:%M:%S")
        instrument = TEM.get_family()
        ###Setup log file###
        log = open("exp_log", "w+")

        ###Now start  3dED experiment###
        print('''
                     ============================================================================
                     |       _____  ______ _____            _ _           _   _                  |
                     |      |  __ \|  ____|  __ \          | | |         | | (_)                 |
                     |   ___| |__) | |__  | |  | | ___ ___ | | | ___  ___| |_ _ _ __   __ _      |
                     |  / __|  _  /|  __| | |  | |/ __/ _ \| | |/ _ \/ __| __| | '_ \ / _` |     |
                     | | (__| | \ \| |____| |__| | (_| (_) | | |  __/ (__| |_| | | | | (_| |     |
                     |  \___|_|  \_\______|_____/ \___\___/|_|_|\___|\___|\__|_|_| |_|\__, |v0.8 |
                     |                                                                 __/ |     |
                     |                                                                |___/      |
                     |  cREDcollecting: A python code for 3DED data collecting on ThermoFisher/  |
                     |                  FEI TEM with the TEMscripting interface.                 |
                     |         Version: 0.8.2                                                    |
                     |            Date: 2023-11-30                                               |
                     |          Author: Haiyang XIAN                                             |
                     |     Affiliation: EM center of Guangzhou Institute of Geochemistry, CAS    |
                     ============================================================================
                     ''', file=log, flush=True)
        print("                                                   ", file=log, flush=True)
        print("                                                   ", file=log, flush=True)

        ###Prepare optics for experiments###
        if TEM.get_beam_blanked() == 'True':
            TEM.set_beam_blanked('False')
        ###Get basic experimental conditions###
        workingvoltage = TEM.get_voltage()
        cameralength = TEM.get_indicated_camera_length()
        spotsize = TEM.get_spot_size_index()
        intensity = TEM.get_intensity()
        defocus = TEM.get_defocus()
        screencurrent = TEM.get_screen_current()
        currentpos = TEM.get_stage_position()
        ###write experimental conditions to log###
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Experimental conditions start+++++++', file=log, flush=True)
        print('WorkingVoltage = ' + str(workingvoltage) + ' kV', file=log, flush=True)
        print('SpotSize = ' + str(spotsize), file=log, flush=True)
        print('Intensity(C2) =' + str(intensity), file=log, flush=True)
        print('CameraLength = ' + str(cameralength) + ' m', file=log, flush=True)
        print('Defocus = ' + str(defocus), file=log, flush=True)
        print('ScreenCurrent = ' + str(screencurrent) + ' nA', file=log, flush=True)
        # print('ImageRotation = '+str(imagerotation)+' mrad',file=log,flush=True)
        print('Binning = ' + str(self.binning), file=log, flush=True)
        print('Drift_Binning = ' + str(self.drift_binning), file=log, flush=True)
        print('ExposureTime = ' + str(self.exposuretime) + ' s', file=log, flush=True)
        print('StartAngle = ' + str(self.startangle) + ' degrees', file=log, flush=True)
        print('EndAngle = ' + str(self.endangle) + ' degrees', file=log, flush=True)
        print('RotationSpeed = ' + str(self.degreespeed) + ' degree/s', file=log, flush=True)
        print('CurrentStagePosition = ' + str(currentpos), file=log, flush=True)
        # print('ImageHeight = '+str(imageheight),file=log,flush=True)
        # print('ImageWidth = '+str(imagewidth),file=log,flush=True)
        print('+++++++Experimental conditions end+++++++', file=log, flush=True)
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print("cRED was performed on a ThermoFisher/FEI " + instrument + " TEM", file=log, flush=True)
        print("Start time: " + starttime, file=log, flush=True)
        print("Working path is: " + filesavepath, file=log, flush=True)
        # print("A time-dependent folder has been created in the working path", file=log, flush=True)
        print("Experimental results will be saved to " + filesavepath, file=log, flush=True)
        print("A time-dependent folder has been created in the working path", file=log, flush=True)
        # print("Folders named 'red'/'cred'/'drift' are generated", file=log, flush=True)
        # print("Diffraction figures are saved in the 'red' and 'cred' folders", file=log, flush=True)
        # print("Drift_measurement results are saved in the 'drift' folder", file=log, flush=True)

    def generate_pets_file(self):
        log = open("exp_log", "a+")
        cameralength = TEM.get_indicated_camera_length()
        if cameralength == 1.35:
            Aprepixel = 0.000413 * self.binning
        elif cameralength == 1.1:
            Aprepixel = 0.000522 * self.binning
        elif cameralength == 0.8400000000000001:
            Aprepixel = 0.000670 * self.binning
        elif cameralength == 0.66:
            Aprepixel = 0.000908 * self.binning
        elif cameralength == 0.52:
            Aprepixel = 0.00114 * self.binning
        elif cameralength == 0.41:
            Aprepixel = 0.00144 * self.binning
        elif cameralength == 0.33:
            Aprepixel = 0.00169 * self.binning
        else:
            Aprepixel = "0.00134 Please define by yourself!"

        if self.binning == 1:
            bin = 4

        elif self.binning == 2:
            bin = 2

        else:
            bin = 1

        if self.beamstop == "full":
            if self.binning == 1:
                beamstop = ("\n"
                            "beamstop\n"
                            "0 1930\n"
                            "1856 1930\n"
                            "1944 1860\n"
                            "2156 1860\n"
                            "2228 1910\n"
                            "2476 2010\n"
                            "2540 2048\n"
                            "2476 2092\n"
                            "2228 2170\n"
                            "2156 2216\n"
                            "1944 2216\n"
                            "1856 2140\n"
                            "0	2140\n"
                            "endbeamstop\n")
            elif self.binning == 2:
                beamstop = ("\n"
                            "beamstop\n"
                            "0 965\n"
                            "928 965\n"
                            "972 930\n"
                            "1078 930\n"
                            "1114 955\n"
                            "1238 1005\n"
                            "1270 1024\n"
                            "1238 1046\n"
                            "1114 1085\n"
                            "1078 1108\n"
                            "972 1108\n"
                            "928 1070\n"
                            "0 1070\n"
                            "endbeamstop\n")
            elif self.binning == 4:
                beamstop = ("\n"
                            "beamstop\n"
                            "0 482\n"
                            "464 482\n"
                            "486 465\n"
                            "539 465\n"
                            "557 478\n"
                            "619 502\n"
                            "635 512\n"
                            "619 523\n"
                            "557 542\n"
                            "539 554\n"
                            "486 554\n"
                            "464 535\n"
                            "0 535\n"
                            "endbeamstop\n")
            elif self.binning == 8:
                beamstop = ("\n"
                            "beamstop\n"
                            "0 241\n"
                            "232 241\n"
                            "243 232\n"
                            "270 232\n"
                            "278 239\n"
                            "310 251\n"
                            "318 256\n"
                            "310 262\n"
                            "278 271\n"
                            "270 277\n"
                            "243 277\n"
                            "232 268\n"
                            "0 268\n"
                            "endbeamstop\n")
        elif self.beamstop == "half":
            if self.binning == 1:
                beamstop = ("\n"
                            "beamstop\n"
                            "0 1930\n"
                            "1384 1930\n"
                            "1472 1860\n"
                            "1684 1860\n"
                            "1756 1910\n"
                            "2004 2010\n"
                            "2068 2048\n"
                            "2004 2092\n"
                            "1756 2170\n"
                            "1684 2216\n"
                            "1472 2216\n"
                            "1384 2140\n"
                            "0 2140\n"
                            "endbeamstop\n")
            elif self.binning == 2:
                beamstop = ("\n"
                            "beamstop\n"
                            "0 965\n"
                            "692 965\n"
                            "736 930\n"
                            "842 930\n"
                            "878 955\n"
                            "1002 1005\n"
                            "1034 1024\n"
                            "1002 1046\n"
                            "878 1085\n"
                            "842 1108\n"
                            "736 1108\n"
                            "692 1070\n"
                            "0 1070\n"
                            "endbeamstop\n")
            elif self.binning == 4:
                beamstop = ("\n"
                            "beamstop\n"
                            "0 483\n"
                            "346 483\n"
                            "368 465\n"
                            "421 465\n"
                            "439 478\n"
                            "501 503\n"
                            "517 512\n"
                            "501 523\n"
                            "439 543\n"
                            "421 554\n"
                            "368 554\n"
                            "346 535\n"
                            "0 535\n"
                            "endbeamstop\n")
            else:
                beamstop = ("\n"
                            "beamstop\n"
                            "0 241\n"
                            "173 241\n"
                            "184 233\n"
                            "211 233\n"
                            "220 239\n"
                            "251 251\n"
                            "259 256\n"
                            "251 262\n"
                            "220 271\n"
                            "211 277\n"
                            "184 277\n"
                            "173 268\n"
                            "0 268\n"
                            "endbeamstop\n")
        else:
            beamstop = ("\n"
                        "beamstop no\n")

        f = open("new.pts", 'w')
        f.write("#####################")
        f.write("\n#                   #")
        f.write("\n#  PETS parameters  #")
        f.write("\n#                   #")
        f.write("\n#####################")
        f.write("\nlambda 0.0251")
        f.write("\nAperpixel " + str(Aprepixel))
        f.write("\nphi 1.00")
        f.write("\nomega 270.0")
        f.write("\nnoiseparameters 3.5 38")
        f.write("\ngeometry continuous")
        f.write("\nreflectionsize 12")
        f.write("\nbin " + str(bin))
        f.write("\ndstarmax  1.25")
        f.write("\ndstarmaxps  1.25")
        f.write("\n")
        f.write(str(beamstop))
        f.write("\n")
        f.write("imagelist\n")
        f.close()

        file1 = 'new.pts'
        file2 = 'ImageList.txt'

        def merge(file1, file2):
            f1 = open(file1, 'a', encoding='utf-8')
            with open(file2, 'r', encoding='utf-8') as f2:
                for i in f2:
                    f1.write(i)

        merge(file1, file2)
        f = open("new.pts", 'a+')
        f.write("\nendimagelist")
        f.write("\n")
        f.write("\nreconstruction")
        f.write("\nhk0   1 0 0 0 1 0 0 0 0")
        f.write("\nhk1   1 0 0 0 1 0 0 0 1")
        f.write("\nhk2   1 0 0 0 1 0 0 0 2")
        f.write("\nhk3   1 0 0 0 1 0 0 0 3")
        f.write("\nh0l   1 0 0 0 0 1 0 0 0")
        f.write("\nh1l   1 0 0 0 0 1 0 1 0")
        f.write("\nh2l   1 0 0 0 0 1 0 2 0")
        f.write("\nh3l   1 0 0 0 0 1 0 3 0")
        f.write("\n0kl   0 1 0 0 0 1 0 0 0")
        f.write("\n1kl   0 1 0 0 0 1 1 0 0")
        f.write("\n2kl   0 1 0 0 0 1 2 0 0")
        f.write("\n3kl   0 1 0 0 0 1 3 0 0")
        f.write("\nhhl   1 1 0 0 0 1 0 0 0")
        f.write("\nh+1hl   1 1 0 0 0 1 1 0 0")
        f.write("\nh+2hl   1 1 0 0 0 1 2 0 0")
        f.write("\nendreconstruction")
        f.close()
        print("A 'new.pts' file has been generated, you can open it with the PETS2 software.", file=log, flush=True)

    def red_no_correct_run(self):
        t0 = time.time()
        workingpath = initwork().setup_workingpath()
        redpath = initwork().setup_redpath(workingpath)
        edpath = initwork().setup_edpath(redpath)
        os.chdir(edpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run uses the stepwise rotation method without drift correction', file=log, flush=True)
        print(str(self.num) + " frames will be saved to the 'red' folder", file=log, flush=True)
        print("The generated 'ImageList.txt' file records the file names and tilt angles", file=log, flush=True)
        # messagebox().before_ed_acquire()
        TEM.set_column_valves_open(True)
        TEM.set_screen_position('UP')
        stepwise_acquire().loop_red()
        self.generate_pets_file()
        self.copyfile('new.pts', redpath)
        sleep(1)
        os.remove('new.pts')
        t1 = time.time()
        dt = t1 - t0
        dt = format(dt, '.2f')
        print('Total elapsed time: ' + str(dt) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        log.close()
        self.copyfile('exp_log', redpath)
        sleep(1)
        os.remove('exp_log')
        TEM.set_screen_position('DOWN')
        TEM.set_beam_blanked(True)
        TEM.set_column_valves_open(False)

    def scred_no_correct_run(self):
        t0 = time.time()
        workingpath = initwork().setup_workingpath()
        scredpath = initwork().setup_scredpath(workingpath)
        edpath = initwork().setup_edpath(scredpath)
        os.chdir(edpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run uses the stepwise continuous rotation method without drift correction', file=log, flush=True)
        print(str(self.num) + " frames will be saved to the 'scred' folder", file=log, flush=True)
        print("The generated 'ImageList.txt' file records the file names and tilt angles.", file=log, flush=True)
        # messagebox().before_ed_acquire()
        TEM.set_column_valves_open(True)
        TEM.set_screen_position('UP')
        stepwise_acquire().loop_scred()
        self.generate_pets_file()
        self.copyfile('new.pts', scredpath)
        sleep(1)
        os.remove('new.pts')
        t1 = time.time()
        dt = t1 - t0
        dt = format(dt, '.2f')
        print('Total elapsed time: ' + str(dt) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        log.close()
        self.copyfile('exp_log', scredpath)
        sleep(1)
        os.remove('exp_log')
        os.remove('backgroundtilt.py')
        os.remove('backgroundcamera.py')
        TEM.set_screen_position('DOWN')
        TEM.set_beam_blanked(True)
        TEM.set_column_valves_open(False)

    def cred_no_correct_run(self):
        t0 = time.time()
        workingpath = initwork().setup_workingpath()
        credpath = initwork().setup_credpath(workingpath)
        edpath = initwork().setup_edpath(credpath)
        os.chdir(edpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run uses the continuous rotation method without drift correction', file=log, flush=True)
        print("The generated 'ImageList.txt' file records the file names and tilt angles.", file=log, flush=True)
        # messagebox().before_ed_acquire()
        TEM.set_column_valves_open(True)
        TEM.set_screen_position('UP')
        stepwise_acquire().loop_cred()
        self.generate_pets_file()
        self.copyfile('new.pts', credpath)
        sleep(1)
        os.remove('new.pts')
        t1 = time.time()
        dt = t1 - t0
        dt = format(dt, '.2f')
        print('Total elapsed time: ' + str(dt) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        log.close()
        self.copyfile('exp_log')
        sleep(1)
        os.remove('exp_log')
        TEM.set_screen_position('DOWN')
        TEM.set_beam_blanked(True)
        TEM.set_column_valves_open(False)

    def cred_online_correct_run(self):
        t0 = time.time()
        workingpath = initwork().setup_workingpath()
        credpath = initwork().setup_credpath(workingpath)
        driftpath = initwork().setup_driftpath(workingpath)
        edpath = initwork().setup_edpath(credpath)
        os.chdir(driftpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run measures the drift value', file=log, flush=True)
        print(str(self.drift_num + 1) + " frames will be saved to the 'drift' folder", file=log, flush=True)
        # messagebox().before_drift_correction()
        TEM.set_column_valves_open(True)
        TEM.set_screen_position('UP')
        print('Start to measure the drift during rotating the stage with alpha......', file=log, flush=True)
        drift_measure().xy_shift()
        print('Drift measurement finished, a drift_value.txt file has been generated.', file=log, flush=True)
        t1 = time.time()
        dt1 = t1 - t0
        dt1 = format(dt1, '.2f')
        print('Total elapsed time for drift measurement: ' + str(dt1) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        self.copyfile(filesavepath+"/"+'drift_value.txt', edpath)
        os.chdir(edpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run uses the continuous rotation method with drift correction', file=log, flush=True)
        print(str(self.num) + " frames will be saved to the 'cred' folder", file=log, flush=True)
        print("The generated 'ImageList.txt' file records the file names and tilt angles.", file=log, flush=True)
        # messagebox().before_ed_acquire()
        stepwise_acquire().loop_cred_drift_correct()
        self.generate_pets_file()
        self.copyfile('new.pts', credpath)
        sleep(1)
        os.remove('new.pts')
        t2 = time.time()
        dt2 = t2 - t1
        dt2 = format(dt2, '.2f')
        print('Total elapsed time: ' + str(dt2) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        log.close()
        self.copyfile('exp_log', credpath)
        sleep(1)
        os.remove('exp_log')
        TEM.set_screen_position('DOWN')
        TEM.set_beam_blanked(True)
        TEM.set_column_valves_open(False)

    def scred_online_correct_run(self):
        t0 = time.time()
        workingpath = initwork().setup_workingpath()
        scredpath = initwork().setup_scredpath(workingpath)
        edpath = initwork().setup_edpath(scredpath)
        driftpath = initwork().setup_driftpath(workingpath)
        os.chdir(driftpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run measures the drift value', file=log, flush=True)
        print(str(self.drift_num + 1) + " frames will be saved to the 'drift' folder", file=log, flush=True)
        # messagebox().before_drift_correction()
        TEM.set_column_valves_open(True)
        TEM.set_screen_position('UP')
        print('Start to measure the drift during rotating the stage with alpha......', file=log, flush=True)
        drift_measure().xy_shift()
        print('Drift measurement finished, a drift_value.txt file has been generated.', file=log, flush=True)
        t1 = time.time()
        dt1 = t1 - t0
        dt1 = format(dt1, '.2f')
        print('Total elapsed time for drift measurement: ' + str(dt1) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        self.copyfile(filesavepath+"/"+'drift_value.txt', edpath)
        os.chdir(edpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run uses the stepwise continuous rotation method with drift correction', file=log, flush=True)
        print(str(self.num) + " frames will be saved to the 'scred' folder", file=log, flush=True)
        print("The generated 'ImageList.txt' file records the file names and tilt angles.", file=log, flush=True)
        # messagebox().before_ed_acquire()
        TEM.set_screen_position('UP')
        stepwise_acquire().loop_scred_drift_correct()
        self.generate_pets_file()
        self.copyfile('new.pts', scredpath)
        sleep(1)
        os.remove('new.pts')
        t2 = time.time()
        dt2 = t2 - t1
        dt2 = format(dt2, '.2f')
        print('Total elapsed time: ' + str(dt2) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        log.close()
        self.copyfile('exp_log', scredpath)
        sleep(1)
        os.remove('exp_log')
        os.remove('backgroundtilt.py')
        os.remove('backgroundcamera.py')
        TEM.set_screen_position('DOWN')
        TEM.set_beam_blanked(True)
        TEM.set_column_valves_open(False)

    def red_online_correct_run(self):
        t0 = time.time()
        workingpath = initwork().setup_workingpath()
        driftpath = initwork().setup_driftpath(workingpath)
        redpath = initwork().setup_redpath(workingpath)
        edpath = initwork().setup_edpath(redpath)
        os.chdir(driftpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run measures the drift value', file=log, flush=True)
        print(str(self.drift_num + 1) + " frames will be saved to the 'drift' folder", file=log, flush=True)
        # messagebox().before_drift_correction()
        TEM.set_column_valves_open(True)
        TEM.set_screen_position('UP')
        TEM.set_beam_blanked(False)
        print('Start to measure the drift during rotating the stage with alpha......', file=log, flush=True)
        drift_measure().xy_shift()
        print('Drift measurement finished, a drift_value.txt file has been generated.', file=log, flush=True)
        t1 = time.time()
        dt1 = t1 - t0
        dt1 = format(dt1, '.2f')
        print('Total elapsed time for drift measurement: ' + str(dt1) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        self.copyfile(filesavepath+"/"+'drift_value.txt', edpath)
        os.chdir(edpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run uses the stepwise rotation method with drift correction', file=log, flush=True)
        print(str(self.num) + " frames will be saved to the 'cred' folder", file=log, flush=True)
        print("The generated 'ImageList.txt' file records the file names and tilt angles.", file=log, flush=True)
        # messagebox().before_ed_acquire()
        TEM.set_screen_position('UP')
        stepwise_acquire().loop_red_drift_correct()
        self.generate_pets_file()
        self.copyfile('new.pts', redpath)
        sleep(1)
        os.remove('new.pts')
        t2 = time.time()
        dt2 = t2 - t1
        dt2 = format(dt2, '.2f')
        print('Total elapsed time: ' + str(dt2) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        log.close()
        self.copyfile('exp_log', redpath)
        sleep(1)
        os.remove('exp_log')
        TEM.set_screen_position('DOWN')
        TEM.set_beam_blanked(True)
        TEM.set_column_valves_open(False)

    def scred_offline_correct_run(self):
        t0 = time.time()
        workingpath = initwork().setup_workingpath()
        scredpath = initwork().setup_scredpath(workingpath)
        edpath = initwork().setup_edpath(scredpath)
        os.chdir(filesavepath)
        self.copyfile(filesavepath+"/"+'drift_value.txt', edpath)
        # messagebox().before_offline_correction()
        os.chdir(edpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run uses the stepwise continuous rotation method with drift correction', file=log, flush=True)
        print(str(self.num) + " frames will be saved to the 'scred' folder", file=log, flush=True)
        print("The generated 'ImageList.txt' file records the file names and tilt angles.", file=log, flush=True)
        # messagebox().before_ed_acquire()
        TEM.set_column_valves_open(True)
        TEM.set_screen_position('UP')
        stepwise_acquire().loop_scred_drift_correct()
        self.generate_pets_file()
        self.copyfile('new.pts', scredpath)
        sleep(1)
        os.remove('new.pts')
        t1 = time.time()
        dt = t1 - t0
        dt = format(dt, '.2f')
        print('Total elapsed time: ' + str(dt) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        log.close()
        self.copyfile('exp_log', scredpath)
        sleep(1)
        os.remove('exp_log')
        os.remove('backgroundtilt.py')
        os.remove('backgroundcamera.py')
        TEM.set_screen_position('DOWN')
        TEM.set_beam_blanked(True)
        TEM.set_column_valves_open(False)

    def cred_offline_correct_run(self):
        t0 = time.time()
        workingpath = initwork().setup_workingpath()
        credpath = initwork().setup_credpath(workingpath)
        edpath = initwork().setup_edpath(credpath)
        os.chdir(filesavepath)
        self.copyfile(filesavepath+"/"+'drift_value.txt', edpath)
        # messagebox().before_offline_correction()
        os.chdir(edpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run uses the continuous rotation method with drift correction', file=log, flush=True)
        print(str(self.num) + " frames will be saved to the 'cred' folder", file=log, flush=True)
        print("The generated 'ImageList.txt' file records the file names and tilt angles.", file=log, flush=True)
        # messagebox().before_ed_acquire()
        TEM.set_column_valves_open(True)
        TEM.set_screen_position('UP')
        stepwise_acquire().loop_cred_drift_correct()
        self.generate_pets_file()
        self.copyfile('new.pts', credpath)
        sleep(1)
        os.remove('new.pts')
        t1 = time.time()
        dt = t1 - t0
        dt = format(dt, '.2f')
        print('Total elapsed time: ' + str(dt) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        log.close()
        self.copyfile('exp_log', credpath)
        sleep(1)
        os.remove('exp_log')
        TEM.set_screen_position('DOWN')
        TEM.set_beam_blanked(True)
        TEM.set_column_valves_open(False)

    def red_offline_correct_run(self):
        t0 = time.time()
        workingpath = initwork().setup_workingpath()
        redpath = initwork().setup_redpath(workingpath)
        edpath = initwork().setup_edpath(redpath)
        os.chdir(filesavepath)
        # messagebox().before_offline_correction()
        self.copyfile(filesavepath+"/"+'drift_value.txt', edpath)
        os.chdir(edpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run uses the stepwise rotation method with drift correction', file=log, flush=True)
        print(str(self.num + 1) + " frames will be saved to the 'red' folder", file=log, flush=True)
        print("The generated 'ImageList.txt' file records the file names and tilt angles.", file=log, flush=True)
        # messagebox().before_ed_acquire()
        TEM.set_column_valves_open(True)
        TEM.set_screen_position('UP')
        stepwise_acquire().loop_red_drift_correct()
        self.generate_pets_file()
        self.copyfile('new.pts', redpath)
        sleep(1)
        os.remove('new.pts')
        t1 = time.time()
        dt = t1 - t0
        dt = format(dt, '.2f')
        print('Total elapsed time: ' + str(dt) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        log.close()
        self.copyfile('exp_log', redpath)
        sleep(1)
        os.remove('exp_log')
        TEM.set_screen_position('DOWN')
        TEM.set_beam_blanked(True)
        TEM.set_column_valves_open(False)

    def only_drift_run(self):
        t0 = time.time()
        self.workingpath = initwork().setup_workingpath()
        self.driftpath = initwork().setup_driftpath(self.workingpath)
        os.chdir(codepath)
        update_input()
        os.chdir(self.driftpath)
        self.runhead()
        log = open("exp_log", "a+")
        print('', file=log, flush=True)
        print('', file=log, flush=True)
        print('+++++++Acquire start+++++++', file=log, flush=True)
        print('This run only measures the drift value', file=log, flush=True)
        print(str(self.drift_num + 1) + " frames will be saved to the 'drift' folder", file=log, flush=True)
        # messagebox().before_drift_correction()
        TEM.set_column_valves_open(True)
        TEM.set_screen_position('UP')
        TEM.set_beam_blanked(False)
        print('Start to measure the drift during rotating the stage with alpha......', file=log, flush=True)
        drift_measure().xy_shift()
        print('Drift measurement finished, a drift_value.txt file has been generated.', file=log, flush=True)
        t1 = time.time()
        dt = t1 - t0
        dt = format(dt, '.2f')
        print('Total elapsed time: ' + str(dt) + ' s.', file=log, flush=True)
        print('+++++++Acquire end+++++++', file=log, flush=True)
        log.close()
        TEM.set_screen_position('DOWN')
        TEM.set_beam_blanked(True)
        TEM.set_column_valves_open(False)

# credcollecting().red_online_correct_run()
# credcollecting().red_offline_correct_run()
# credcollecting().only_drift_run()
# credcollecting().scred_run()
# credcollecting().scred_online_correct_run()
# credcollecting().scred_offline_correct_run()
# credcollecting().red_run()
# credcollecting().runhead()
# synchro_tilt_acquire().backgroundrotation_correction()
