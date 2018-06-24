#!/usr/bin/env python3

#Grundlagen der Informatik II, SS 2018
#Projekt Cocktailmischmaschiene
#Aufgabe 2
#Autoren: Marco Baier, Nicolas Buhr, Marcel Dinse
#Matrikelnummern: 4444363, 4444295, 4440877
#Abgabedatum: 24.06.18
#Beschreibung: Verschiedene Getränke werden mit Hilfe von Pumpen aus ihren Behältern in ein Glas befördert.
#              Hierzu können am Computer entweder bestehende Rezepte ausgewählt oder die Mengenangaben manuell eingegeben werden.
#              Die geforderten Mengen werden an den Arduino übertragen und dieser steuert die Pumpen.


##Verwendete Bibliotheken:
#Bibliothek für die graphische Oberfläche
from tkinter import * 
##Bibliothek die vorgefertigte Dateimanagementfenster enthält (z.B. um Dateien zu öffnen).
from tkinter.filedialog import * 
##Mit pickle ist es möglisch Listen als Datei zu speichern.
import pickle 
##Die Bibliothek socket ist für die W-Lan Kommunikation mit dem Arduino zuständig.
import socket as so

##Farbeinstellungen
##Im folgenden werden Farben in bestimmte Variablen gespeichert, sodass z.B. Buttons einheitlich aussehen und die Farbe auf Wunsch leicht
##geändert werden kann.
# @param hlcolor  Überschriftenfarbe
hlcolor = 'brown4'
# @param bgcolor  Hintergrundfarbe von Fenstern
bgcolor = 'grey12'
# @param fgcolor  Schriftfarbe vom Fenstern
fgcolor = 'grey70'
# @param boxbgcolor  Hintergrundfarbe von Buttons, Textfeldern etc.
boxbgcolor = 'grey30'
# @param boxfgcolor  Textfarbe von Buttons, Textfeldern etc.
boxfgcolor = 'grey75'

##Starteinstellungen
# @param textsize Die Textgröße ist standardmäßig bei Programmstart auf 4 eingestellt und wird später mit unterschiedlichen Faktoren für Überschriften oder normalen Texten multipliziert, sodass sich durch die Änderung der Variable textsize die Schriftgröße ändert, aber das Verhältnis gleich 
#bleibt. 
textsize = 4 
# @param schriftart  Als Schriftart wird im ganzen Programm Arial verwendet.
schriftart = 'Arial'

# @param filename  Zum speichern wird die Variable filename erstellt. 
filename = ''

# @param number_of_ingredients  Die Anzahl der Zutaten ist zunächst 3
number_of_ingredients = 3
# @param glas_size  und die Glasgröße (maximale Füllmenge) auf 25cl eingestellt.
glas_size = 25

# @param recepies  In recepies werden Objekte der Klasse Recepi gespeichert.
recepies = []
# @param settings  Die Variablen settings und
settings = 0
# @param arduino  sind zunächst nur Platzhalter und werden später noch geändert.
arduino = 0

## Funktion um Textgröße und Schriftart in den Textartpresets zu aktualisieren.
# @param global text            Variable für die Größe des normalen Textes.
# @param global headline        Variable für die Größe von Überschriften.
# @param global mainheadline    Variable für die Größe von Hauptüberschriften.
def update_textsize():
    global text 
    global headline
    global mainheadline
    global schriftart
    global textsize
    text = schriftart+' '+str(5*textsize) 
    headline = schriftart+' '+str(7*textsize)+' bold'
    mainheadline = schriftart+' '+str(12*textsize)+' bold'

update_textsize() 

## Funktion um die Textgröße zu verkleinern.
def decr_size(): 
    global textsize
    global settings
    if textsize > 1:
        textsize -= 1
        update_textsize()
        mainwindow.hlframe.destroy()
        mainwindow.create_hlframe('Cocktails')
        if settings != 0:
            settings.window.destroy()
        settings = Settings_window('Einstellungen')
        settings.done()

