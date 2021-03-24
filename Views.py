from tkinter import *
from tkinter import filedialog
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import Controller
import Models
import threading


def plot(x, y, types="直线", window="new", xname="X轴", yname="Y轴", title=""):
    if window == "new":
        window = Toplevel()
        window.title("命令画图")
    plotCanvas = Canvas(window)
    toolbar = Frame(window)
    fig = plt.figure(dpi=150)
    fPlot = fig.add_subplot(111)
    canvasSpice = FigureCanvasTkAgg(fig, plotCanvas)
    canvasSpice.get_tk_widget().place(x=0, y=0)
    plt.rcParams['font.sans-serif'] = 'SimHei'
    fPlot.clear()
    plt.xlabel(xname, size=20)
    plt.ylabel(yname, size=20)
    plt.title(title, size=20)
    if types == "散点":
        plt.scatter(x, y, alpha=0.6)
    elif types == "直线":
        plt.plot(x, y)
    plt.grid(True)
    canvasSpice.draw()
    wh = []
    for i in canvasSpice.get_width_height():
        wh.append(i)
    NavigationToolbar2Tk(canvasSpice, toolbar).update()
    plotCanvas.pack(expand=True)
    toolbar.pack(expand=True)
    window.config(width=wh[0], height=wh[1])
    plotCanvas.config(width=wh[0], height=wh[1])
    toolbar.config(width=wh[0])
    window.resizable(width=False, height=False)
    return Models.UniMessage("画图完成！")


