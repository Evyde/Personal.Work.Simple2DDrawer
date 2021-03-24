import tkinter as tk


def insertToTextarea(textarea, msg):
    tagName = "#" + str(hash(msg))
    textarea.tag_add(tagName, tk.END)
    textarea.tag_config(tagName, foreground=msg.getColor())
    textarea.insert(tk.END, msg, tagName)


def setComboboxValue(combobox, values):
    combobox.config(values=values)
    combobox.current(0)