## Funktion um die Textgröße zu vergrößern.
def incr_size():
    global textsize
    global settings
    if textsize < 16:
        textsize += 1
        update_textsize()
        mainwindow.hlframe.destroy()
        mainwindow.create_hlframe('Cocktails')
        if settings != 0:
            settings.window.destroy()
        settings = Settings_window('Einstellungen')
        settings.done()

## Erstellung einer Fehlermeldung, die bei Buttondruck geschlossen wird
def create_error_window(error):
    error_window = Toplevel(bg=bgcolor) 
    error_window.title('Error:') 
    error_headline = Label(error_window, text='Error', font=headline, bg=bgcolor, fg=hlcolor)
    error_headline.pack()    
    error_label = Label(error_window, text=error, font=text, bg=bgcolor, fg=fgcolor)
    error_label.pack()
    error_button = Button(error_window, text='OK', font=text, command=error_window.destroy, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0)
    error_button.pack() 
## Klasse zur Kommunikation mit dem Arduino
class Arduino(object):
    
    ## Initiator der Klasse (Verbindungsaufbau)
    # @param host   iP-Adresse des Netzwerks
    # @param port   Passwort zum Verbinden
    def __init__(self, host, port): 
        self.socket = so.socket() 
        self.socket.connect((host, port)) 
        self.socket.setblocking(False)

    ## Funktion die den Text (in utf8 codiert) an den Arduino sendet. 
    # @param command    Text der gesendet werden soll. 
    def send_command(self, command): 
        self.socket.send(command.encode('utf-8') + b'\n') 
    
    ## Verbindung wird wieder geschlossen
    def close(self): 
        self.socket.close()

## Eine Klasse, die die Liste der Zutaten enthält und mehrere Fenster zur Eingabe erstellen kann. 
class Ingredientlist(object):
    
    ## Liste der Zutaten wird initialisiert
    def __init__(self):
        # @ brief   Liste mit Anzahl der Zutaten (number_of_ingredients, Standardmäßig 3) wird erstellt und mit den Strings: 
        #           Zutat 1, Zutat 2,..., Zutat (a+1) gefüllt.
        self.ilist = [] 
        for a in range(number_of_ingredients): 
            self.ilist.append('Zutat '+str(a+1))
    
    
    ## Erstellung der graphischen Oberfläche für Zutaten in den Einstellungen. Dafür wird eine Überschrift ('Zutaten'), Felder zur Eingabe mit der Anzahl der Zutaten, sowie die Buttons '+' und '-' zum Hinzufügen einer neuen Zutat zur Liste ertelllt.
    # @param master   Zeigt Zutatenfenster mit Eingabefeldern im Einstellungsmenü an
    def show_in_settings(self, master):
        self.iframe_s = Frame(master, bg=bgcolor) 
        self.iframe_s.pack(side=LEFT)
        self.ilabel = Label(self.iframe_s, text='Zutaten:', font=text, bg=bgcolor, fg=fgcolor) 
        self.ilabel.pack()
        self.ientrys = [] 
        for a in range(number_of_ingredients):
            self.ientrys.append(Entry(self.iframe_s, font=text, width=15, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0))
            self.ientrys[a].insert(0, self.ilist[a])
            self.ientrys[a].pack()
        self.editframe = Frame(self.iframe_s, bg=bgcolor)
        self.editframe.pack(fill=X) 
        self.delbutton = Button(self.editframe, width=2, text='-', font=text, command=self.del_ingredient, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0)
        self.delbutton.pack(side=RIGHT) 
        self.addbutton = Button(self.editframe, width=2, text='+', font=text, command=self.add_ingredient, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0)
        self.addbutton.pack(side=RIGHT) 
    
    ## Zeigt die Zutaten im Hauptfenster bei 'Dein Cocktail' an
    def show_in_main(self, master): 
        self.iframe_m = Frame(master, bg=bgcolor) 
        self.iframe_m.pack(side=LEFT) 
        self.inames = [] 
        for a in range(number_of_ingredients):
            self.inames.append(Label(self.iframe_m, text=self.ilist[a], font=text, bg=bgcolor, fg=fgcolor, highlightthickness=0)) 
            self.inames[a].pack()
    
    ## Zutaten werden aus den Felder für Zutaten im Einstellungsfenster kopiert und in der Liste der Zutaten gespeichert.
    def save(self): #für speichern in den einstellungen
        for a in range(number_of_ingredients):
            self.ilist[a] = self.ientrys[a].get() #beim schließen von den settings speichert ientrys die eingegebenen Zutaten in ilist

    ## Funktion zum Hinzufügen einer Zutat bei Button-Druck '+', solange bis es 10 sind.
    def add_ingredient(self): 
        global number_of_ingredients 
        global settings
        global recepies
        settings.save_all() 

        if number_of_ingredients < 10: 
            settings.bodyframe.destroy() #löscht mittelteil aus einstellungsfenster
            settings.botframe.destroy() #löscht unteren teil aus einstellungsfenster 

            number_of_ingredients += 1 
            self.ilist.append('Zutat '+str(number_of_ingredients))
            for a in range(len(recepies)):
                recepies[a].amounts.append(0) 

            settings.create_bodyframe() 
            settings.create_botframe() 
        
        else:
            create_error_window('Es sind nicht mehr als 10 Zutaten möglich.') # oben definierte Funktion wird benutzt

    ## Funktion zum Löschen einer Zutat bei Button-Druck '-', solange es mehr als 0 sind.
    def del_ingredient(self): #Letzter Eintrag der Liste wird gelöscht
        global number_of_ingredients
        global settings
        settings.save_all()
        
        if number_of_ingredients > 0:
            settings.bodyframe.destroy()
            settings.botframe.destroy()

            number_of_ingredients -= 1
            ingredientlist.ilist.remove(ingredientlist.ilist[number_of_ingredients])
            for a in range(len(recepies)): # in allen Rezepten wird die Menge der letzten Zutat gelöscht
                del recepies[a].amounts[-1]
            
            settings.create_bodyframe()
            settings.create_botframe()

        else:
            create_error_window('Es sind nicht weniger als 0 Zutaten möglich.')# errorfunktion wird gestartet mit anderer fehlermeldung

