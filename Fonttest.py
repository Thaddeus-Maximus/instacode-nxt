from Tkinter import *

master = Tk()

preview=Label(master,text="Instacode Is Cool",bg='#22cc33')
preview.pack(side=TOP)

button=Button(master,command=lambda:preview.config(font=entrybox.get()))
button.pack(side=BOTTOM)

entrybox = Entry(master,width=30)
entrybox.pack(side=BOTTOM)


master.bind("<Return>",lambda x=None:preview.config(font=entrybox.get()))
master.configure(background='#22cc33')
master.mainloop()