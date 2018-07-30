# This tool is designed to utilize Arista eAPI in order to make json requests
# and parse responses
# Main functionality includes listing active port mirroring sessions, stopping
# them and creating new

# Additional functionality is automated switching of the range of source ports

# User with privelege level 2 or higher is required.
# Auto-enable on login for this user is REQUIRED!
# https://eos.arista.com/forum/how-do-i-enable-configure-commands-via-http-api/

# pyinstaller can be used to bake a handy executable file
# first install it using pip, then:
# pyinstaller -w -F [pythonfile.py]

# importing dependencies
import tkinter as tk   # GUI module
import pyeapi   # Arista eAPI module
import tkinter.messagebox   # Pop up windows module


#**************************FUNCTIONAL PART*************************************




class connect_to_switch(object):
    # Creates a connected switch object

    def get_login_credentials(self):
        # user input gathered from forms and passed to switch object
        self.ip_addr = main_app.ip_addr_entry.get()
        self.username = main_app.username_entry.get()
        self.password = main_app.password_entry.get()

    def initiate_connection(self):
        # connection initiated as switch object parameter
        self.connected_switch = pyeapi.connect(
            transport='https', host=self.ip_addr, username=self.username, password=self.password, port=None)

       

        # As there is no usable way to parse connection errors on initiation state,
        # connection status is checked by executing simple "show hostname" command.
        # If successfull - label "connected" method is executed and label is displayed
        try:
            switch.switch_hostname = switch.connected_switch.execute(
                ['show hostname'])
            main_app.connected()
            main_app.display_label()

        # if not succsessfull - label "not_connected" method is executed and label is displayed
        except:
            main_app.not_connected()
            main_app.display_label()


# "empty" switch object is created at the beggining
switch = connect_to_switch()


def switch_login():
    # Proxy function for GUI login button
    switch.get_login_credentials()
    switch.initiate_connection()
    monitor_sessions_list()


class monitor_sessions(object):
    # Monitoring sessions list refresh class

    def refresh_list(self):
        # Requests monitor session list from switch, parses the reply and puts all used ports to the lists
        self.used_source_ports = []
        self.used_destination_ports = []
        main_app.output_text.delete('1.0', tk.END)
        main_app.output_text.insert(tk.END, 'Current port mirroring configuration:')

        self.active_sessions = switch.connected_switch.execute(
            ['show monitor session'])
        for session_name in self.active_sessions['result'][0]['sessions']:
            main_app.output_text.insert(
                tk.END, '\n\n Mirroring session name: {}'.format(session_name))
            try:
                for input_only_ports in self.active_sessions['result'][0]['sessions'][session_name]['sourceRxInterfaces']:
                    main_app.output_text.insert(
                        tk.END, '\n RX interfaces: {}'.format(input_only_ports))
                    self.used_source_ports.append(input_only_ports)
            except IndexError:
                pass

            try:
                for output_only_ports in self.active_sessions['result'][0]['sessions'][session_name]['sourceTxInterfaces']:
                    main_app.output_text.insert(
                        tk.END, '\n TX interfaces: {}'.format(output_only_ports))
                    self.used_source_ports.append(output_only_ports)
            except IndexError:
                pass

            try:
                for both_ways_ports in self.active_sessions['result'][0]['sessions'][session_name]['sourceBothInterfaces']:
                    main_app.output_text.insert(
                        tk.END, '\n Duplex interfaces: {}'.format(both_ways_ports))
                    self.used_source_ports.append(both_ways_ports)
            except IndexError:
                pass

            try:
                for destination_port in self.active_sessions['result'][0]['sessions'][session_name]['targetInterfaces']:
                    main_app.output_text.insert(
                        tk.END, '\n Mirrored to: {}'.format(destination_port['name']))
                    self.used_destination_ports.append(
                        destination_port['name'])
            except:
                pass


# "empty" monitor sessions object is created at the beggining
current_sessions = monitor_sessions()