## Objekt wird erstellt.
ingredientlist = Ingredientlist() 

## Funktion zum Laden von Dateien, mit Hilfe der Bibliotheken tkinter_filedialog und pickle. Die gespeicherten Listen und Werte werden an den entsprechenden Plätzen eingefügt. (Umkehrung von save_file)
def load_file():
    global filename
    global number_of_ingredients
    global recepies
    global ingredientlist
    global settings
    global glas_size

    filename = askopenfilename(initialdir="/", title="Select file", filetypes=(("cocktail files","*.cocktail"),("all files","*.*"))) #dateiname wird in filename gespeichert
    save_list = pickle.load(open(filename,'rb'))

    number_of_ingredients = save_list[0] #save funktion wird umgekehrt.
    glas_size = save_list[1]
    ingredientlist.ilist = save_list[4]
    recepies = []
    for a in range(len(save_list[2])):
        recepies.append(Recipe())
        recepies[a].name = save_list[2][a]
        recepies[a].amounts = save_list[3][a]
    
    if settings != 0:
        settings.window.destroy()
    settings = Settings_window('Einstellungen')
    settings.update_main()

## Funktion um Dateien zu speichern. Die Funktion kann dazu auf alle relevanten Listen zugreifen und speichert Namen und Mengen der Rezepte in neuen Listen. Anschließend werden alle wichtigen Werte und Listen in eine neue Liste (save_list) gespeichert. 
##  Ist kein Dateiname vorhanden wird ein Dialogfenster von tkinter_filedialog geöffnet. 
##  Anschließend wird die Liste mittels der Bibliothek pickle gespeichert. 
def save_file():
    global filename
    global number_of_ingredients
    global recepies
    global ingredientlist
    global glas_size

    names = []
    amounts = [] 
    for a in range(len(recepies)):
        names.append(recepies[a].name) 
        amounts.append(recepies[a].amounts) 
    save_list = [number_of_ingredients, glas_size, names, amounts, ingredientlist.ilist] 

    if filename == '': 
        filename = asksaveasfilename(initialdir="/", title="Select file", filetypes=(("cocktail files","*.cocktail"),("all files","*.*")))
    pickle.dump(save_list, open(filename, 'wb'), protocol=4) 

