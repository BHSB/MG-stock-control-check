import tkinter
from tkinter import messagebox

'''
Interface:
-Title
-Instructions
-Textbox & button to open diaglogue box to select crystal report
-Textbox & button to select destination folder
-Button to run program
'''

class StockCheck:

    def __init__(self, master):
        self.master = master
        self.mainframe = tkinter.Frame(self.master, bg='white')
        self.mainframe.pack(fill=tkinter.BOTH, expand=True)
        self.master.title("Stock Check")

        self.build_grid()
        self.build_banner()
        self.build_instructions()
        self.build_input()

    def build_grid(self):
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1) #title
        self.mainframe.rowconfigure(1, weight=1) #instructions
        self.mainframe.rowconfigure(2, weight=0) #select report
        self.mainframe.rowconfigure(3, weight=0) #select destination
        self.mainframe.rowconfigure(4, weight=0) #run!

    def build_banner(self):
        banner = tkinter.Label(
            self.mainframe,
            bg='white',
            text='Stock Check',
            fg='blue',
            font=('helvetica', 24)
        )
        banner.grid(
        row=0, column=0, sticky='ew',
        padx=10, pady=10
        )

    def build_instructions(self):
        instructions = tkinter.Label(
            self.mainframe,
            bg='white',
            text='''
            Select input file
            Select out destination
            Run
            ''',
            fg='black',
            font=('helvetica', 12)
        )
        instructions.grid(
        row=1, column=0, sticky='ew',
        padx=10, pady=10
        )

    def build_input(self):
        input_frame = tkinter.Frame(self.mainframe)
        input_frame.grid(row=2, column=0)
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)

        self.input_textbox = tkinter.Entry(input_frame)
        self.input_button = tkinter.Button(
        input_frame,
        text="Input File")

        self.input_textbox.grid(row=0, column=0, sticky='ew')
        self.input_button.grid(row=0, column=1, sticky='ew')





if __name__ == '__main__':
    root = tkinter.Tk()
    StockCheck(root)
    root.mainloop()
