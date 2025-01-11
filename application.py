import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
import psutil
import threading
import time

class NetworkMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Monitor")
        self.root.geometry("500x400")
        self.root.attributes('-topmost', True)
        self.root.resizable(False, False)

        # Définir une icône personnalisée
        self.root.iconbitmap("Logo.ico")

        # Définir le style général
        self.set_style()

        # Variables pour le graphique
        self.time_data = []
        self.traffic_data = []

        # Interface graphique
        self.create_widgets()

        # Thread pour mettre à jour les données réseau
        self.running = True
        self.update_thread = threading.Thread(target=self.update_data)
        self.update_thread.start()

    def set_style(self):
        # Appliquer un thème ttk
        style = ttk.Style()
        style.theme_use("clam")

        # Configurer les couleurs
        style.configure("TButton", font=("Helvetica", 12), padding=6)
        style.configure("TFrame", background="#2b2b2b")  # Fond principal
        style.configure("TLabel", font=("Helvetica", 12), background="#2b2b2b", foreground="white")

        # Configurer les boutons
        style.configure("QuitButton.TButton", foreground="#6c0c0c", background="#ff5555", padding=8)

    def create_widgets(self):
        # Cadre principal
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Label titre
        title_label = ttk.Label(main_frame, text="Moniteur Réseau", style="TLabel", anchor="center", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # Matplotlib graphique
        self.figure, self.ax = plt.subplots(figsize=(4.5, 2.5))

        # Appliquer un fond sombre
        self.figure.patch.set_facecolor("#2b2b2b")
        self.ax.set_facecolor("#1e1e1e")

        self.ax.set_title("Débit réseau", fontsize=12, color="#ffffff")
        self.ax.set_xlabel("Temps (s)", fontsize=10, color="#dddddd")
        self.ax.set_ylabel("Débit", fontsize=10, color="#dddddd")
        self.ax.spines['top'].set_color('#ffffff')
        self.ax.spines['bottom'].set_color('#ffffff')
        self.ax.spines['left'].set_color('#ffffff')
        self.ax.spines['right'].set_color('#ffffff')
        self.ax.tick_params(colors="#dddddd")

        # Définir un formateur pour les unités dynamiques
        self.ax.yaxis.set_major_formatter(FuncFormatter(self.format_units))

        self.line, = self.ax.plot([], [], label="Octets envoyés/s", color="#00acee")
        self.ax.legend(facecolor="#2b2b2b", edgecolor="#ffffff", labelcolor="#ffffff", loc="upper left")

        # Ajuster les marges pour éviter les coupures
        self.figure.tight_layout()

        # Intégrer le graphique dans Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, master=main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bouton Quitter
        quit_button = ttk.Button(main_frame, text="Quitter", style="QuitButton.TButton", command=self.quit_app)
        quit_button.pack(pady=10)
        
         # Modifier le curseur lors du survol du bouton "Quitter"
        quit_button.bind("<Enter>", lambda event: quit_button.config(cursor="hand2"))  # Changer le curseur
        quit_button.bind("<Leave>", lambda event: quit_button.config(cursor=""))  # Retour au curseur par défaut

    def format_units(self, value, _):
        """Formater les valeurs en fonction de leur échelle."""
        if value >= 1e9:
            return f"{value / 1e9:.2f} Go"
        elif value >= 1e6:
            return f"{value / 1e6:.2f} Mo"
        elif value >= 1e3:
            return f"{value / 1e3:.2f} Ko"
        else:
            return f"{value:.0f} octets"

    def update_data(self):
        prev_sent = psutil.net_io_counters().bytes_sent
        start_time = time.time()

        while self.running:
            time.sleep(0.2)  # Intervalle réduit pour plus de fluidité
            current_sent = psutil.net_io_counters().bytes_sent
            elapsed_time = time.time() - start_time

            # Calcul des octets envoyés par seconde (moyenne sur 1 seconde)
            bytes_sent_per_sec = (current_sent - prev_sent) / 0.2
            prev_sent = current_sent

            # Mise à jour des données
            self.time_data.append(elapsed_time)
            self.traffic_data.append(bytes_sent_per_sec)

            # Garder un maximum de 60 points sur le graphique
            if len(self.time_data) > 60:
                self.time_data.pop(0)
                self.traffic_data.pop(0)

            # Mettre à jour le graphique
            self.line.set_data(self.time_data, self.traffic_data)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()

    def quit_app(self):
        self.running = False
        self.update_thread.join()
        self.root.destroy()

# Lancer l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkMonitorApp(root)
    root.mainloop()