## Funktion führt erst das Dialogfenster von tkinter_filedialog aus und danach die Funktion save_file()
def save_to_file():
    global filename

    filename = asksaveasfilename(initialdir="/", title="Select file", filetypes=(("cocktail files","*.cocktail"),("all files","*.*"))) 
    save_file()


## Klasse zum Erstellen der Rezepte.
class Recipe(object): 

    ## Liste mit Namen der Rezepte und Mengen der Zutaten wird initialisiert.
    def __init__(self):
        self.name = 'Name' 
        self.amounts = [] 
        for a in range(number_of_ingredients): 
            self.amounts.append(0) 

    ## Vorhandene Namen und Mengen werden im Einstellungsfenster angezeigt, wird dieses geöffnet.
    def show_in_settings(self, master): 
        self.rframe = Frame(master, bg=bgcolor) 
        self.rframe.pack(side=LEFT)
        self.rname = Entry(self.rframe, font=text, width=12, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0) 
        self.rname.insert(0, self.name)
        self.rname.pack()
        self.rspinbox = [] 
        for a in range(number_of_ingredients):
            self.rspinbox.append(Spinbox(self.rframe, font=text, from_=0, to=glas_size, width=12, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0))
            self.rspinbox[a].delete(0, 'end') 
            self.rspinbox[a].insert(0, self.amounts[a]) 
            self.rspinbox[a].pack() 
        self.delete_button = Button(self.rframe, text='Löschen', font=text, command=self.delete, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0)
        self.delete_button.pack() 

    ## Vohandene Namen und Mengen werden im Hauptfenster angezeigt.
    def show_in_main(self, master): #rahmen mit mischen knopf.
        self.rframe = Frame(master, bg=bgcolor) 
        self.rframe.pack(side=LEFT, fill=Y)
        self.innerframe = Frame(self.rframe, bg=bgcolor)
        self.innerframe.pack(side=TOP)
        self.rnamelabel = Label(self.innerframe, font=headline, bg=bgcolor, fg=fgcolor, highlightthickness=0)
        self.rnamelabel.config(text=' '+self.name+' ')
        self.rnamelabel.pack()
        self.ramount = []
        for a in range(number_of_ingredients):
                self.ramount.append(Label(self.innerframe, font=text, bg=bgcolor, fg=fgcolor, highlightthickness=0))
                self.ramount[a].config(text=str(self.amounts[a])+' cl '+ingredientlist.ilist[a])
                if self.amounts[a] >= 1:
                    self.ramount[a].pack()
        self.rbutton = Button(self.innerframe, text='Mischen', font=text, command=self.send, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0)
        self.rbutton.pack()

    ## Namen und Mengen werden aus den Boxen des Einstellungsfensters gespeichert.
    def save(self): 
        self.name = self.rname.get()
        for a in range(number_of_ingredients):
            self.amounts[a] = int(self.rspinbox[a].get())

    ## Bei Knopfdruck 'Mischen' im Hauptfenster werden die Mengen der Zutaten in einem String gespeichert und an den Arduino gesendet.
    def send(self): 
        self.send_text = ''
        for a in range(number_of_ingredients): 
            self.send_text+=(str(self.amounts[a])+',') 
        for a in range(10-number_of_ingredients):
            self.send_text+='0,' 
        arduino.send_command(self.send_text) 

    ## Funktion zum Löschen einer Spalte (eines kompletten Rezepts) im Einstellungsfenster. 
    def delete(self): 
        global settings
        recepies.remove(self)
        settings.save_all()
        settings.bodyframe.destroy()
        settings.botframe.destroy()
        settings.create_bodyframe()
        settings.create_botframe()

    ## Mengen aller Zutaten eines Rezepts werden aufaddiert und in total_amount gespeichert. (um später mit glas_size zu vergleichen).
    def give_total_amount(self):
        self.total_amount = 0 
        for a in range(number_of_ingredients):
            self.total_amount += int(self.rspinbox[a].get()) 
        return self.total_amount 

