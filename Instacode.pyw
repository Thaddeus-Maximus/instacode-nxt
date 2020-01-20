import subprocess
import pickle
try:
  from Tkinter import *
except:
  from tkinter import *

commands_config = { 'start':('Click Colored Commands on Left\nto Make Your Program!','#22cc33'),
                    'beep':('Beep','#ff69b4'),
                    'none':('Blank','#aaaaaa'),
                    'arm':('Move Arm','#dd7700'),
                    'wait':('Wait','#11bbbb'),
                    #'forward':('Forward','#00dd00'),
                    #'backward':('Backward','#dd0000'),
                    #'left':('Left','#dddd00'),
                    #'right':('Right','#3311ee'),

                    'turn':('Turn','#3311ee'),
                    'drive':('Drive','#00dd00'),
                    'track':('Track Line','#dd0000')
                    }
order_of_commands = ['drive','track','turn','arm','beep','wait','none']
custom_font = 'Consolas 14 bold'
scripting_font = 'Consolas 12 bold'
bgcolor = '#141414'

global commands
window = Tk()
nxt_path = StringVar()

def compile(commands, run=True):
  with open('Instabotics_Lab.nxc','w') as f:
    f.write('#include "Instacode.h"\n\ntask main(){start armRegulator;\n\n/* Begin User Generated Code! */\n\n')

    #f.write('StraightInches(5,70,0.2);')
    #f.write('TurnDegrees(90);')
    for c in commands:
      command = c.get_details()
      if command[0] == 'arm':
        if command[1] == 'up':
          f.write('MoveArmBy('+str(command[2])+', '+str(command[3])+');\n')
        else:
          f.write('MoveArmBy('+str(-float(command[2]))+', '+str(command[3])+');\n')

      elif command[0] == 'wait':
        f.write('Delay(' + str(command[1]) + ');\n')

      elif command[0] == 'beep':
        f.write('Beep(' + str(command[1]) +', '+str(command[2]) + ');\n')

      elif command[0] == 'drive':
        if command[1] == 'forward':
          if command[3] == 'inches':
            f.write('StraightInches('+str(command[2])+', '+str(command[4])+');\n')
          else:
            f.write('StraightSeconds('+str(command[2])+', '+str(command[4])+');\n')
        else:
          if command[3] == 'inches':
            f.write('StraightInches('+str(-float(command[2]))+', '+str(command[4])+');\n')
          else:
            f.write('StraightSeconds('+str(command[2])+', '+str(-float(command[4]))+');\n')

      elif command[0] == 'turn':
        if command[1] == 'right':
          f.write('TurnDegrees('+str(command[2])+', '+str(command[3])+');\n')
        else:
          f.write('TurnDegrees('+str(-float(command[2]))+', '+str(command[3])+');\n')
    # f.write the rest of the code here
    f.write('\n/* End User Generated Code. */\n\nOff(OUT_ABC);Delay(1);Stop(true);}');

  with open('nbc_output.log','w') as out:
    if run:
      subprocess.call('nbc -S='+nxt_path.get()+' -r Instabotics_Lab.nxc', stdout=out) # -d downloads, -r runs.
      out.write('Command Used: '+'nbc -S='+nxt_path.get()+' -r Instabotics_Lab.nxc'+'\n')
    else:
      subprocess.call('nbc -S='+nxt_path.get()+' -d Instabotics_Lab.nxc', stdout=out)
      out.write('Command Used: '+'nbc -S='+nxt_path.get()+' -d Instabotics_Lab.nxc'+'\n')


def move_command_up(index):
  global commands
  if index > 0:
    commands[index], commands[index-1] = commands[index-1], commands[index]
    commands[index].index = index
    commands[index-1].index = index-1
    commands[index-1].grid(index-1)
    commands[index].grid(index)

def move_command_down(index):
  global commands
  if index < len(commands)-1:
    commands[index], commands[index+1] = commands[index+1], commands[index]
    commands[index].index = index
    commands[index+1].index = index+1
    commands[index+1].grid(index+1)
    commands[index].grid(index)

def remove_command(index):
  commands[index].pack_forget()
  commands.pop(index)
  for i in range(len(commands)):
    commands[i].index=i
  if len(commands) <= 0:
    add_command('start')

