#!/usr/bin/python3

# Import libraries
import sys
from tkinter import Tk
from pomodoro import Pomodoro


def main():
    args = sys.argv[1:]

    root = Tk()
    root.title("Pomodoro Habitica")
    # root.geometry('400x360')
    if args:
        # TODO: This is temporal. Pass argv in future.
        from tkinter import Frame, Label
        code = args[0]
        Frame(root).pack(side="top", fill="both", expand=True)
        Label(root, text=code).pack()
    else:
        Pomodoro(root).pack(side="top", fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()