## Die Events sind für Tastenkombinationen notwendig und führen die entsprechende Funktion aus.

def key_open_settings(event):
    mainwindow.open_settings()

def key_open_secret_settings(event):
    mainwindow.open_secret_settings()

def key_save(event):
    save_file() 

def key_save_to(event):
    save_to_file()

def key_load(event):
    load_file()

def key_decr_size(event):
    decr_size()

def key_incr_size(event):
    incr_size()

## Klasse des Hauptfensters
class Main_window(object):

    ## Initialisierung des Rahmens des Hauptfensters und Ausführung der Optionen die es beinhaltet. 
    def __init__(self, title):
        self.window = Tk()
        self.window.title(title)

        self.create_menubar() 
        self.key_combinations() 
        self.create_hlframe(title)
        self.create_bodyframe()
        self.create_botframe()
        self.open_IP_Window()


    ## Die Menübar wird erstellt. Dafür werden verschiedene Menüpunkte erstellt, die nach unten ausklappbar sind und Optionen anbieten. 
    ## Beim Anklicken verweisen sie auf die vorher erstellten Funktionen load_file, save_file etc.
    def create_menubar(self):
        self.menubar = Menu(self.window) 
        
        self.mainmenu = Menu(self.menubar)
        self.mainmenu.add_command(label='Einstellungen ...   ctrl e', command=self.open_settings)
        self.menubar.add_cascade(label='Cocktails', menu=self.mainmenu)

        self.filemenu = Menu(self.menubar) 
        self.filemenu.add_command(label='Öffnen ...                       ctrl o', command=load_file)  
        self.filemenu.add_command(label='Speichern                      ctrl s', command=save_file) 
        self.filemenu.add_command(label='Speichern unter ...   ctrl ⇧ s', command=save_to_file)
        self.menubar.add_cascade(label='Datei', menu=self.filemenu)

        self.viewmenu = Menu(self.menubar) 
        self.viewmenu.add_command(label='Schriftgröße verkleinern   ctrl -', command=decr_size) 
        self.viewmenu.add_command(label='Schriftgröße vergrößern   ctrl +', command=incr_size)
        self.menubar.add_cascade(label='Anzeige', menu=self.viewmenu)
        
        self.window.config(menu=self.menubar) 

    ## Funktion der Definition der Tastenkombinationen für Tastenkombinationen. Sie verweisen auf die Events, welche dann die Funktionen ausführen.
    def key_combinations(self): 
        self.window.bind('<Control-e>', key_open_settings) 
        self.window.bind_all('<Control-E>', key_open_secret_settings) 
        self.window.bind_all('<Control-o>', key_load)
        self.window.bind_all('<Control-s>', key_save)
        self.window.bind_all('<Control-S>', key_save_to)
        self.window.bind('<Control-minus>', key_decr_size)
        self.window.bind('<Control-plus>', key_incr_size)

    ## Überschrift im Hauptfenster wird erstellt.
    def create_hlframe(self, title):
        self.hlframe = Frame(self.window, bg=bgcolor)
        self.hlframe.pack(fill=X)
        self.headline = Label(self.hlframe, text=title, font=mainheadline, bg=bgcolor, fg=hlcolor)
        self.headline.pack(side=LEFT)

    ## Die Rezepte aus Namen und Mengen werden im Hauptfenster erstellt.
    def create_bodyframe(self):
        self.bodyframe = Frame(self.window, bg=bgcolor)
        self.bodyframe.pack(fill=BOTH, expand=TRUE)
        for a in range(len(recepies)):
            recepies[a].show_in_main(self.bodyframe)

    ## Erstellung des Bereichs 'Dein Cocktail' im Hauptfenster
    def create_botframe(self): 
        self.botframe = Frame(self.window, bg=bgcolor)
        self.botframe.pack(fill=X)
        self.bothl = Label(self.botframe, text='Dein Cocktail', font=headline, bg=bgcolor, fg=fgcolor)
        self.bothl.pack()
        self.botbody = Frame(self.botframe, bg=bgcolor)
        self.botbody.pack()
        self.botbodyleft = Frame(self.botbody, bg=bgcolor)
        self.botbodyleft.pack(side=LEFT)
        self.botbodyright = Frame(self.botbody, bg=bgcolor)
        self.botbodyright.pack(side=LEFT)

        ingredientlist.show_in_main(self.botbodyleft)
        self.userentrys = []
        for a in range(number_of_ingredients):
            self.userentrys.append(Spinbox(self.botbodyright, font=text, from_=0, to=glas_size, width=3, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0))
            self.userentrys[a].pack()
        self.mix_button = Button(self.botframe, text='Mischen', font=text, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0, command=self.mix_userrecepie)
        self.mix_button.pack()

    ## Funktion zum erstellen des Einstellungsfensters.
    def open_settings(self):
        global settings
        settings = Settings_window('Einstellungen')

    ## Funktion zum erstellen des Einstellungsfensters für die Glasgröße.
    def open_secret_settings(self):
        self.secret_settings = Secret_settings_window('Glasgröße')

    ## Funktion zum erstellen des IP-Fensters.
    def open_IP_Window(self):
        self.ip_window = IP_Window('IP')

    ## Funktion die ausgeführt wird wenn Mischen-Button im Hauptfenster, 'Dein Cocktail' gedrückt wird. String mit Mengen der Zutaten 
    #  wird an den Arduino gesendet, wenn die Gesamtmenge kleiner als die Glasgröße ist.
    def mix_userrecepie(self):
        self.userrecepi = []
        for a in range(number_of_ingredients):
            self.userrecepi.append(int(self.userentrys[a].get()))
        self.total_amount = 0
        for a in range(number_of_ingredients):
            self.total_amount += int(self.userentrys[a].get())

        if self.total_amount <= glas_size:
            self.send_text = ''
            for a in range(number_of_ingredients):
                self.send_text+=(str(self.userrecepi[a])+',')
            for a in range(10-number_of_ingredients):
                self.send_text+='0,'
            arduino.send_command(self.send_text)

        else:
            create_error_window('Maximal '+str(glas_size)+'cl pro Cocktail.')