class Command:
  def __init__(self,name,index,params=()):
    self.index = index
    self.name = name
    self.frame = Frame(scripting_frame, bg=commands_config[self.name][1])
    self.frame.grid(row=self.index, ipady=2, sticky=W+E)
    self.widgets = []
    self.widgets.append(Label(self.frame, font=scripting_font, bg=commands_config[self.name][1], text=commands_config[self.name][0]))
    self.widgets[-1].pack(side=LEFT, ipadx=2)
    def add_padding():
      self.widgets.append(Frame(self.frame, height=20, bd=1, relief=FLAT, bg=commands_config[self.name][1]))
      self.widgets[-1].pack(side=LEFT, padx=5, pady=5)
    add_padding()

    
    if self.name == 'arm':
      def turn_direction_callback():
        if self.widgets[2]["text"] == 'up':
          self.widgets[2]['text'] = 'down'
        else:
          self.widgets[2]['text'] = 'up'

      self.widgets.append(Button(self.frame, font=scripting_font, bg=commands_config[self.name][1], text='up', command=turn_direction_callback))
      self.widgets[-1].pack(side=LEFT, ipadx=2)

      add_padding()

      self.widgets.append(Spinbox(self.frame, font=scripting_font, from_=0, to=200, increment=10, width=5))
      self.widgets[-1].delete(0,END)
      if params:
        self.widgets[-1].insert(0,str(params[1]))
      else:
        self.widgets[-1].insert(0,'90')
      self.widgets[-1].pack(side=LEFT, ipadx=2)
      self.widgets.append(Label(self.frame, font=scripting_font, bg=commands_config[self.name][1], text="Degrees"))
      self.widgets[-1].pack(side=LEFT, ipadx=2)

      add_padding()

      self.widgets.append(Spinbox(self.frame, font=scripting_font, from_=20, to=100, increment=10, width=5))
      self.widgets[-1].delete(0,END)
      if params:
        self.widgets[-1].insert(0,str(params[2]))
      else:
        self.widgets[-1].insert(0,'100')
      self.widgets[-1].pack(side=LEFT, ipadx=2)
      self.widgets.append(Label(self.frame, font=scripting_font, bg=commands_config[self.name][1], text="% Power"))
      self.widgets[-1].pack(side=LEFT, ipadx=2)

      if params:
        if params[0] != 'up':
          turn_direction_callback()

    if self.name == 'beep':
      self.widgets.append(Spinbox(self.frame, font=scripting_font, values=(100,200,400,600,800,1000,2000,3000,4000), width=5))
      self.widgets[-1].delete(0,END)
      if params:
        self.widgets[-1].insert(0,str(params[0]))
      else:
        self.widgets[-1].insert(0,'400')
      self.widgets[-1].pack(side=LEFT, ipadx=2)
      self.widgets.append(Label(self.frame, font=scripting_font, bg=commands_config[self.name][1], text="Hz"))
      self.widgets[-1].pack(side=LEFT, ipadx=2)

      add_padding()

      self.widgets.append(Spinbox(self.frame, font=scripting_font, from_=0, to=10, increment=0.5, width=5))
      self.widgets[-1].delete(0,END)
      if params:
        self.widgets[-1].insert(0,str(params[1]))
      else:
        self.widgets[-1].insert(0,'0.5')
      self.widgets[-1].pack(side=LEFT, ipadx=2)
      self.widgets.append(Label(self.frame, font=scripting_font, bg=commands_config[self.name][1], text="Seconds"))
      self.widgets[-1].pack(side=LEFT, ipadx=2)

    elif self.name == 'wait':
      self.widgets.append(Spinbox(self.frame, font=scripting_font, from_=0, to=10, increment=0.5, width=5))
      self.widgets[-1].delete(0,END)
      if params:
        self.widgets[-1].insert(0,str(params[0]))
      else:
        self.widgets[-1].insert(0,'1.0')
      self.widgets[-1].pack(side=LEFT, ipadx=2)
      self.widgets.append(Label(self.frame, font=scripting_font, bg=commands_config[self.name][1], text="Seconds"))
      self.widgets[-1].pack(side=LEFT, ipadx=2)

    elif self.name == 'turn':
      def turn_direction_callback():
        if self.widgets[2]["text"] == 'right':
          self.widgets[2]['text'] = 'left'
        else:
          self.widgets[2]['text'] = 'right'

      self.widgets.append(Button(self.frame, font=scripting_font, bg=commands_config[self.name][1], text='right', command=turn_direction_callback))
      self.widgets[-1].pack(side=LEFT, ipadx=2)

      add_padding()

      self.widgets.append(Spinbox(self.frame, font=scripting_font, from_=0, to=360, increment=10, width=5))
      self.widgets[-1].delete(0,END)
      if params:
        self.widgets[-1].insert(0,str(params[1]))
      else:
        self.widgets[-1].insert(0,'90')
      self.widgets[-1].pack(side=LEFT, ipadx=2)
      self.widgets.append(Label(self.frame, font=scripting_font, bg=commands_config[self.name][1], text="Degrees"))
      self.widgets[-1].pack(side=LEFT, ipadx=2)

      add_padding()

      self.widgets.append(Spinbox(self.frame, font=scripting_font, from_=30, to=100, increment=10, width=5))
      self.widgets[-1].delete(0,END)
      if params:
        self.widgets[-1].insert(0,str(params[2]))
      else:
        self.widgets[-1].insert(0,'50')
      self.widgets[-1].pack(side=LEFT, ipadx=2)
      self.widgets.append(Label(self.frame, font=scripting_font, bg=commands_config[self.name][1], text="% Power"))
      self.widgets[-1].pack(side=LEFT, ipadx=2)

      if params:
        if params[0] != 'right':
          turn_direction_callback()

    elif self.name == 'drive':
      def drive_direction_callback():
        if self.widgets[2]["text"] == 'forward':
          self.widgets[2]['text'] = 'reverse'
        else:
          self.widgets[2]['text'] = 'forward'

      self.widgets.append(Button(self.frame, font=scripting_font, bg=commands_config[self.name][1], text='forward', command=drive_direction_callback))
      self.widgets[-1].pack(side=LEFT, ipadx=2)

      add_padding()

      self.widgets.append(Spinbox(self.frame, font=scripting_font, from_=0, to=100, increment=1, width=5))
      self.widgets[-1].delete(0,END)
      if params:
        self.widgets[-1].insert(0,str(params[1]))
      else:
        self.widgets[-1].insert(0,'5')
      self.widgets[-1].pack(side=LEFT, ipadx=2)

      def units_callback():
        if self.widgets[5]["text"] == 'inches':
          self.widgets[5]['text'] = 'seconds'
          self.widgets[4].delete(0,END)
          self.widgets[4].insert(0,'2')
          self.widgets[4].config(to=10, increment=0.5)
        else:
          self.widgets[5]['text'] = 'inches'
          self.widgets[4].delete(0,END)
          self.widgets[4].insert(0,'5')
          self.widgets[4].config(to=100, increment=1)

      self.widgets.append(Button(self.frame, font=scripting_font, bg=commands_config[self.name][1], text='inches', command=units_callback))
      self.widgets[-1].pack(side=LEFT, ipadx=2)

      add_padding()

      self.widgets.append(Spinbox(self.frame, font=scripting_font, from_=30, to=100, increment=10, width=5))
      self.widgets[-1].delete(0,END)
      if params:
        self.widgets[-1].insert(0,str(params[3]))
      else:
        self.widgets[-1].insert(0,'70')
      self.widgets[-1].pack(side=LEFT, ipadx=2)
      self.widgets.append(Label(self.frame, font=scripting_font, bg=commands_config[self.name][1], text="% Power"))
      self.widgets[-1].pack(side=LEFT, ipadx=2)

      if params:
        if params[2] != 'inches':
          units_callback()
        if params[0] != 'forward':
          drive_direction_callback()

    elif self.name == 'start':
      return

    add_padding()

    self.widgets.append(Button(self.frame, font=scripting_font, text=u"\u25bc", command=lambda:move_command_down(self.index)))
    self.widgets[-1].pack(side=RIGHT, ipadx=2)
    self.widgets.append(Button(self.frame, font=scripting_font, text=u"\u25b2", command=lambda:move_command_up(self.index)))
    self.widgets[-1].pack(side=RIGHT, ipadx=2)
    self.widgets.append(Button(self.frame, font=scripting_font, text=u"\u26d4", command=lambda:remove_command(self.index)))
    self.widgets[-1].pack(side=RIGHT, ipadx=2)

  def get_details(self):
    if self.name == 'arm':
      return ('arm',self.widgets[2]['text'],self.widgets[4].get(),self.widgets[7].get())

    elif self.name == 'wait':
      return ('wait',self.widgets[2].get())

    elif self.name == 'beep':
      return ('beep',self.widgets[2].get(),self.widgets[5].get())

    elif self.name == 'drive':
      return ('drive',self.widgets[2]['text'],self.widgets[4].get(),self.widgets[5]['text'],self.widgets[7].get())

    elif self.name == 'turn':
      return ('turn',self.widgets[2]['text'],self.widgets[4].get(),self.widgets[7].get())

    return ('none','none')

  def grid(self, row):
    self.frame.grid(row=row, ipady=2, sticky=W+E)

  def pack_forget(self):
    self.name = 'none'
    for widget in self.widgets:
      widget.pack_forget()
    self.frame.grid_forget()

