from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import platform
import os
import telnetlib
from ftplib import FTP


class Main:
    def __init__(self):
        self.menu = Tk()
        self.menu.title("Practica 4")
        self.menu.resizable(False, False)
        self.frm = ttk.Frame(self.menu, padding=3)
        self.frm.grid()
        self.lbl0 = ttk.Label(self.frm, text="Modulo de Administración de Configuración")
        self.lbl0.grid(columnspan=2, row=0)
        self.eleccion =StringVar()
        self.opc1 = ttk.Radiobutton(self.frm, text="RCPlive-1", value="192.168.1.1", variable=self.eleccion, command=lambda: self.habilitar())
        self.opc1.grid(column=0, row=1)
        self.opc2 = ttk.Radiobutton(self.frm, text="RCPlive-3", value="192.168.0.9", variable=self.eleccion, command=lambda: self.habilitar())
        self.opc2.grid(column=1, row=1)
        self.btn1 = ttk.Button(self.frm, text="Ping", command=lambda: self.ping(), state=DISABLED)
        self.btn1.grid(columnspan=2, row=2)
        self.btn2 = ttk.Button(self.frm, text="Generar la Configuracion", command=lambda: self.generar(), state=DISABLED)
        self.btn2.grid(columnspan=2, row=3)
        self.btn3 = ttk.Button(self.frm, text="Extraer la Configuracion", command=lambda: self.extraer(), state=DISABLED)
        self.btn3.grid(columnspan=2, row=4)
        self.btn4 = ttk.Button(self.frm, text="Importar la Configuracion", command=lambda: self.importar(), state=DISABLED)
        self.btn4.grid(columnspan=2, row=5)
        self.menu.mainloop()

    def habilitar(self):
        self.btn1.state(["!disabled"])
        self.btn2.state(["!disabled"])
        self.btn3.state(["!disabled"])
        self.btn4.state(["!disabled"])

    def ping(self):
        pingw = Toplevel()
        pingw.title("Ping")
        pingw.resizable(False, False)
        label1 = ttk.Label(pingw, text="Comprobando el estado de la red " + self.eleccion.get(), relief=SUNKEN, padding=6)
        label1.grid(column=0, row=0)
        comando = ""
        if platform.system().lower() == "windows":
            comando = "ping -n 1 -w 3 " + self.eleccion.get()
        else:
            comando = "ping -c 1 -w 3 " + self.eleccion.get()
        labels = []
        r = 1

        for i in range(0, 5):
            labels.append(ttk.Label(pingw, text="\nRealizando el ping " + str(i+1) + "..."))
            labels[r-1].grid(column=0, row=r)
            self.menu.update()
            r += 1
            t = os.system(comando)
            if t:
                labels.append(ttk.Label(pingw, text="Ping Fallido.", foreground="red"))
            else:
                labels.append(ttk.Label(pingw, text="Ping Exitoso!", foreground="green"))
            labels[r - 1].grid(column=0, row=r)
            r += 1

    def generar(self):
        generarw = Toplevel()
        generarw.title("Generar la Configuracion")
        generarw.resizable(False, False)
        label1 = ttk.Label(generarw, text="Generando la configuracion de la red " + self.eleccion.get(), relief=SUNKEN, padding=6)
        label1.grid(column=0, row=0)
        self.menu.update()
        up = "rcp"
        tn = telnetlib.Telnet(self.eleccion.get())
        tt = ""
        tt += tn.read_until(b"User: ").decode('ascii')
        tn.write(up.encode('ascii') + b"\n")
        tt += tn.read_until(b"Password: ").decode('ascii')
        tn.write(up.encode('ascii') + b"\n")
        tn.write(b"enable\n")
        tn.write(b"show clock\n")
        tn.write(b"copy running-config startup-config\n")
        tn.write(b"exit\n")
        tt += tn.read_all().decode('ascii')
        tn.close()
        label2 = ttk.Label(generarw, text=tt)
        label2.grid(column=0, row=1)

    def extraer(self):
        extraerw = Toplevel()
        extraerw.title("Extraer la Configuracion")
        extraerw.resizable(False, False)
        label1 = ttk.Label(extraerw, text="Obtiendo el archivo startup-config de " + self.eleccion.get(), relief=SUNKEN, padding=6)
        label1.grid(columnspan=2, row=0)
        ftp = FTP(self.eleccion.get())
        ftp.login("rcp", "rcp")
        data = []
        ftp.dir(data.append)
        flag = False
        print(data)
        for d in data:
            if "startup-config" in d:
                flag = True
                break
        if flag:
            with open('startup-config', 'wb') as sc:
                ftp.retrbinary('RETR startup-config', sc.write)
            label2 = ttk.Label(extraerw, text="\nSe guardo con exito el archivo startup-config:\n", foreground="green")
            label2.grid(columnspan=2, row=1)
            st = ""
            with open('startup-config', 'r') as sc:
                st = sc.read()
            scrbar1 = ttk.Scrollbar(extraerw, orient=VERTICAL)
            scrbar1.grid(column=1, row=2, sticky="NS")
            text1 = Text(extraerw, yscrollcommand=scrbar1.set)
            text1.insert(INSERT, st)
            text1.config(state=DISABLED)
            scrbar1.config(command=text1.yview)
            text1.grid(column=0, row=2)

        else:
            label2 = ttk.Label(extraerw, text="\nNo se pudo extraer el archivo startup-config", foreground="red")
            label2.grid(columnspan=2, row=1)
        ftp.quit()

    def importar(self):
        def enviar():
            with open('startup-config', 'w') as sc:
                sc.write(text1.get("1.0", END))
            ftp = FTP(self.eleccion.get())
            ftp.login("rcp", "rcp")
            try:
                with open('startup-config', 'rb') as sc:
                    ftp.storbinary('STOR startup-config', sc)
                ftp.quit()
                importarw.destroy()
                messagebox.showinfo("Exito", "Se actualizo correctamente el archivo startup-config de " + self.eleccion.get())
            except Exception as e:
                ftp.quit()
                importarw.destroy()
                messagebox.showerror("Error!", "Ocurrio un error al actualizar el archivo startup-config de " + self.eleccion.get() + "\n" + e.args[0])

        importarw = Toplevel()
        importarw.title("Importar la configuracion")
        importarw.resizable(False, False)
        label1 = ttk.Label(importarw, text="Edite el nuevo archivo startup-config para " + self.eleccion.get() + "\n")
        label1.grid(columnspan=2, row=0)
        st = ""
        with open('startup-config', 'r') as sc:
            st = sc.read()
        scrbar1 = ttk.Scrollbar(importarw, orient=VERTICAL)
        scrbar1.grid(column=1, row=1, sticky="NS")
        text1 = Text(importarw, yscrollcommand=scrbar1.set)
        text1.insert(INSERT, st)
        scrbar1.config(command=text1.yview)
        text1.grid(column=0, row=1)
        btn1 = ttk.Button(importarw, text="Actualizar\nstartup-config", command=lambda: enviar())
        btn1.grid(columnspan=2, row=2)


Main() 