class new_monitor_session(object):
    # Class creates new monitor session on the switch
    def __init__(self):
        # Gets session details from user input fields
        self.new_session_name = main_app.user_session_name.get()
        self.source_port_number = main_app.user_source_port.get()
        self.destination_port_number = main_app.user_destination_port.get()

    def tx_session_source(self):
        # Assigns a TX only source port to the session
        # The checks are made is the source port is already in use and if the input field is empty
        if 'Ethernet' + self.source_port_number in current_sessions.used_source_ports or 'Ethernet' + self.source_port_number in current_sessions.used_destination_ports:
            tkinter.messagebox.showwarning(
                'Warning', 'Source port already in use! \n Only destination port assigned!')

        elif self.source_port_number != '':
            try:
                switch.connected_switch.execute(
                    ['configure terminal', 'monitor session {} source ethernet {} tx'.format(self.new_session_name, self.source_port_number)])

            except:
                tkinter.messagebox.showerror(
                    'Error', 'Bad source port! \n Check your input!')

    def rx_session_source(self):
        # Assigns a RX only source port to the session
        # The checks are made is the source port is already in use and if the input field is empty
        if 'Ethernet' + self.source_port_number in current_sessions.used_source_ports or 'Ethernet' + self.source_port_number in current_sessions.used_destination_ports:
            tkinter.messagebox.showwarning(
                'Warning', 'Source port already in use! \n Only destination port assigned!')

        elif self.source_port_number != '':
            try:
                switch.connected_switch.execute(
                    ['configure terminal', 'monitor session {} source ethernet {} rx'.format(self.new_session_name, self.source_port_number)])

            except:
                # If not done - error is pooped up
                tkinter.messagebox.showerror(
                    'Error', 'Bad source port! \n Check your input!')

    def duplex_session_source(self):
        # Assigns a duplex source port to the session
        # The checks are made is the source port is already in use and if the input field is empty
        if 'Ethernet' + self.source_port_number in current_sessions.used_source_ports or 'Ethernet' + self.source_port_number in current_sessions.used_destination_ports:
            tkinter.messagebox.showwarning(
                'Warning', 'Source port already in use! \n Only destination port assigned!')

        elif self.source_port_number != '':
            try:
                switch.connected_switch.execute(
                    ['configure terminal', 'monitor session {} source ethernet {} both'.format(self.new_session_name, self.source_port_number)])

            except:
                # If not done - error is pooped up
                tkinter.messagebox.showerror(
                    'Error', 'Bad source port! \n Check your input!')

    def destination(self):
        # Assigns a destination port to the session
        # The checks are made if the port is in use or input field is empty
        if 'Ethernet' + self.destination_port_number in current_sessions.used_source_ports or 'Ethernet' + self.destination_port_number in current_sessions.used_destination_ports:
            tkinter.messagebox.showwarning(
                'Warning', 'Destination port already in use!')
        elif self.destination_port_number != '':
            try:
                switch.connected_switch.execute(['configure terminal', 'monitor session {} destination ethernet {} '.format(
                    self.new_session_name, self.destination_port_number)])

            except:
                # If not done - error is pooped up
                tkinter.messagebox.showerror(
                    'Error', 'Something went wrong! \n Check your input!')


class new_automated_session(object):

    def initiate(self):
        # Class creates a list of source ports to go through from user input fields
        self.index = 0
        self.new_session_name = main_app.user_session_name_automate.get()
        self.first_source_port_number = int(main_app.start_user_source_port.get())
        self.last_source_port_number = int(main_app.end_user_source_port.get())
        self.destination_port_number = main_app.user_destination_port_automate.get()
        self.port_range = []
        for port in range(self.first_source_port_number, self.last_source_port_number + 1):
            self.port_range.append(port)

        self.current_port = self.port_range[self.index]

    def next_port(self):
        # goes through the ports list, kills currents session, initiates session creation for next port
        if self.index < int(self.last_source_port_number) + 1:
            self.index += 1
            try:
                self.current_port = self.port_range[self.index]
                self.kill_monitor_session()
                self.duplex_session_source()

            except IndexError:
                # WHen list is over - pop up is displayed
                tkinter.messagebox.showinfo('Executed', 'Range finished!')

    def duplex_session_source(self):
        # Checks if the ports are in use and creates the session for current port
        if 'Ethernet{}'.format(self.current_port) in current_sessions.used_source_ports or 'Ethernet{}'.format(self.current_port) in current_sessions.used_destination_ports:
            tkinter.messagebox.showwarning(
                'Warning', 'Source port already in use! \n Skipping!')

        elif self.current_port != '':
            try:
                switch.connected_switch.execute(
                    ['configure terminal', 'monitor session {} source ethernet {} both'.format(self.new_session_name, self.current_port)])

            except:
                tkinter.messagebox.showerror(
                    'Error', 'Bad source port! \n Check your input!')

    def destination(self):

        switch.connected_switch.execute(['configure terminal', 'monitor session {} destination ethernet {} '.format(
            self.new_session_name, self.destination_port_number)])

    def kill_monitor_session(self):
        # Stops session for current ports
        try:
            switch.connected_switch.execute(
                ['configure terminal', 'no monitor session {}'.format(self.new_session_name)])

        except:
            # If the command was unsuccesfull error pop up is displayed
            tkinter.messagebox.showerror(
                'Error', 'No active sessions with this name! \n Check your input!')