## Klasse des Einstellungsfensters.
class Settings_window(object):

    ## Fenster wird als Nebenfenster initialisiert
    def __init__(self, title):
        self.window = Toplevel()
        self.window.title(title)

        self.create_hlframe(title)
        self.create_bodyframe()
        self.create_botframe()
    
    ## Überschriftszeile im Einstellungsfenster 
    def create_hlframe(self, title):
        self.hlframe = Frame(self.window, bg=bgcolor)
        self.hlframe.pack(fill=X)
        self.headline = Label(self.hlframe, text=title, font=mainheadline, bg=bgcolor, fg=hlcolor)
        self.headline.pack(side=LEFT)

    ## Listen und Werte aus dem Hauptfenster werden ins Einstellungsfensterkopiert und das Fenster ertsellt.
    def create_bodyframe(self):
        self.bodyframe = Frame(self.window, bg=bgcolor)
        self.bodyframe.pack(fill=X)
        
        ingredientlist.show_in_settings(self.bodyframe)
        for a in range(len(recepies)):
            recepies[a].show_in_settings(self.bodyframe)
    
    ## Die Buttons 'Neu' und 'Fertig' im Einstellungsfenster werden erstellt.
    def create_botframe(self):
        self.botframe = Frame(self.window, bg=bgcolor)
        self.botframe.pack(fill=X)
        for x in range(1):
            Grid.columnconfigure(self.botframe, x, weight=1)

        self.add_button = Button(self.botframe, text='Neu', font=text, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0, command=self.add)
        self.add_button.grid(row=0, column=0, sticky=W+S)
        self.done_button = Button(self.botframe, text='Fertig', font=text, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0, command=self.done)
        self.done_button.grid(row=0, column=1, sticky=E+S)

    ## Die eingegebenen Zutaten und Rezepte werden gespeichert.
    def save_all(self):
        for a in range(len(recepies)):
            recepies[a].save()
        ingredientlist.save()

    ## Funktion zerstört altes 'Cocktails'-Fenster und baut das neue auf, wenn self.done ausgeführt wird
    def update_main(self):
        mainwindow.bodyframe.destroy()
        mainwindow.create_bodyframe()
        mainwindow.botframe.destroy()
        mainwindow.create_botframe()

    ## Funktion aktualisiert das Hauptfenster, wenn die eingegebenen cl-Angaben kleiner als die Größe des Glases ist. 
    ## Sonst wird das 'Error'-Fenster aufgerufen. (Bei Knopfdruck auf 'Fertig'). 
    def done(self):
        self.max_amount = 0
        for a in range(len(recepies)):
            if recepies[a].give_total_amount() > self.max_amount:
                self.max_amount = recepies[a].give_total_amount()
        if self.max_amount <= glas_size:
            self.save_all()
            self.update_main()
            self.window.destroy()
        else:
            create_error_window('Maximal '+str(glas_size)+'cl pro Cocktail.')

    ## Funktion zum Hinzufügen eines neuen Rezepts beim Druck auf den Button 'Neu'    
    def add(self):
        recepies.append(Recipe())
        recepies[len(recepies)-1].show_in_settings(self.bodyframe)

