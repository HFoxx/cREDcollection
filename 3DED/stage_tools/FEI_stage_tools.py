import math
import os
import tkinter as tk
from temscript import null_microscope
from temscript import microscope
from time import sleep
import psutil
from threading import Thread
import numpy as np
from tkinter import filedialog

microscope = null_microscope.NullMicroscope()
# microscope = microscope.Microscope()
is_running = False  # 用于标记任务是否正在执行

def select_file():
    filename = filedialog.askopenfilename()
    drift_file_textbox.delete(0, tk.END)
    drift_file_textbox.insert(tk.END, filename)

def search_pid():
    pidlist = psutil.pids()
    for sub_pid in pidlist:
        process_info = psutil.Process(sub_pid)
        if process_info.name() == 'cmd.exe':
            pid = sub_pid
            return pid

def backgroundrotation(goalangle, degree_speed):
    arcgoalangle = math.radians(goalangle)
    rotation_speed = degree_speed / 29.332
    with open('backgroundtilt.py', 'w') as f:
        f.write('from temscript import null_microscope')
        f.write('\nfrom temscript import microscope')
        f.write('\nTEM = microscope.Microscope()')
        f.write('\ngoalangle = ' + str(arcgoalangle))
        f.write('\nrotationspeed = ' + str(rotation_speed))
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
        pid = search_pid()
        os.system("taskkill /F /PID {}".format(pid))
    backgroundtilt()
    killcmd()

def execute_go_script():
    global is_running
    is_running = True
    go_with_correction_button.config(state=tk.DISABLED)
    go_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    start_angle = float(start_angle_textbox.get())
    end_angle = float(end_angle_textbox.get())
    degree_speed = float(degree_speed_textbox.get())
    rotation_speed = degree_speed / 29.332
    arcstartangle = math.radians(start_angle)
    arcendangle = math.radians(end_angle)
    microscope.set_stage_position(a=arcstartangle, method='GO', speed=1)
    sleep(3)
    backgroundrotation(end_angle, degree_speed)
    #thread = Thread(target=microscope.set_stage_position(a=arcendangle, method='GO', speed=rotation_speed))
    #thread.start()
    while is_running == False:
        break

def execute_go_correct_script():
    global is_running
    is_running = True
    go_with_correction_button.config(state=tk.DISABLED)
    go_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    start_angle = float(start_angle_textbox.get())
    end_angle = float(end_angle_textbox.get())
    degree_speed = float(degree_speed_textbox.get())
    arcstartangle = math.radians(start_angle)
    arcendangle = math.radians(end_angle)
    microscope.set_stage_position(a=arcstartangle, method='GO', speed=1)
    sleep(3)
    log = open("exp_log", "a+")
    print('Background tilt with drift correction start......', file=log, flush=True)
    driftfile = str(drift_file_textbox.get())
    drift_value = np.loadtxt(driftfile)
    drift_step = drift_value[0, 1] - drift_value[1, 1]
    drift_time = drift_step / degree_speed
    startstage = microscope.get_stage_position()
    startx = startstage['x']
    starty = startstage['y']
    drift_num = abs(start_angle-end_angle)/ drift_step
    backgroundrotation(end_angle, degree_speed)
    for i in range(1, drift_num):
        sleep(drift_time)
        drift_value = np.loadtxt('drift_value.txt')
        deltax = drift_value[i, 3] * 1e-9
        deltay = drift_value[i, 4] * 1e-9
        newx = startx - deltax
        newy = starty + deltay
        microscope.set_stage_position(x=newx, y=newy, method='GO')
        sleep(1)
        while is_running == False:
            break
    log.close

def stop_execution():
    go_button.config(state=tk.NORMAL)
    go_with_correction_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    global is_running
    is_running = False

root = tk.Tk()
root.title('FEI Tilt Speed Controller')

# 创建文本框 startangle
start_angle_label = tk.Label(root, text='Start Angle:')
start_angle_label.grid(row=0, column=0, padx=10, pady=10)
start_angle_textbox = tk.Entry(root)
start_angle_textbox.grid(row=0, column=1, padx=10, pady=10)
start_angle_unit_label = tk.Label(root, text='degrees')
start_angle_unit_label.grid(row=0, column=2, padx=10, pady=10)

# 创建文本框 endangle
end_angle_label = tk.Label(root, text='End Angle:')
end_angle_label.grid(row=1, column=0, padx=10, pady=10)
end_angle_textbox = tk.Entry(root)
end_angle_textbox.grid(row=1, column=1, padx=10, pady=10)
end_angle_unit_label = tk.Label(root, text='degrees')
end_angle_unit_label.grid(row=1, column=2, padx=10, pady=10)

# 创建文本框 degree_speed
degree_speed_label = tk.Label(root, text='Degree Speed:')
degree_speed_label.grid(row=2, column=0, padx=10, pady=10)
degree_speed_textbox = tk.Entry(root)
degree_speed_textbox.grid(row=2, column=1, padx=10, pady=10)
degree_speed_unit_label = tk.Label(root, text='degrees/s')
degree_speed_unit_label.grid(row=2, column=2, padx=10, pady=10)

# 创建文本框drift file
drift_file_label = tk.Label(root, text='Drift File:')
drift_file_label.grid(row=3, column=0, padx=10, pady=10)
drift_file_textbox = tk.Entry(root)
drift_file_textbox.grid(row=3, column=1, padx=10, pady=10)

# 创建file按钮
file_button = tk.Button(root, text='...', command=select_file)
file_button.grid(row=3, column=2, padx=10, pady=10)

# 创建Go按钮
go_button = tk.Button(root, text='Go', command=execute_go_script)
go_button.grid(row=4, column=0, padx=10, pady=10)

# 创建Go with correction按钮
go_with_correction_button = tk.Button(root, text='Go with correction', command=execute_go_correct_script)
go_with_correction_button.grid(row=4, column=1, padx=10, pady=10)

# 创建Stop按钮
stop_button = tk.Button(root, text='Refresh', command=stop_execution,state=tk.DISABLED)
stop_button.grid(row=4, column=2, padx=10, pady=10)

root.mainloop()
