"""
collision/application.py: root window class
"""
import tkinter as tk
from tkinter import ttk
from . import views as v
from . import models as m

import numpy as np
import threading

class Application(tk.Tk):  # subclase from Tk instead of Frame
    """Application root window.
    It needs to contain:
        - A title label
        - An instance of MyForm class (call and place form in GUI)

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.model = m.myModel()
        self.model = m.Simulation(self, 1, 0.01)

        self.simform = v.SimForm(self, self.model)

        # window title
        self.title('Particle Simulation')
        self.columnconfigure(0, weight=0)

        # header
        # ttk.Label(  # parent is self. self is our Tk instance inside this class
        #     self, text='Header',
        #     font=("TkDefaultFont, 18")
        # ).grid(row=0)

        # Add form with widgets
        self.simform.grid(row=0, sticky=tk.W + tk.E)
        self.simform.bind('<<GenerateSim>>', self._on_generate)

        # def show_sim(self, *_):
        #     nparticles = 20
        #     radii = np.random.random(nparticles)*0.03+0.02
        #     # chart = v.Simulation(
        #     chart = m.Simulation(
        #         self.simform, nparticles, radii
        #     )
        #     chart.grid(row=2, column=4, columnspan=3)
        #     chart.do_animation()

        # show_sim(self)

        self._on_generate(self)

    def thread_safe_gui_update(self, func, *args):
        self.after(0, func, *args)

    def show_error_message(self, message):
        # Display an error message at the top or in a dedicated label
        error_label = ttk.Label(self, text=message, foreground="red")
        error_label.grid(row=0, column=0, columnspan=3, sticky=tk.W + tk.E)
        self.after(5000, error_label.destroy)  # Remove the error message after 5 seconds



    def _on_generate(self, *_):
        '''
        To prevent the GUI from freezing, we offload the simulation logic 
        to a separate thread. Tkinter itself isn't thread-safe, so only the simulation 
        logic should run in a separate thread, while any updates to the GUI should be 
        done using thread-safe methods like after().
        '''
        if hasattr(self, 'chart'):
            self.chart.destroy()

        try:
            nparticles = self.simform._vars['num_particles'].get()
            radii = np.random.random(nparticles) * 0.03 + 0.02
            styles = {'edgecolor': 'C0', 'linewidth': 2, 'fill': None}

            # Create the chart
            self.chart = m.Simulation(self.simform, nparticles, radii, styles)
            self.chart.grid(row=0, column=4, columnspan=3)

            # Run simulation in a separate thread
            thread = threading.Thread(target=self.chart.do_animation, args=(False,))
            thread.start()
        except Exception as e:
            self.show_error_message(f"Error: {e}")



if __name__ == "__main__":
    # create instance of our application and start its mainloop
    app = Application()
    app.mainloop()