def monitor_sessions_list():
    # Proxy function for the GUI button "refresh session list"
    if main_app.switch_is_connected == True:
        current_sessions.refresh_list()
    else:
        tkinter.messagebox.showerror('Error', 'Connect to the switch first!')


def tx_session_creation():
    # Proxy function for TX only new session GUI button
    if main_app.switch_is_connected == True:
        new_session = new_monitor_session()
        new_session.tx_session_source()
        new_session.destination()
        monitor_sessions_list()
    else:
        tkinter.messagebox.showerror('Error', 'Connect to the switch first!')


def rx_session_creation():
    # Proxy function for TX only new session GUI button
    if main_app.switch_is_connected == True:
        new_session = new_monitor_session()
        new_session.rx_session_source()
        new_session.destination()
        monitor_sessions_list()
    else:
        tkinter.messagebox.showerror('Error', 'Connect to the switch first!')


def duplex_session_creation():
    # Proxy function for TX only new session GUI button
    if main_app.switch_is_connected == True:
        new_session = new_monitor_session()
        new_session.duplex_session_source()
        new_session.destination()
        monitor_sessions_list()
    else:
        tkinter.messagebox.showerror('Error', 'Connect to the switch first!')


def kill_monitor_session():
    # Function to stop any active session
    # Session name is received from the text field
    if main_app.switch_is_connected == True:

        session_to_kill = main_app.remove_session_name.get()
        try:
            switch.connected_switch.execute(
                ['configure terminal', 'no monitor session {}'.format(session_to_kill)])

        except:
            # If the command was unsuccesfull error pop up is displayed
            tkinter.messagebox.showerror(
                'Error', 'No active sessions with this name! \n Check your input!')
        finally:
            # Sessions list is updated

            monitor_sessions_list()
    else:
        tkinter.messagebox.showerror('Error', 'Connect to the switch first!')


automated_session = new_automated_session()


def start_duplex_automation():
    # Proxy function for automated session GUI button
    if main_app.switch_is_connected == True:
        automated_session.initiate()
        automated_session.duplex_session_source()
        automated_session.destination()
        monitor_sessions_list()
    else:
        tkinter.messagebox.showerror('Error', 'Connect to the switch first!')


def next_automated():
    # Proxy function for next port GUI button
    if main_app.switch_is_connected == True:
        automated_session.next_port()
        automated_session.destination()
        monitor_sessions_list()
    else:
        tkinter.messagebox.showerror('Error', 'Connect to the switch first!')

#****************************GUI PART****************************************