class MainFrame:
    __mainFrame = None
    __textarea = None
    __btn_open = None
    __btn_draw = None
    __label_filename = None
    __label_datasheet_choose = None
    __label_x_choose = None
    __label_y_choose = None
    __combobox_datasheet_choose = None
    __combobox_x_choose = None
    __combobox_y_choose = None
    __combobox_type_choose = None
    __filepath = ""

    def __init__(self):
        # 框架
        self.__mainFrame = Tk()
        self.__mainFrame.resizable(width=False, height=False)
        self.__mainFrame.title("简易2D图形绘制程序")
        textframe = Frame(self.__mainFrame)
        self.__textarea = Text(textframe, width=100, height=10)
        scrollbar = Scrollbar(textframe, orient=VERTICAL)
        scrollbar.config(command=self.__textarea.yview)
        scrollbar.pack(side=RIGHT, fill=Y)  # 靠右摆放, fill整个纵向
        self.__textarea.config(yscrollcommand=scrollbar.set)
        self.__textarea.pack(side=LEFT, fill=BOTH, expand=1)  # 靠左摆放, 左右的剩余空间都给textarea
        self.__textarea.config(state=NORMAL)  # 开启允许编辑text
        self.__textarea.delete(1.0, END)  # 删除所有之前的内容
        # 添加事件监听器
        self.__textarea.bind("<Return>", self.__commandLineListener)
        # 按钮等其它组件
        fileChooseFrame = Frame(self.__mainFrame)
        self.__btn_open = Button(fileChooseFrame, text='打开', width=5, height=1, command=self.__chooseFileListener)
        self.__label_filename = Label(fileChooseFrame, width=70, height=1, text="选择文件：", justify=LEFT, anchor="w")
        self.__btn_draw = Button(fileChooseFrame, text='画图', width=5, height=1, command=self.__drawListener)
        self.__combobox_type_choose = ttk.Combobox(fileChooseFrame, values=("散点", "直线"), state="readonly", width=4)
        self.__combobox_type_choose.current(0)

        dataChooseFrame = Frame(self.__mainFrame)
        self.__label_datasheet_choose = Label(dataChooseFrame, width=10, height=1, text="选择数据表：")
        self.__combobox_datasheet_choose = ttk.Combobox(dataChooseFrame, values=("请先选择文件！",), state=DISABLED)
        self.__combobox_datasheet_choose.current(0)
        self.__combobox_datasheet_choose.bind("<<ComboboxSelected>>", self.__chooseDatasheetListener)

        self.__label_x_choose = Label(dataChooseFrame, width=10, height=1, text="选择X轴：")
        self.__combobox_x_choose = ttk.Combobox(dataChooseFrame, values=("请先选择文件！",), state=DISABLED)
        self.__combobox_x_choose.current(0)

        self.__label_y_choose = Label(dataChooseFrame, width=10, height=1, text="选择Y轴：")
        self.__combobox_y_choose = ttk.Combobox(dataChooseFrame, values=("请先选择文件！",), state=DISABLED)
        self.__combobox_y_choose.current(0)
        # 排列
        fileChooseFrame.grid(row=0, sticky=NW)
        dataChooseFrame.grid(row=1, sticky=NW)
        textframe.grid(row=2)
        self.__label_filename.pack(side=LEFT)
        self.__btn_open.pack(side=LEFT)
        self.__btn_draw.pack(side=RIGHT)
        self.__combobox_type_choose.pack(side=RIGHT)
        self.__label_datasheet_choose.pack(side=LEFT)
        self.__combobox_datasheet_choose.pack(side=LEFT)
        self.__label_x_choose.pack(side=LEFT)
        self.__combobox_x_choose.pack(side=LEFT)
        self.__label_y_choose.pack(side=LEFT)
        self.__combobox_y_choose.pack(side=LEFT)

    def __drawListener(self):
        # 获得当前输入命令
        cmd = self.__textarea.get("end-1c linestart+3c", "end-1c")
        # 删除当前行并重新输出命令
        self.__textarea.delete("end-1c linestart", "end")
        self.__textarea.insert("end", f"\n>> {cmd}")
        self.__textarea.insert("end", "\n")
        if self.__filepath and self.__combobox_x_choose.get() and self.__combobox_y_choose.get():
            Controller.insertToTextarea(self.__textarea,
                                        Models.draw2D(Toplevel(self.__mainFrame),
                                                      self.__filepath, [self.__combobox_x_choose.get(),
                                                                        self.__combobox_y_choose.get()],
                                                      self.__combobox_datasheet_choose.get(),
                                                      self.__combobox_type_choose.get()))
        else:
            # 未知bug，红色不生效
            Controller.insertToTextarea(self.__textarea, Models.UniMessage("请先打开文件并选择数据轴！", "red"))
        self.__textarea.insert("end", "\n")
        Controller.insertToTextarea(self.__textarea, Models.UniMessage(f">> {cmd}"))

    def __chooseFileListener(self):
        filePath = filedialog.askopenfilename(filetypes=[("CSV数据表", ".csv"), ("Excel数据表", (".xls", ".xlsx"))])
        self.__label_filename.configure(text=filePath)
        self.__filepath = filePath
        Models.getDataDetails(filePath, self)

    def __chooseDatasheetListener(self, event):
        xy = Models.getFirstLineBySheetName(self.__filepath, self.__combobox_datasheet_choose.get())
        Controller.setComboboxValue(self.__combobox_x_choose, xy)
        Controller.setComboboxValue(self.__combobox_y_choose, xy)

    def getMainFrame(self):
        return self.__mainFrame

    def getTextarea(self):
        return self.__textarea

    def getDatasheetChooseCombobox(self):
        return self.__combobox_datasheet_choose

    def getXChooseCombobox(self):
        return self.__combobox_x_choose

    def getYChooseCombobox(self):
        return self.__combobox_y_choose

    def __deleteEnterChar(self):
        self.__textarea.delete("insert-1c", "insert")
        self.__textarea.focus_set()

    def __commandLineListener(self, event):
        if event.keycode == 13:
            # 获得当前输入命令
            cmd = self.__textarea.get("end-1c linestart+3c", "end-1c")
            # 删除当前行并重新输出命令
            self.__textarea.delete("end-1c linestart", "end")
            self.__textarea.insert("end", f"\n>> {cmd}")
            # 开一个线程，删除换行符
            threading.Thread(target=self.__deleteEnterChar).start()
            # 解析并输出命令
            self.__textarea.config(state=DISABLED)
            result = Models.interpreter(cmd)
            self.__textarea.config(state=NORMAL)
            self.__textarea.insert("end", "\n")
            Controller.insertToTextarea(self.__textarea, result)
            # 输出下一行开头
            Controller.insertToTextarea(self.__textarea, Models.UniMessage("\n>> "))
