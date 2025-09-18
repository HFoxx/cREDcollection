import os
import signal
import sys
import subprocess
import tkinter
from threading import Thread, Event
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import StringVar
from tkinter import messagebox
import matplotlib.pyplot as plt

# 全局变量，标记Execute Module程序是否正在运行
codepath = os.getcwd()
thread = None
stop_event = Event()
def reload_ui():
    # 关闭当前窗口
    window.destroy()
    # 重新运行GUI1.py文件
    python = sys.executable
    GUI = codepath + "\\GUI1.py"
    subprocess.Popen([python, GUI])
    current_pid = os.getpid()

    # os.kill(current_pid, signal.SIGKILL)


    #sys.exit()


def save_input_variables():
    # 获取用户输入的变量值
    cameraname = combo_cameraname.get()
    exposuretime = entry_exposuretime.get()
    binning = combo_binning.get() # 修改获取binning值的方式
    degreespeed = entry_degreespeed.get()
    startangle = entry_startangle.get()
    endangle = entry_endangle.get()
    filesavepath = entry_filesavepath.get()
    freetime = entry_freetime.get()
    drift_step = entry_drift_step.get()
    drift_exposuretime = entry_drift_exposuretime.get()
    beamstop = combo_beamstop.get()
    drift_binning = combo_binning_drift.get()
    drift_image_save = checkbox_var.get()
    # drift_binning =
    if filesavepath == "":
        messagebox.showwarning("Warning", "Please choose a file save path!")
        return

    # 获取当前脚本所在的路径
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 保存文件路径
    file_path = os.path.join(script_dir, "input.cred")

    # 将变量值保存到文件
    with open(file_path, "w") as file:
        file.write(f"cameraname = {cameraname}\n")
        file.write(f"exposuretime = {exposuretime}\n")
        file.write(f"binning = {binning}\n")
        file.write(f"degreespeed = {degreespeed}\n")
        file.write(f"startangle = {startangle}\n")
        file.write(f"endangle = {endangle}\n")
        file.write(f"filesavepath = {filesavepath}\n")
        file.write(f"freetime = {freetime}\n")
        file.write(f"drift_step = {drift_step}\n")
        file.write(f"drift_exposuretime = {drift_exposuretime}\n")
        file.write(f"drift_binning = {drift_binning}\n")
        file.write(f"drift_image_save = {drift_image_save}\n")
        file.write(f"beamstop = {beamstop}\n")
    button_execute.config(state=tk.ACTIVE)
    #button_save.config(state = tk.DISABLED)
    # 提示保存成功
    label_result.config(text="input.cred has been saved！")
def choose_filesavepath():
    # 弹出文件夹选择对话框
    filesavepath = filedialog.askdirectory()
    entry_filesavepath.delete(0, tk.END)
    entry_filesavepath.insert(tk.END, filesavepath)

def execute_module():
    filesavepath = entry_filesavepath.get()
    if filesavepath == "":
        messagebox.showwarning("Warning", "Please choose a file save path!")
        return
    # button_reload_ui.config(state=tk.DISABLED)
    button_save.config(state=tk.DISABLED)
    button_execute.config(state=tk.DISABLED,background="yellow")
    label_result.config(text="Execution in progress...")
    global thread
    # if thread is not None and thread.is_alive():
    #     return
    # 实例化credcollecting类
    # 组合下拉框的值作为要执行的模块名称

    thread = Thread(target=execute_task)
    #thread = Thread(target=collector.only_drift_run)
    thread.daemon = True
    thread.start()

    # 调用某个模块方法
    # 在主线程中调度执行update_gui()
    # update_gui_after_execution()

def execute_task():
    import credcollecting
    # 拿到credcollecting这个类
    collector = credcollecting.credcollecting()
    # 拿到3DED model的值
    module_value = module_var.get()
    # 拿到Drift Correction的值
    correct_value = correct_var.get()
    if module_value == "only_drift":
        module = collector.only_drift_run
    else:
        module = getattr(collector, f"{module_value}_{correct_value}_run")
    # 直接调用module函数或方法
    # while not stop_event.is_set():
    module()
    window.after(0, update_gui_after_execution)


def update_gui_after_execution():
    # 在这里执行更新GUI的操作，例如禁用或启用按钮等
    button_execute.config(state=tk.DISABLED)
    button_save.config(state = tk.DISABLED)
    # button_reload_ui.config(state=tk.NORMAL)
    label_result.config(text="Execution completed.")



