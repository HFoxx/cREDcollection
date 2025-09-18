import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


from PyQt5 import QtCore, QtGui, QtWidgets
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QCheckBox


def create_merge_folder(output_folder, folder_name="Merged"):
    merged_path = os.path.join(output_folder, folder_name)
    if not os.path.exists(merged_path):
        os.makedirs(merged_path)
    return merged_path


def copy_and_rename_edpatterns(folder_paths, merge_path):
    for i, folder_path in enumerate(folder_paths):
        for sub_folder in ["scred", "red", "cred"]:
            src_edpatterns_path = os.path.join(folder_path, sub_folder, "EDpatterns")
            if os.path.exists(src_edpatterns_path):
                dst_edpatterns_path = os.path.join(merge_path, f"EDpatterns{i + 1}")
                shutil.copytree(src_edpatterns_path, dst_edpatterns_path)


def merge_imagelists(folder_paths, merge_path):
    all_imagelists = []
    header = []
    footer = []
    first_file_processed = False

    for i, folder_path in enumerate(folder_paths):
        for sub_folder in ["scred", "red", "cred"]:
            sub_folder_path = os.path.join(folder_path, sub_folder)
            pts_file = os.path.join(sub_folder_path, "new.pts")
            if os.path.exists(pts_file):
                with open(pts_file, 'r') as file:
                    lines = file.readlines()
                    in_imagelist = False
                    for line in lines:
                        if line.strip() == "imagelist":
                            in_imagelist = True
                            if not first_file_processed:
                                header = lines[:lines.index(line) + 1]
                                first_file_processed = True
                        elif line.strip() == "endimagelist":
                            in_imagelist = False
                            if not footer:
                                footer = lines[lines.index(line):]
                        elif in_imagelist:
                            new_line = line.replace('EDpatterns\\', f'EDpatterns{i + 1}\\')
                            all_imagelists.append(new_line)

    with open(os.path.join(merge_path, "new_merged.pts"), 'w') as file:
        file.writelines(header)
        file.writelines(all_imagelists)
        file.writelines(footer)


def get_subfolders(base_folder_path):
    return [os.path.join(base_folder_path, name) for name in os.listdir(base_folder_path)
            if os.path.isdir(os.path.join(base_folder_path, name))]

class FolderMergeApp(object):
    def setupUi(self, Form):
        Form.setObjectName("FolderMerge")
        Form.resize(700, 250)
        Form.setMinimumSize(QtCore.QSize(700, 250))
        Form.setStyleSheet("#FolderMerge{\n"
                           "    border-image: url(./img/LogViewer_BG.jpg);\n"
                           "}\n"
                           "\n"
                           "\n"
                           "QLabel{\n"
                           "    color: #4bbdda;\n"
                           "    font-weight: bold;\n"
                           "}\n"
                           "\n"
                           "QLineEdit{\n"
                           "    border: none;\n"
                           "    background: #00ffffff;\n"
                           "    border-bottom-style: solid;\n"
                           "    border-bottom-width: 1px;\n"
                           "    border-bottom-color: #abcdef;\n"
                           "    color: #fff;\n"
                           "}\n"
                           "\n"
                           "#checkBox{\n"
                           "    color: #4bbdda;\n"
                           "}\n"
                           "\n"
                           "\n"
                           "QPushButton{\n"
                           "    background-color:  qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(1, 32, 66, 255), stop:1 #aa4bbdda);\n"
                           "    border-radius: 5px;\n"
                           "    padding: 10px;\n"
                           "    font-weight: bold;\n"
                           "    color: #4bbdda;\n"
                           "\n"
                           "}\n"
                           "\n"
                           "QPushButton:hover{\n"
                           "    background-color: #789abc;\n"
                           "}\n"
                           "\n"
                           "QPushButton:pressed{\n"
                           "    background-color: #89abcd;\n"
                           "}\n"
                           "\n"
                           "#groupBox{\n"
                           "        background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #cc03070e, stop:1 #aa267ab8);\n"
                           "    border-radius: 5px;\n"
                           "    border:2px solid #4bbdda;\n"
                           "}\n"
                           "\n"
                           "")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setMaximumSize(QtCore.QSize(750, 300))
        self.groupBox.setStyleSheet("")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setContentsMargins(30, 20, 30, 20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(11)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setStyleSheet("")
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_4.setStyleSheet("")
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.horizontalLayout_4.addWidget(self.lineEdit_4)
        self.pushButton_5 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_5.setStyleSheet("")
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_4.addWidget(self.pushButton_5)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setStyleSheet("")
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_3.setStyleSheet("")
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout_3.addWidget(self.lineEdit_3)
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_3.setStyleSheet("")
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_3.addWidget(self.pushButton_3)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.addWidget(self.checkBox)
        self.pushButton_4 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_4.setObjectName("pushButton_4")
        self.verticalLayout.addWidget(self.pushButton_4)
        self.horizontalLayout.addWidget(self.groupBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        self.connect_Event()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("FolderMerge", "FolderMerge"))
        self.label_4.setText(_translate("FolderMerge", "输入文件夹："))
        self.pushButton_5.setText(_translate("FolderMerge", "选择文件夹"))
        self.label_3.setText(_translate("FolderMerge", "输出文件夹："))
        self.pushButton_3.setText(_translate("FolderMerge", "选择文件夹"))
        self.checkBox.setText(_translate("FolderMerge", "Same as Input Folder"))
        self.pushButton_4.setText(_translate("FolderMerge", "运行"))

    def connect_Event(self):
        self.pushButton_5.clicked.connect(self.select_input_folder)
        self.pushButton_3.clicked.connect(self.select_output_folder)
        self.pushButton_4.clicked.connect(lambda: self.run_merge(Form))
        self.checkBox.stateChanged.connect(self.update_output_entry)

    def select_input_folder(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog)
        if file_dialog.exec_() == QFileDialog.Accepted:
            folder_path = file_dialog.selectedFiles()[0]
            if folder_path:
                self.lineEdit_4.setText(folder_path)
                if self.checkBox.isChecked():
                    self.lineEdit_3.setText(folder_path)

    def select_output_folder(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog)
        if file_dialog.exec_() == QFileDialog.Accepted:
            folder_path = file_dialog.selectedFiles()[0]
            if folder_path:
                self.lineEdit_3.setText(folder_path)

    def update_output_entry(self):
        if self.checkBox.isChecked():
            self.lineEdit_3.setText(self.lineEdit_4.text())
        else:
            self.lineEdit_3.clear()

    def run_merge(self, Form):
        input_path = self.lineEdit_4.text()
        output_path = self.lineEdit_3.text()

        if not input_path or not output_path:
            QMessageBox.information(Form, "完成", "操作已完成！")
            return

        folder_paths = get_subfolders(input_path)
        merged_path = create_merge_folder(output_path, "Merge")
        copy_and_rename_edpatterns(folder_paths, merged_path)
        merge_imagelists(folder_paths, merged_path)
        QMessageBox.information(Form, "完成", "操作已完成！")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = FolderMergeApp()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
