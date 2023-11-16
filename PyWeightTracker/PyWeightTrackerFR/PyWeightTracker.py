#              PyWeightTracker.py - Logiciel de suivi de poids

#  Nom du fichier: PyWeightTracker.py
#  Description: Logiciel de suivi de poids
#  Auteur(s): Électro L.I.B (2023)
#  Optimisation: ChatGPT2
#  Version: 1.0
#  Licence: GPLv3

#  PyWeightTracker.py est un logiciel libre : vous pouvez le redistribuer et/ou le modifier
#  selon les termes de la licence publique générale GNU telle que publiée par
#  la Free Software Foundation, soit la version 3 de la licence, ou
#  (à votre choix) toute version ultérieure.

#  Ce programme est distribué dans l'espoir qu'il sera utile,
#  mais SANS AUCUNE GARANTIE ; sans même la garantie implicite de
#  QUALITÉ MARCHANDE ou D'ADÉQUATION À UN USAGE PARTICULIER.
#  Consultez la licence publique générale GNU pour plus de détails.

#  Vous devriez avoir reçu une copie de la licence publique générale GNU
#  avec ce programme. Si ce n'est pas le cas, consultez <http://www.gnu.org/licenses/>.
#                 Référence dans le fichier "COPYING.txt".

import tkinter as tk
import tkinter.messagebox as mbox
from tkinter import ttk
import csv
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import configparser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import Calendar