# def stop_execution():
#     # 将is_running设置为False，表示停止程序的运行
#     # global thread
#     # # print(thread)
#     # stop_event.set()
#     # label_result.config(text="Execution has been stopped.")
#     # if thread is not None:
#     #     # 设置停止事件并等待线程结束
#     #     thread.join()
#     #     thread = None
#     # # 取消之前调度的update_gui()函数的执行
#     sys.exit()

# def read_log_file():
#     log_file=



#创建主窗口
window = tk.Tk()
window.title("cREDcollecting GUI1 v0.8.2")

frame1 = tk.Frame(window, width=400, height =400)
frame1.grid(row=0, column=0, padx=10, pady=0)

canvas = tk.Canvas(window, height=2)
canvas.grid(row=1, column=0, padx=10, pady=10)
canvas.create_line(0,1,400,1,fill="gray",width=3)

frame2 = tk.Frame(window,  width=400, height =400)
frame2.grid(row=2, column=0, padx=10, pady=0)

canvas = tk.Canvas(window, height=2)
canvas.grid(row=3, column=0, padx=10, pady=10)
canvas.create_line(0,1,400,1,fill="gray",width=3)

frame3 = tk.Frame(window,  width=400, height =400)
frame3.grid(row=4, column=0, padx=10, pady=0)


# log_box = tk.Text(window, width=50)
# log_box.place(x=400,y=10, width=400,height=500)
#
# label_logfilepath = tk.Label(window, text="Log File Path:")
# label_logfilepath.place(x=400,y=520, sticky=tk.W)
# entry_filesavepath = tk.Entry(window)
# entry_filesavepath.place(x=450,y=520, padx=5, pady=5, sticky=tk.W)
# button_filesavepath = tk.Button(window, text="...", command=choose_filesavepath)
# button_filesavepath.place(x=500,y=520, padx=5, pady=5, sticky=tk.W)



#创建输入框和标签
label_cameraname = tk.Label(frame1, text="Camera Name:")
label_cameraname.grid(row=0, column=0, sticky=tk.W)
combo_cameraname = ttk.Combobox(frame1, values=["BM-Ceta", "CCD"], state="readonly")
combo_cameraname.current(0)
combo_cameraname.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)


label_exposuretime = tk.Label(frame1, text="Exposure Time:")
label_exposuretime.grid(row=1, column=0, sticky=tk.W)
label_exposuretime_unit = tk.Label(frame1, text="seconds")
label_exposuretime_unit.grid(row=1, column=2, sticky=tk.W)
entry_exposuretime = tk.Entry(frame1)
entry_exposuretime.insert(tk.END, "2")
entry_exposuretime.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

label_binning = tk.Label(frame1, text="Binning:")
label_binning.grid(row=2, column=0, sticky=tk.W)
#创建binning下拉框
binning_values = ["1", "2", "4", "8"]
combo_binning = ttk.Combobox(frame1, values=binning_values, state="readonly")
combo_binning.current(3)
combo_binning.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)



label_degreespeed = tk.Label(frame1, text="Degree Speed:")
label_degreespeed.grid(row=3, column=0, sticky=tk.W)
label_degreespeed_unit = tk.Label(frame1, text="degrees/s")
label_degreespeed_unit.grid(row=3, column=2, sticky=tk.W)
entry_degreespeed = tk.Entry(frame1)
entry_degreespeed.insert(tk.END, "0.2")
entry_degreespeed.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

label_startangle = tk.Label(frame1, text="Start Angle:")
label_startangle.grid(row=4, column=0, sticky=tk.W)
label_startangle_unit = tk.Label(frame1, text="degrees")
label_startangle_unit.grid(row=4, column=2, sticky=tk.W)
entry_startangle = tk.Entry(frame1)
entry_startangle.insert(tk.END, "-60")
entry_startangle.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

label_endangle = tk.Label(frame1, text="End Angle:")
label_endangle.grid(row=5, column=0, sticky=tk.W)
label_endangle_unit = tk.Label(frame1, text="degrees")
label_endangle_unit.grid(row=5, column=2, sticky=tk.W)
entry_endangle = tk.Entry(frame1)
entry_endangle.insert(tk.END, "60")
entry_endangle.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