class MainApplication(tk.Frame):
    
    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.login_section()
        self.new_section_section()
        self.remove_session_section()
        self.session_list_section()
        self.automated_switching()
        self.label_is_visible = False
        self.switch_is_connected = False

    def configure_gui(self):
        self.master.title('Arista port mirroring tool')
        self.master.resizable(False, False)
    def login_section(self):
        # Section title
        self.login_first_label = tk.Label(self.master, text='Login First', font='Arial 12 bold')
        self.login_first_label.grid(row=1, columnspan=3)

        # IP address label and input text field
        self.ip_addr_label = tk.Label(self.master, text='Device IP address', font='Arial 10')
        self.ip_addr_label.grid(row=3, column=0, sticky=tk.E)

        self.ip_addr_entry = tk.Entry(self.master, font='Arial 10')
        self.ip_addr_entry.grid(row=3, column=1)

        # Username label and input text field
        self.username_label = tk.Label(self.master, text='Username', font='Arial 10')
        self.username_label.grid(row=4, column=0, sticky=tk.E)

        self.username_entry = tk.Entry(self.master, font='Arial 10')
        self.username_entry.grid(row=4, column=1)

        # Password label and input text field, password is hidden when entering
        self.password_label = tk.Label(self.master, text='Password', font='Arial 10')
        self.password_label.grid(row=5, column=0, sticky=tk.E)

        self.password_entry = tk.Entry(self.master, show='*', font='Arial 10')
        self.password_entry.grid(row=5, column=1)

        # Login button. Calls for switch login function
        self.login_button = tk.Button(self.master, text='Login', width=30,
                              command=switch_login, font='Arial 10')
        self.login_button.grid(row=6, columnspan=3)

        # Dummy field. Replaced by login status when connection is active
        self.status_label = tk.Label(self.master, text='Connection Status', font='Arial 10')
        self.status_label.grid(row=7, columnspan=3)


    def connected(self):
        # Basic switch info is displayed when connected
        self.status_bar = tk.Label(self.master, bg='green', font='Arial 10', text='Connected to: {} at {}'.format(switch.switch_hostname['result'][0]['hostname'], switch.ip_addr), bd=1, relief=tk.SUNKEN, anchor=tk.CENTER)
        self.switch_is_connected = True
        

    def not_connected(self):
        # if not connected - error displayed
        self.status_bar = tk.Label(self.master, bg='red', font='Arial 10', text='Connection error, check parameters!', bd=1, relief=tk.SUNKEN, anchor=tk.CENTER)
        self.switch_is_connected = False
        

    def display_label(self):
        # checks if the label is visible, destroys label when info is refreshed
        try:
            self.status_bar.tk.destroy()
        except:
            pass
        finally:
            self.status_bar.grid(row=7, columnspan=5, sticky=tk.N+tk.S+tk.E+tk.W)
         

    def new_section_section(self):
        # Section title
        self.new_session_label = tk.Label(self.master, text='Create or modify session', font='Arial 12 bold')
        self.new_session_label.grid(row=10, columnspan=3)

        # Session name label and text field
        self.session_name_label = tk.Label(self.master, text='Session name', font='Arial 10')
        self.session_name_label.grid(row=11, column=0, sticky=tk.E)

        self.user_session_name = tk.Entry(self.master, font='Arial 10')
        self.user_session_name.grid(row=11, column=1)

        # Source port label and text field
        self.source_port_label = tk.Label(self.master, text='Source port', font='Arial 10')
        self.source_port_label.grid(row=12, column=0, sticky=tk.E)

        self.user_source_port = tk.Entry(self.master, font='Arial 10')
        self.user_source_port.grid(row=12, column=1)

        # Destination port label and text field
        self.destination_port_label = tk.Label(self.master, text='Destination port', font='Arial 10')
        self.destination_port_label.grid(row=13, column=0, sticky=tk.E)


        self.user_destination_port = tk.Entry(self.master, font='Arial 10')
        self.user_destination_port.grid(row=13, column=1)

        # TX only button. Calls for TX only new session function
        self.tx_only_button = tk.Button(self.master, text='Source port: TX only', width=30, command=tx_session_creation, font='Arial 10')
        self.tx_only_button.grid(row=14, columnspan=3)

        # RX only button. Calls for RX only new session function
        self.rx_only_button = tk.Button(self.master, text='Source port: RX only', width=30, command=rx_session_creation, font='Arial 10')
        self.rx_only_button.grid(row=15, columnspan=3)

        # Duplex button. Calls for duplex new session function
        self.duplex_button = tk.Button(self.master, text='Source port: Duplex', width=30, command=duplex_session_creation, font='Arial 10')
        self.duplex_button.grid(row=16, columnspan=3)

    def remove_session_section(self):

        # Section title
        self.remove_session_label = tk.Label(self.master, text='Remove session', font='Arial 12 bold')
        self.remove_session_label.grid(row=17, columnspan=3)

        # Session to remove name text field and title
        self.session_remove_name_label = tk.Label(self.master, text='Session name', font='Arial 10')
        self.session_remove_name_label.grid(row=19, column=0, sticky=tk.E)

        self.remove_session_name = tk.Entry(self.master, font='Arial 10')
        self.remove_session_name.grid(row=19, column=1)

        # Session remove button, calls session remove function
        self.remove_session_button = tk.Button(self.master, text='Remove session', width=30, command=kill_monitor_session, font='Arial 10')
        self.remove_session_button.grid(row=20, columnspan=3)

    def session_list_section(self):
        
        # Section title
        self.list_label = tk.Label(self.master, text='Active sessions', font='Arial 12 bold')
        self.list_label.grid(row=21, columnspan=3)

        # Session refresh button. Calls session list refresh function
        self.sessions_list_button = tk.Button(self.master, text='Refresh sessions list', width=30, command=monitor_sessions_list, font='Arial 10')
        self.sessions_list_button.grid(row=22, columnspan=3)

        # Main text output filed
        self.output_scroll = tk.Scrollbar(self.master)
        self.output_text = tk.Text(self.master, height=37, width=48)
        self.output_scroll.grid(row=1, rowspan=35, column=6)
        self.output_text.grid(row=1, rowspan=35, column=5)
        self.output_scroll.config(command=self.output_text.yview)
        self.output_text.config(yscrollcommand=self.output_scroll.set)

        self.output_text.insert(tk.END, """
README FIRST:

This tool is designed to utilize Arista eAPI

Normally a dedicated username with privelege
level 15 is recommended
Auto-enable on login for this user is REQUIRED!

How to do it? See:
https://eos.arista.com/forum/how-do-i-enable-configure-commands-via-http-api/

            
Copyright 2018 Ievgen Kostiukevych

Licensed under the Apache License, Version 2.0
(the "License");
you may not use this file except in compliance
with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to
in writing, software distributed under the
License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied.
See the License for the specific language
governing permissions and limitations
under the License.
""")    

    def automated_switching(self):

        # Section title
        self.list_label = tk.Label(self.master, text='Automated switching (Duplex only)', font='Arial 12 bold')
        self.list_label.grid(row=23, columnspan=3)

        # Session name label and text field
        self.session_name_label_automate = tk.Label(self.master, text='Session name', font='Arial 10')
        self.session_name_label_automate.grid(row=24, column=0, sticky=tk.E)

        self.user_session_name_automate = tk.Entry(self.master, font='Arial 10')
        self.user_session_name_automate.grid(row=24, column=1)

        # Start source port label and text field
        self.start_source_port_label = tk.Label(self.master, text='First source port', font='Arial 10')
        self.start_source_port_label.grid(row=25, column=0, sticky=tk.E)

        self.start_user_source_port = tk.Entry(self.master, font='Arial 10')
        self.start_user_source_port.grid(row=25, column=1)


        # End source port label and text field

        self.end_source_port_label = tk.Label(self.master, text='Last source port', font='Arial 10')
        self.end_source_port_label.grid(row=26, column=0, sticky=tk.E)

        self.end_user_source_port = tk.Entry(self.master, font='Arial 10')
        self.end_user_source_port.grid(row=26, column=1)


        # Destination port label and text field

        self.destination_port_label_automate = tk.Label(self.master, text='Destination port', font='Arial 10')
        self.destination_port_label_automate.grid(row=27, column=0, sticky=tk.E)

        self.user_destination_port_automate = tk.Entry(self.master, font='Arial 10')
        self.user_destination_port_automate.grid(row=27, column=1)


        # Start automation button, initiates port-by-port monitoring sessions
        self.duplex_only_button = tk.Button(self.master, text='Start', width=30, command=start_duplex_automation, font='Arial 10')
        self.duplex_only_button.grid(row=29, columnspan=3)


        # Next port button
        self.next_button = tk.Button(self.master, text='Next port', width=30, command=next_automated, font='Arial 10')
        self.next_button.grid(row=31, padx=1, columnspan=3)


if __name__ == '__main__':
    root = tk.Tk()
    main_app =  MainApplication(root)
    root.mainloop()