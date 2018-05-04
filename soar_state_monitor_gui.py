import xmlrpclib
import time
import socket

import argparse
import Tkinter as tk
from tkFont import Font
from operator import itemgetter

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Single Shot MultiBox Detection')

    parser.add_argument('--host', default='localhost', type=str,
                        help='hostname for remote state queries')

    parser.add_argument('--port', default=30000, type=int,
                        help='socket port# for remote state queries')

    args = parser.parse_args()

LIGHT_BLUE = '#b8d4d8'
DARKER_BLUE = '#1AA5C7'
ORANGE = '#fda429'

script = [
    ('',                         'False', 'Open front door       '),
    ('front_door_open',          'True',  'Unlock cartridge'),
    ('toner_cartridge_unlocked', 'True',  'Remove cartridge'),
    ('drum_cartridge_out',       'True',  'Insert new cartridge'),
    ('drum_cartridge_out',       'False', 'Lock cartridge'),
    ('toner_cartridge_unlocked', 'False', 'Close front door'),
    ('front_door_open',          'False', 'Replacement complete'),
]
class Application(tk.Frame, object):


    def __init__(self, master=None):

        super(Application, self).__init__(master)

        self.create_connection()

        self.create_widgets()

        self.after(300,self.update)



    def restart(self):

        pass


    def update(self):

        print("Updating")

        server_vars = self.server.get_all()

        index = 0
        state_var_list = sorted(server_vars, key=itemgetter('name'))
        for vars in state_var_list:
            for k,v in vars.items():
                widget = self.var_to_widget_index[index][k]
                string_var = self.var_to_StringVar_index[index][k]
                string_var.set("{}".format(v))
                if(v=='false'):
                    widget.config(bg='red')
                if(v=='true'):
                    widget.config(bg='green')
                if(v.replace(".",'').isdigit()):
                    widget.config(bg='green')
            index = index + 1
        self.after(300,self.update)


    def create_connection(self):


        print("ARA Tracker state client")

        self.url = 'http://{}:{}'.format(args.host,args.port)

        print("Attempting connection {}".format(self.url))

        self.server = xmlrpclib.ServerProxy(self.url)

        print("Connection created")



    def create_widgets(self):

        print("Create widgets")

        self.var_to_widget_index = list()
        self.var_to_StringVar_index = list()

        self.configure(background='white')
        self.option_add("*Label*font", "Helvetica 15 bold")

        myFont = Font(family="Helvetica", size=20)
        boldFont = Font(family="Helvetica",size=20,weight="bold")
        bigFont = Font(family="Helvetica",size=40,weight="bold")
        smallFont = Font(family="Helvetica",size=18)

        height = 5
        width = 2
        self.grid()

        print("Calling server")
        server_vars = self.server.get_all()
        self.state_vars = server_vars


        print("Initializing interface grid")
        i=0


        b=tk.Label(self, text='Printer State',fg='black',bg='white',font=boldFont)
        b.grid(row=i,column=0,padx=5,pady=5,sticky='W' )
        i=i+1

        state_var_list =sorted(self.state_vars, key=itemgetter('name'))

        for state_var in state_var_list:
            var_to_widget = dict()
            var_to_StringVar = dict()
            b = tk.Label(self, text="name", fg='black', bg='white', font=myFont)
            b.grid(row=i, column=0, padx=1, pady=5, sticky='W')
            b.bd=1

            sv = tk.StringVar()
            b = tk.Label(self, textvariable = sv, fg = 'white', bg = LIGHT_BLUE, font = myFont)
            b.grid(row = i, column = 1, padx=5,pady=5,sticky='W')
            b.bd=1
            var_to_widget['name'] = b
            sv.set("{}".format(state_var['name']))
            var_to_StringVar['name'] = sv

            b = tk.Label(self, text="id", fg='black', bg='white', font=myFont)
            b.grid(row=i, column=3, padx=1, pady=5, sticky='W')
            b.bd = 1

            sv = tk.StringVar()


            b = tk.Label(self, textvariable=sv, fg='white', bg=LIGHT_BLUE, font=myFont)
            b.grid(row=i, column=4, padx=5, pady=5, sticky='W')
            b.bd = 1
            var_to_widget['id'] = b
            sv.set("{}".format(state_var['id']))
            var_to_StringVar['id'] = sv

            column_no = 5
            for k,v in state_var.items():
                if (k != "name") and (k != "id"):
                    b = tk.Label(self, text=k, fg='black', bg='white', font=myFont)
                    b.grid(row=i, column=column_no, padx=1, pady=5, sticky='W')
                    b.bd = 1

                    sv = tk.StringVar()
                    b = tk.Label(self, textvariable=sv, fg='white', bg=LIGHT_BLUE, font=myFont)
                    b.grid(row=i, column=column_no+1, padx=5, pady=5, sticky='W')
                    b.bd = 1
                    var_to_widget[k] = b
                    sv.set("{}".format(v))
                    var_to_StringVar[k] = sv

                    column_no = column_no + 2
            i = i + 1
            self.var_to_widget_index.append(var_to_widget)
            self.var_to_StringVar_index.append(var_to_StringVar)


        self.pack(padx=20, pady=20)

print("Done creating widgets")

def create_widgets_orig(self):

        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=root.destroy)
        self.quit.pack(side="bottom")


def say_hi(self):

        print("hi there, everyone!")


root = tk.Tk()
root.title('Xerox PARC Visual Repair Assistant')
root.configure(background='white')
root.option_add("*Label*font", "Helvetica 15 bold")

app = Application(master=root)
app.mainloop()
