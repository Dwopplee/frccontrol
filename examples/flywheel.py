#!/usr/bin/env python3

# Avoid needing display if plots aren't being shown
import sys

if "--noninteractive" in sys.argv:
    import matplotlib as mpl

    mpl.use("svg")

import frccontrol as frccnt
import math
import matplotlib.pyplot as plt
import numpy as np


class Flywheel(frccnt.System):
    def __init__(self, dt):
        """Flywheel subsystem.

        Keyword arguments:
        dt -- time between model/controller updates
        """
        state_labels = [("Angular velocity", "rad/s")]
        u_labels = [("Voltage", "V")]
        self.set_plot_labels(state_labels, u_labels)

        # Number of motors
        self.num_motors = 1.0
        # Flywheel moment of inertia in kg-m^2
        self.J = 0.00032
        # Gear ratio
        self.G = 12.0 / 18.0

        self.model = frccnt.models.flywheel(
            frccnt.models.MOTOR_775PRO, self.num_motors, self.J, self.G
        )
        frccnt.System.__init__(self, self.model, -12.0, 12.0, dt)

        q = [9.42]
        r = [12.0]
        self.design_dlqr_controller(q, r)
        # self.place_controller_poles([0.87])
        self.design_two_state_feedforward(q, r)

        q_vel = 1.0
        r_vel = 0.01
        self.design_kalman_filter([q_vel], [r_vel])
        # self.place_observer_poles([0.3])


def main():
    dt = 0.00505
    flywheel = Flywheel(dt)
    flywheel.export_cpp_coeffs("Flywheel", "Subsystems/")

    if "--save-plots" in sys.argv or "--noninteractive" not in sys.argv:
        plt.figure(1)
        flywheel.plot_pzmaps()
    if "--save-plots" in sys.argv:
        plt.savefig("flywheel_pzmaps.svg")

    # Set up graphing
    l0 = 0.1
    l1 = l0 + 5.0
    l2 = l1 + 0.1
    t = np.arange(0, l2 + 5.0, dt)

    refs = []

    # Generate references for simulation
    for i in range(len(t)):
        if t[i] < l0:
            r = np.array([[0]])
        elif t[i] < l1:
            r = np.array([[9000 / 60 * 2 * math.pi]])
        else:
            r = np.array([[0]])
        refs.append(r)

    if "--save-plots" in sys.argv or "--noninteractive" not in sys.argv:
        plt.figure(2)
        state_rec, ref_rec, u_rec = flywheel.generate_time_responses(t, refs)
        flywheel.plot_time_responses(t, state_rec, ref_rec, u_rec)
    if "--save-plots" in sys.argv:
        plt.savefig("flywheel_response.svg")
    if "--noninteractive" not in sys.argv:
        plt.show()


if __name__ == "__main__":
    main()
