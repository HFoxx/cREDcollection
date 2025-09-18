# second_file.py
from tkinter import filedialog, messagebox
from queue import Queue

# 子线程执行的函数
def thread_func(q: Queue):
    messagebox.showinfo("提示", "请先选择需要处理的文件夹")
    folder_path = filedialog.askdirectory()  # 选择文件夹，路径保存于folder_path中
    q.put(folder_path)  # 将文件路径放入队列