## Klasse in der das Fenster für die cl-Eingabe des Glases eingestellt werden kann.
class Secret_settings_window(object):

    ## Initialisierung des Fensters Glasgröße.
    def __init__(self, title):
        self.window = Toplevel(bg=bgcolor)
        self.window.title(title)
        self.headline = Label(self.window, text=title, font=mainheadline, bg=bgcolor, fg=hlcolor)
        self.headline.pack()
        self.text = Label(self.window, text='Maximum pro Glas in cl:', font=text, bg=bgcolor, fg=fgcolor)
        self.text.pack()
        self.size_spinbox = Spinbox(self.window, font=text, from_=0, to=100, width=3, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0)
        self.size_spinbox.delete(0, 'end')
        self.size_spinbox.insert(0, glas_size)
        self.size_spinbox.pack()
        self.button = Button(self.window, text='Fertig', font=text, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0, command=self.done)
        self.button.pack()
    
    ## Funktion die ausgeführt wird wenn 'Fertig'-Button im Glasgröße-Fenster gedrückt wird. 
    # @param global glas_size   Wert aus der Spinbox wird als Integer in der Variable glas_size gespeichert.
    def done(self):
        global glas_size
        glas_size = int(self.size_spinbox.get())
        self.window.destroy()

## Klasse in der das Fenster mit Eingabefeld für iP und Port erstellt wird.
class IP_Window(object):

    ## Initialisierung des Fensters IP.
    def __init__(self, title):
        self.window = Toplevel(bg=bgcolor)
        self.window.title(title)
        self.ip_text = Label(self.window, text='IP-Adresse:', font=text, bg=bgcolor, fg=fgcolor)
        self.ip_text.pack()
        self.ip_entry = Entry(self.window, font=text, width=15, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0)
        self.ip_entry.pack()
        self.port_text = Label(self.window, text='Port:', font=text, bg=bgcolor, fg=fgcolor)
        self.port_text.pack()
        self.port_entry = Entry(self.window, font=text, width=6, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0)
        self.port_entry.pack()
        self.button = Button(self.window, text='Fertig', font=text, bg=boxbgcolor, fg=boxfgcolor, highlightthickness=0, command=self.done)
        self.button.pack()

    ## Funktion die ausgeführt wird wenn 'Fertig'-Button im iP-Window gedrückt wird. Einträge für iP und host werden an die Klasse Arduino übergeben und das Fenster zerstört. 
    def done(self):
        global arduino
        host = self.ip_entry.get() 
        port = self.port_entry.get() 
        arduino = Arduino(host, int(port)) 
        self.window.destroy() 

## Objekt mit dem Namen mainwindow der Klasse Main_window und mit dem Titel Cocktails wird erstellt.
mainwindow = Main_window('Cocktails')
## Das Hauptfenster wird gestartet. 
mainwindow.window.mainloop() 