# 创建选择文件保存路径的按钮
label_filesavepath = tk.Label(frame1, text="File Save Path:")
label_filesavepath.grid(row=6, column=0, sticky=tk.W)
entry_filesavepath = tk.Entry(frame1)
entry_filesavepath.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
button_filesavepath = tk.Button(frame1, text="...", command=choose_filesavepath)
button_filesavepath.grid(row=6, column=2, padx=5, pady=5, sticky=tk.W)

label_freetime = tk.Label(frame2, text="Free Time:")
label_freetime.grid(row=1, column=0, sticky=tk.W)
label_freetime_unit = tk.Label(frame2, text="seconds")
label_freetime_unit.grid(row=1, column=2, sticky=tk.W)
entry_freetime = tk.Entry(frame2)
entry_freetime.insert(tk.END, "0.15")
entry_freetime.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

label_drift_step = tk.Label(frame2, text="Drift Step:")
label_drift_step.grid(row=2, column=0, sticky=tk.W)
label_drift_step_unit = tk.Label(frame2, text="degrees")
label_drift_step_unit.grid(row=2, column=2, sticky=tk.W)
entry_drift_step = tk.Entry(frame2)
entry_drift_step.insert(tk.END, "5")
entry_drift_step.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

label_drift_exposuretime = tk.Label(frame2, text="Drift Exposure Time:")
label_drift_exposuretime.grid(row=3, column=0, sticky=tk.W)
label_drift_exposuretime_unit = tk.Label(frame2, text="seconds")
label_drift_exposuretime_unit.grid(row=3, column=2, sticky=tk.W)
entry_drift_exposuretime = tk.Entry(frame2)
entry_drift_exposuretime.insert(tk.END, "1")
entry_drift_exposuretime.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

label_binning_drift = tk.Label(frame2, text="Drift Binning:")
label_binning_drift.grid(row=4, column=0, sticky=tk.W)
combo_binning_drift = ttk.Combobox(frame2, values=binning_values, state="readonly")
combo_binning_drift.current(1)
combo_binning_drift.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

checkbox_var = tk.IntVar()
checkbox = tk.Checkbutton(frame2, text="Save drift images", variable = checkbox_var)
checkbox.grid(row=5, column=1, padx=10, pady=10)

label_beamstop = tk.Label(frame3, text="Beam Stop:")
label_beamstop.grid(row=1, column=0, sticky=tk.W)
combo_beamstop = ttk.Combobox(frame3, values=["full", "half", "no"], state="readonly")
combo_beamstop.current(0)
combo_beamstop.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)


# 创建下拉框1，选择module的值
module_var = StringVar()
module_combobox = ttk.Combobox(frame3, textvariable=module_var, values=["only_drift", "red", "scred", "cred"])
module_combobox.grid(row=2, column=1, padx=5, pady=5)
module_combobox.current(1)
label_module_combobox = tk.Label(frame3, text="3DED Methods:")
label_module_combobox.grid(row=2, column=0, sticky=tk.W)

# 创建下拉框2，选择correct的值
correct_var = StringVar()
correct_combobox = ttk.Combobox(frame3, textvariable=correct_var, values=["online_correct", "offline_correct", "no_correct"])
correct_combobox.grid(row=3, column=1, padx=5, pady=5)
correct_combobox.current(0)
label_correct_combobox = tk.Label(frame3, text="Drift Correction:")
label_correct_combobox.grid(row=3, column=0, sticky=tk.W)

# 创建保存结果的标签
label_result = tk.Label(frame3, text="")
label_result.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

# 创建执行模块的按钮
button_execute = tk.Button(frame3, text="Execute", command=execute_module, state=tkinter.DISABLED)
button_execute.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)

# 创建保存按钮
button_save = tk.Button(frame3, text="Save", command=save_input_variables)
button_save.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)


# 创建停止执行的按钮
# button_stop = tk.Button(window, text="Stop", command=stop_execution)
# button_stop.grid(row=12, column=2, padx=5, pady=5, sticky=tk.W)

# button_reload_ui = tk.Button(window, text="Refresh UI", command=reload_ui)
# button_reload_ui.grid(row=13, column=0, padx=5, pady=5, sticky=tk.W)


# 运行主窗口的消息循环
window.mainloop()
