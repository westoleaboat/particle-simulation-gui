""" collision.py: Particle Simulation

The code is organized in the following classes:

    -BoundText: Text widget with a bound variable
    -LabelInput: Widget containing a label and input together
    -SimForm: Input form for widgets
    -Application: Application root window


Author: Tomas C. 
"""

from collision.application import Application

app = Application()
app.mainloop()


# if __name__ == '__main__':
#     nparticles = 20
#     radii = np.random.random(nparticles)*0.03+0.02
#     styles = {'edgecolor': 'C0', 'linewidth': 2, 'fill': None}
#     sim = Simulation(nparticles, radii, styles)
#     sim.do_animation(save=True, filename='collision.gif')