def add_command(name,params=None):
  if name != 'start':
    if len(commands) > 0:
      if commands[0].name == 'start':
        commands[0].pack_forget()
        commands.pop(0)
    commands.append(Command(name,len(commands),params))
  else:
    commands.append(Command('start',0,params))


commands = []

def clear():
  global commands
  for command in commands:
    command.pack_forget()
  commands = []
  add_command('start')

def save():
  f = open('savefile.pkl', 'wb')
  for command in commands:
    pickle.dump(command.get_details(), f)
  f.close()

def load():
  f = open('savefile.pkl', 'rb')
  clear()
  while 1:
    try:
      raw_command = pickle.load(f)
      add_command(raw_command[0],raw_command[1:])
    except:
      break 
  f.close()


scripting_frame = Frame(window)
scripting_frame.grid(row=0,column=2,sticky='nw')

action_frame = Frame(window, bg='#333333')
action_frame.grid(row=0,column=0,sticky='nw')

commands_frame = Frame(window, bg='#333333')
commands_frame.grid(row=0,column=1,sticky='nw')

use_bluetooth_button = Entry(action_frame, width=10, font=custom_font, textvariable=nxt_path)
nxt_path.set('usb')
use_bluetooth_button.pack(side=TOP, padx=5,pady=4)
download_button = Button(action_frame, font=custom_font, width=10, text="Download", command = lambda: compile(commands, False))
download_button.pack(side=TOP, padx=5, pady=4)
run_button = Button(action_frame, font=custom_font, width=10, text="Run", command = lambda: compile(commands))
run_button.pack(side=TOP, padx=5, pady=4)

separator = Frame(action_frame, height=5, bd=1, relief=FLAT, bg='#333333')
separator.pack(fill=X, padx=5, pady=5)

clear_button = Button(action_frame, font=custom_font, width=10, text="Clear", command = clear)
clear_button.pack(side=TOP, padx=5, pady=4)

separator2 = Frame(action_frame, height=5, bd=1, relief=FLAT, bg='#333333')
separator2.pack(fill=X, padx=5, pady=5)

save_button = Button(action_frame, font=custom_font, width=10, text="Save", command = save)
save_button.pack(side=TOP, padx=5, pady=4)
load_button = Button(action_frame, font=custom_font, width=10, text="Load", command = load)
load_button.pack(side=TOP, padx=5, pady=4)




command_buttons = []
for c in order_of_commands:
  command_buttons.append(Button(commands_frame, font=custom_font, width=10, bg=commands_config[c][1], text=commands_config[c][0], command = lambda c=c: add_command(c) ))
  command_buttons[-1].pack(side=TOP, pady=1, padx=5)

window.minsize(470, 350)
window.configure(background=bgcolor)
window.title('Instacode')

add_command('start')

window.mainloop()