class PyWeightTrackerApp:
    def update_goal_entry(self):
        for data in self.weight_data:
            if isinstance(data[0], str) and data[0] == "Objectif":
                self.goal_var.set(data[1])
                break

    def __init__(self, root):
        self.root = root
        self.root.title("PyWeightTracker")

        self.config = configparser.ConfigParser()
        self.config.read('PyWeightTracker.cfg')

        self.weight_text = tk.StringVar()

        self.goal_label = tk.Label(self.root, text="Objectif de poids (en Livres):")
        self.weight_label = tk.Label(self.root, text="Poids (Livres):")

        self.weight_label.pack()

        self.unit_var = tk.IntVar()
        self.unit_var.set(self.config.getint('GUI', 'unit_var', fallback=1))
        self.unit_selected()  # Mettre à jour l'étiquette de poids
        self.unit_var.trace_add('write', self.save_config)  # Sauvegarder le choix du bouton radio

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Gérer la fermeture de la fenêtre

        self.weight_data = []
        self.load_weight_data_from_file('weight_data.csv')

        self.create_plot()
        self.create_controls()
        self.update_goal_entry()
        self.update_plot()

        # Définir la date par défaut comme la date actuelle
        default_date = datetime.date.today().strftime('%Y-%m-%d')
        self.date_var.set(default_date)

    def create_plot(self):
        fig, self.ax = plt.subplots(figsize=(8, 4))
        plt.subplots_adjust(bottom=0.2)
        plt.rc('font', size=6)
        self.plot = FigureCanvasTkAgg(fig, master=self.root)
        self.plot.get_tk_widget().pack()
        self.unit_selected()

    def create_controls(self):
        add_weight_frame = tk.Frame(self.root)
        add_weight_frame.pack()

        unit_frame = tk.Frame(self.root)
        unit_frame.pack()

        self.unit_var = tk.IntVar()
        self.unit_var.set(1)  # 1 pour les livres, 2 pour les kilos

        unit_label = tk.Label(unit_frame, text="Unité de mesure:")
        unit_label.grid(row=0, column=0)

        lbs_radio = tk.Radiobutton(unit_frame, text="Livres", variable=self.unit_var, value=1, command=self.unit_selected)
        lbs_radio.grid(row=0, column=1)

        kg_radio = tk.Radiobutton(unit_frame, text="Kilos", variable=self.unit_var, value=2, command=self.unit_selected)
        kg_radio.grid(row=0, column=2)

        self.date_label = tk.Label(add_weight_frame, text="Date:")
        self.date_label.grid(row=0, column=0)

        self.date_var = tk.StringVar()
        self.date_entry = tk.Entry(add_weight_frame, textvariable=self.date_var, state='readonly')
        self.date_entry.grid(row=0, column=1)
        self.date_button = tk.Button(add_weight_frame, text='   Choisir une date   ', command=self.choose_date)
        self.date_button.grid(row=0, column=2)

        goal_button = tk.Button(add_weight_frame, text="Enregistrer l'objectif", command=self.save_goal)
        goal_button.grid(row=2, column=2, columnspan=2)
        
        self.goal_label = tk.Label(add_weight_frame, text="Objectif de poids (Livres):")

        self.goal_label.grid(row=2, column=0)
        self.goal_var = tk.DoubleVar()
        self.goal_entry = ttk.Entry(add_weight_frame, textvariable=self.goal_var)
        self.goal_entry.grid(row=2, column=1)

        self.weight_label = tk.Label(add_weight_frame, text="Poids (Livres):")
        
        self.weight_label.grid(row=1, column=0)
        self.weight_var = tk.DoubleVar()
        self.weight_spinbox = ttk.Spinbox(add_weight_frame, from_=0, to=300, increment=0.1, textvariable=self.weight_var)
        if self.weight_data:
            last_date, last_weight = self.weight_data[-1]
            self.weight_var.set(last_weight)
        self.weight_spinbox.grid(row=1, column=1)

        add_button = tk.Button(add_weight_frame, text="           Ajouter          ", command=self.add_weight)
        add_button.grid(row=1, column=2, columnspan=2)

        show_button = tk.Button(self.root, text="    Afficher le graphique    ", command=self.show_plot)
        show_button.pack()

        clear_button = tk.Button(self.root, text="Effacer toutes les données", command=self.clear_data)
        clear_button.pack()
        
        lbs_radio = tk.Radiobutton(unit_frame, text="Livres", variable=self.unit_var, value=1, command=self.unit_selected)
        lbs_radio.grid(row=0, column=1)

        kg_radio = tk.Radiobutton(unit_frame, text="Kilos", variable=self.unit_var, value=2, command=self.unit_selected)
        kg_radio.grid(row=0, column=2)

        # Récupérer la dernière sélection du radiobutton
        last_unit_selection = self.config.getint('GUI', 'unit_var', fallback=1)

        # Sélectionner le radiobutton approprié
        if last_unit_selection == 1:
            lbs_radio.select()
        else:
            kg_radio.select()
        # mettre à jour l'étiquette de poids au démarrage
        self.unit_selected()

    def save_goal(self):
        new_goal = self.goal_var.get()

        # Mettre à jour la variable d'objectif de poids dans la liste self.weight_data
        for i, (date, weight) in enumerate(self.weight_data):
            if isinstance(date, str) and date == "Objectif":
                self.weight_data[i] = ("Objectif", new_goal)
                break
        else:
            self.weight_data.append(("Objectif", new_goal))

        self.save_weight_data_to_file('weight_data.csv')
        self.update_plot()

    def choose_date(self):
        top = tk.Toplevel(self.root)
        top.title("Calendrier")

        # Centrer la fenêtre du calendrier au démarrage
        window_width = 400
        window_height = 320

        screen_width = top.winfo_screenwidth()
        screen_height = top.winfo_screenheight()

        x = int((screen_width/2) - (window_width/2))
        y = int((screen_height/2) - (window_height/2))

        top.geometry(f"{window_width}x{window_height}+{x}+{y}")

        cal = Calendar(top, date_pattern='yyyy-mm-dd')
        cal.pack()

        ok_button = tk.Button(top, text="OK", command=lambda: self.update_date(cal, top))
        ok_button.pack()

    def update_date(self, cal, top):
        selected_date = cal.get_date()
        if isinstance(selected_date, str):
            selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
        self.date_var.set(selected_date.strftime('%Y-%m-%d'))
        top.destroy()

    def add_weight(self):
        new_date_str = self.date_var.get()
        new_weight = self.weight_var.get()
        #new_weight *= 0.45359237

        new_date = datetime.datetime.strptime(new_date_str, '%Y-%m-%d').date()

        for i, (date, weight) in enumerate(self.weight_data):
            if date == new_date:
                self.weight_data[i] = (new_date, new_weight)
                break
        else:
            self.weight_data.append((new_date, new_weight))

        self.save_weight_data_to_file('weight_data.csv')
        self.update_plot()
        self.unit_selected() #Pour mettre à jour l'étiquette de poids

    def unit_selected(self):
        if self.unit_var.get() == 2:
            self.weight_label.config(text="Poids (en Kilos):")
            self.goal_label.config(text="Objectif de poids (en Kilos):")
        else:
            self.weight_label.config(text="Poids (en Livres):")
            self.goal_label.config(text="Objectif de poids (en Livres):")
            
    def show_plot(self):
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        sorted_data = sorted(self.weight_data, key=lambda x: x[0] if isinstance(x[0], datetime.date) else datetime.date.min)
        weights = [data[1] for data in sorted_data if isinstance(data[0], datetime.date)]


        sorted_data = sorted(self.weight_data, key=lambda x: x[0] if isinstance(x[0], datetime.date) else datetime.date.min)

        dates = [data[0] for data in sorted_data if isinstance(data[0], datetime.date)]
        weights = [data[1] for data in sorted_data if isinstance(data[0], datetime.date)]
        self.ax.plot(dates, weights, marker='o', label='Données')

        # Afficher l'objectif de poids si celui-ci est défini
        goal_data = [data for data in sorted_data if isinstance(data[0], str) and data[0] == "Objectif"]
        if goal_data:
            goal = goal_data[0][1]
            if goal is not None:  # Vérifiez si l'objectif n'est pas None
                self.ax.axhline(y=goal, color='red', linestyle='--', label='Objectif')

        self.ax.set_title('Évolution du poids')
        self.ax.set_xlabel('Date')
        if self.unit_var.get() == 2:
            self.ax.set_ylabel('Poids (Kilos)')
        else:
            self.ax.set_ylabel('Poids (Livres)')
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.legend()

        self.plot.draw()
        self.unit_selected() # Mettre à jour l'étiquette de poids
        

    def clear_data(self):
        confirmation = mbox.askokcancel("Confirmation", "Êtes-vous sûr de vouloir effacer toutes les données ?")
        if confirmation:
            self.weight_data = []
            self.save_weight_data_to_file('weight_data.csv')
            self.update_plot()

    def save_weight_data_to_file(self, file_name):
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Poids"])

            for data in self.weight_data:
                if isinstance(data[0], datetime.date):
                    date = data[0].strftime('%Y-%m-%d')
                    writer.writerow([date, data[1]])

                elif data[0] == "Objectif":
                    writer.writerow(["Objectif", data[1]])

    def load_weight_data_from_file(self, file_name):
        try:
            with open(file_name, mode='r', newline='') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if row[0] == "Objectif":
                        self.weight_data.append(("Objectif", float(row[1])))
                    else:
                        date = datetime.datetime.strptime(row[0], '%Y-%m-%d').date()
                        weight = float(row[1])
                        self.weight_data.append((date, weight))

                # Vérifiez si l'objectif de poids est déjà présent dans self.weight_data
                for data in self.weight_data:
                    if data[0] == "Objectif":
                        return

                # S'il n'est pas présent, ajoutez-le à la fin de self.weight_data
                self.weight_data.append(("Objectif", None))
        except FileNotFoundError:
            print("Fichier de données introuvable. Création d'un nouveau fichier.")

    def delete_weight(self, event):
        sensitivity_offset = 0.4  # Ajustez le décalage de sensibilité au besoin
        if event.xdata is not None and event.ydata is not None:
            clicked_date = mdates.num2date(event.xdata + sensitivity_offset).date()
            for i, (date, weight) in enumerate(self.weight_data):
                if date == clicked_date:
                    confirmation = mbox.askokcancel("Confirmation", f"Voulez-vous vraiment supprimer l'enregistrement du {date}?")
                    if confirmation:
                        del self.weight_data[i]
                        self.save_weight_data_to_file('weight_data.csv')
                        self.update_plot()
                    break

	
    def save_config(self, *args):
	        self.config['GUI'] = {'unit_var': str(self.unit_var.get())}
	        with open('PyWeightTracker.cfg', 'w') as configfile:
	            self.config.write(configfile)




    def save_config(self, *args):
        self.config['GUI'] = {'unit_var': str(self.unit_var.get())}
        with open('PyWeightTracker.cfg', 'w') as configfile:
            self.config.write(configfile)

    def on_close(self):
        self.save_config()
        self.root.destroy()



root = tk.Tk()
app = PyWeightTrackerApp(root)
# Centrer la fenêtre au démarrage
window_width = 800
window_height = 600

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = int((screen_width/2) - (window_width/2))
y = int((screen_height/2) - (window_height/2))

root.geometry(f"{window_width}x{window_height}+{x}+{y}")
app.plot.mpl_connect('button_press_event', app.delete_weight)
root.mainloop()
