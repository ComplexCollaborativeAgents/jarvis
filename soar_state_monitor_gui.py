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

        #server_predicates = self.server.get_all_predicates()
        #print("Predicates: {}".format(server_predicates))

        server_vars = self.server.get_all()
        print(server_vars)

        index = 0
        state_var_list = sorted(server_vars, key=itemgetter('name'))
        if len(self.var_to_StringVar_index) > 0 and len(self.var_to_widget_index) > 0:
            for vars in state_var_list:
                for k,v in vars.items():
                    # if(k == 'name'):
                    #     print(v)
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



        height = 5
        width = 2
        self.grid()

        print("Calling server")
        print("Getting first vals of the server")
        server_vars = self.server.get_all()
        print(server_vars)

        self.state_vars = server_vars


        print("Initializing interface grid")
        i=0



        b=tk.Label(self, text='Printer State', fg='black', bg='white', font=BOLDFONT)
        b.grid(row=i,column=0,padx=5,pady=5,sticky='W' )
        i=i+1

        state_var_list =sorted(self.state_vars, key=itemgetter('name'))

        for state_var in state_var_list:
            var_to_widget = dict()
            var_to_StringVar = dict()
            b = tk.Label(self, text="name", fg='black', bg='white', font=MYFONT)
            b.grid(row=i, column=0, padx=1, pady=5, sticky='W')
            b.bd=1

            sv = tk.StringVar()
            b = tk.Label(self, textvariable = sv, fg = 'white', bg = LIGHT_BLUE, font = MYFONT)
            b.grid(row = i, column = 1, padx=5,pady=5,sticky='W')
            b.bd=1
            var_to_widget['name'] = b
            sv.set("{}".format(state_var['name']))
            var_to_StringVar['name'] = sv

            b = tk.Label(self, text="id", fg='black', bg='white', font=MYFONT)
            b.grid(row=i, column=3, padx=1, pady=5, sticky='W')
            b.bd = 1

            sv = tk.StringVar()


            b = tk.Label(self, textvariable=sv, fg='white', bg=LIGHT_BLUE, font=MYFONT)
            b.grid(row=i, column=4, padx=5, pady=5, sticky='W')
            b.bd = 1
            var_to_widget['id'] = b
            sv.set("{}".format(state_var['id']))
            var_to_StringVar['id'] = sv

            column_no = 5
            for k,v in state_var.items():
                if (k != "name") and (k != "id"):
                    b = tk.Label(self, text=k, fg='black', bg='white', font=MYFONT)
                    b.grid(row=i, column=column_no, padx=1, pady=5, sticky='W')
                    b.bd = 1

                    sv = tk.StringVar()
                    b = tk.Label(self, textvariable=sv, fg='white', bg=LIGHT_BLUE, font=MYFONT)
                    b.grid(row=i, column=column_no+1, padx=5, pady=5, sticky='W')
                    b.bd = 1
                    var_to_widget[k] = b
                    sv.set("{}".format(v))
                    var_to_StringVar[k] = sv

                    column_no = column_no + 2
            i = i + 1
            self.var_to_widget_index.append(var_to_widget)
            self.var_to_StringVar_index.append(var_to_StringVar)

        self.create_instruction_widgets(i+1)

        self.pack(padx=20, pady=20)

    def create_instruction_widgets(self, row_num):
        self.instruction_string_var = tk.StringVar()
        label = tk.Label(self, text = 'Instructions', fg='black', bg = 'white', font=BOLDFONT)
        label.grid(row = row_num, column = 0, padx=5, pady=5, sticky='W')

        button = tk.Button(self, text="Get Next", fg='black', bg='white',
                           command = self.get_next_instruction_from_soar_runner, font = SMALLFONT)
        button.grid(row=row_num + 1, column=0, padx=5, pady=5, stick='W')

        instruction_label = tk.Label(self, textvariable=self.instruction_string_var, fg='black', bg = 'white')
        instruction_label.grid(row = row_num + 1, column = 1, padx=5, pady=5, stick='W')


    def get_next_instruction_from_soar_runner(self):
        next_instruction = self.server.get_next_instruction()
        self.instruction_string_var.set("{} {}".format(next_instruction['action'], next_instruction['component']))
        print("Received instruction: {}".format(next_instruction))



print("Done creating widgets")


root = tk.Tk()
root.title('Xerox PARC Visual Repair Assistant')
root.configure(background='white')
root.option_add("*Label*font", "Helvetica 15 bold")

### FONT SPECS
MYFONT = Font(family="Helvetica", size=20)
BOLDFONT = Font(family="Helvetica", size=20, weight="bold")
BIGFONT = Font(family="Helvetica", size=40, weight="bold")
SMALLFONT = Font(family="Helvetica", size=18)


app = Application(master=root)
app.mainloop()
