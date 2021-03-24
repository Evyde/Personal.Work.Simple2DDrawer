import Controller
import Models
import Views

if __name__ == '__main__':
    a = Views.MainFrame()
    Controller.insertToTextarea(a.getTextarea(), Models.UniMessage("欢迎使用！命令行窗口可以进行简单的绘图。"
                                                                   "\n输入\"help(\"all command\")\"查看所有命令。"))
    Controller.insertToTextarea(a.getTextarea(), Models.UniMessage("\n>> "))
    a.getMainFrame().mainloop()
