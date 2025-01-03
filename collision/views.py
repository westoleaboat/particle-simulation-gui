"""
collision/views.py: form containing widgets
"""

import tkinter as tk
from tkinter import ttk

from . import widgets as w
from .constants import FieldTypes as FT


class SimForm(tk.Frame):
    """Input Form for widgets

    - self._vars = Create a dictionary to hold all out variable objects 
    - _add_frame = instance method that add a new label frame. Pass in 
                   label text and optionally a number of columns.

    """

    var_types = {
        FT.string: tk.StringVar,
        FT.string_list: tk.StringVar,
        FT.short_string_list: tk.StringVar,
        FT.iso_date_string: tk.StringVar,
        FT.long_string: tk.StringVar,
        FT.decimal: tk.DoubleVar,
        FT.integer: tk.IntVar,
        FT.boolean: tk.BooleanVar
    }

    def _add_frame(self, label, cols=3):
        frame = ttk.LabelFrame(self, text=label)
        frame.grid(sticky=tk.W + tk.E)
        for i in range(cols):
            frame.columnconfigure(i, weight=1)
        return frame

    def __init__(self, parent, model, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.model = model
        fields = self.model.fields

        self._vars = {  # hold all variable objects
            key: self.var_types[spec['type']]()
            for key, spec in fields.items()
        }

        # disable var for Output field
        self._disable_var = tk.BooleanVar()

        # build the form
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)



        simFrame = self._add_frame(
        'Simulation Control'
        )

        w.LabelInput(
            simFrame, 
            'Number of particles',
            # input_class=ttk.Spinbox,
            field_spec=fields['num_particles'],
            var=self._vars['num_particles'],
            # input_args={`
            #     "from_":2,
            #     "to":100,
            #     "increment":1
            # }`
        ).grid(sticky=tk.E + tk.W, row=0, column=0)

        self._vars['num_particles'].set(20)

        ###########
        # buttons #
        ###########

        # buttons = ttk.Frame(self)  # add on a frame
        # buttons.grid(sticky=tk.W + tk.E, row=4)
        
        # # pass instance methods as callback commands
        self.generatebutton = ttk.Button(
            simFrame, text="Generate", command=self._on_generate)
        # self.generatebutton.pack(side=tk.RIGHT)
        self.generatebutton.grid(sticky=tk.E + tk.W, row=1)

    def _on_generate(self):
        self.event_generate('<<GenerateSim>>')
