import Controller
import csv
import os
import re
import xlrd

import Views


def draw2D(panel, filepath, xy, sheetname, types):
    panel.title(f"{filepath} - X轴：{xy[0]}, Y轴：{xy[1]}")
    # 实际上，这样按照数据轴名字查找的方法存在一个问题，即存在重名轴时会选择第一个
    try:
        if re.findall(".csv$", filepath):
            with open(filepath) as csvfile:
                init = False
                xs = []
                ys = []
                for i in csv.reader(csvfile):
                    if not init:
                        # 首次先获得x y轴的列数
                        xIndex = i.index(xy[0])
                        yIndex = i.index(xy[1])
                        init = True
                    else:
                        xs.append(float(i[xIndex]))
                        ys.append(float(i[yIndex]))
                return Command().plot(xs, ys, window=panel, xname=xy[0], yname=xy[1], title=filepath, types=types)
        else:
            data = xlrd.open_workbook(filepath).sheet_by_name(sheetname)
            nrows = data.nrows
            xs = []
            ys = []
            xIndex = 0
            yIndex = 0
            init = False
            for i in range(nrows):
                if not init:
                    # 首次先获得x y轴的列数
                    xIndex = data.row_values(0).index(xy[0])
                    yIndex = data.row_values(0).index(xy[1])
                    init = True
                else:
                    xs.append(float(data.cell_value(i, xIndex)))
                    ys.append(float(data.cell_value(i, yIndex)))
            return Command().plot(xs, ys, window=panel, xname=xy[0], yname=xy[1], title=filepath, types=types)
    except:
        panel.destroy()
        panel.update()
        return UniMessage("数据错误！请重试！", "red")


def getDatasheets(filepath):
    data = xlrd.open_workbook(filepath)
    return data.sheet_names()


def getFirstLineBySheetName(filepath, sheet):
    data = xlrd.open_workbook(filepath)
    st = data.sheet_by_name(sheet)
    return [str(st.cell_value(0, i)) for i in range(0, st.ncols)]


def getDataDetails(filepath, app):
    if filepath:
        if re.findall(".csv$", filepath):
            app.getDatasheetChooseCombobox().config(state="disabled")
            Controller.setComboboxValue(app.getDatasheetChooseCombobox(), ("CSV文件无需选择数据表！",))
            with open(filepath, newline='') as csvfile:
                c = csv.reader(csvfile)
                for i in c:
                    Controller.setComboboxValue(app.getXChooseCombobox(), i)
                    app.getXChooseCombobox().config(state="readonly")
                    Controller.setComboboxValue(app.getYChooseCombobox(), i)
                    app.getYChooseCombobox().config(state="readonly")
                    return

        else:
            Controller.setComboboxValue(app.getDatasheetChooseCombobox(), getDatasheets(filepath))
            app.getDatasheetChooseCombobox().config(state="readonly")
            xy = getFirstLineBySheetName(filepath, app.getDatasheetChooseCombobox().get())
            Controller.setComboboxValue(app.getXChooseCombobox(), xy)
            app.getXChooseCombobox().config(state="readonly")
            Controller.setComboboxValue(app.getYChooseCombobox(), xy)
            app.getYChooseCombobox().config(state="readonly")


def interpreter(command):
    # 整个套在一个try-catch块里，如果命令格式错误就直接返回
    # 同时创建一个函数列表，防止eval()执行Python内置函数产生错误
    try:
        if "=" in command:
            # 变量定义命令
            command = str(command).replace(" ", "")
            names = globals()
            names[str(command).split("=")[0]] = eval(str(command).split("=")[1])
            return UniMessage("定义成功！")
        # 解析命令参数
        args = re.findall("\(.*\)", command)[0]
        # 解析命令体
        cmd = str(re.findall("^.*\(", command)[0]).split("(")[0]
        if cmd == "print":
            # 调试
            args = str(args).replace("(", "")
            args = str(args).replace(")", "")
            return UniMessage(eval(args))
        # 检查命令体是否在所有命令里
        if cmd in Command().getAllCommand():
            # 执行命令
            return eval(f"Command().{cmd}{args}")
        else:
            raise Exception("Command Error!")
    except:
        return UniMessage("命令输入错误！输入help(\"all command\")查看所有命令！", "red")


class UniMessage:
    # 消息类，所有需要输出的文字必须经此封装，在窗口中可以显示颜色
    __color = ""
    __msg = ""

    def __init__(self, msg, color="blue"):
        self.__msg = msg
        self.__color = color

    def __str__(self):
        return str(self.__msg)

    def getColor(self):
        return self.__color


class Command:
    # 命令类，这样写只是为了好看，实际上每次调用命令都会新建一个Command对象，占内存
    __allCommand = ["help", "ls", "plot", "print", "cat"]

    def getAllCommand(self):
        return self.__allCommand

    def help(self, cmd):
        if cmd == "all command":
            return UniMessage(f"这是全部的命令：{self.getAllCommand()}\n，使用Python语法来定义变量，如x=[1,2,3,4,5]。")
        elif cmd == "help":
            return UniMessage("这是帮助命令。使用\"help(\"命令\")\"来查看对应命令的用法。")
        elif cmd == "ls":
            return UniMessage("输入\"ls(\"\")\"来查看目录下所有文件。")
        elif cmd == "cat":
            return UniMessage("输入\"cat(\"文件名称\")\"来查看文件内容。")
        elif cmd == "print":
            return UniMessage("和Python自带的print用法相同，可用来输出变量。")
        elif cmd == "plot":
            return UniMessage("plot(x, y, types=\"直线\", xname=\"X轴\", yname=\"Y轴\", title=\"\")"
                              "\n其中，x、y代表参与绘图的变量"
                              "\ntypes代表画图类型，包括\"直线\"和\"散点\""
                              "\nxname代表X轴名称，可忽略"
                              "\nyname代表Y轴名称，可忽略"
                              "\ntitle代表图表名称，可忽略")

    def ls(self, cmd):
        __includeHideFiles = False
        if 'a' in cmd:
            __includeHideFiles = True
        return UniMessage(f"当前目录文件：{os.listdir(os.path.abspath('.'))}")

    def plot(self, x, y, types="直线", window="new", xname="X轴", yname="Y轴", title=""):
        return Views.plot(x, y, types, window, xname, yname, title)

    def cat(self, filename):
        with open(filename, 'rt', encoding="utf-8") as f:
            return  UniMessage(f.read())