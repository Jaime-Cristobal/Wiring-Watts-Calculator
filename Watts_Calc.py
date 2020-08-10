"""
This program calculate the AC net power rating and breaker sizes required for
N amount of solar panels placed on a roof.

There are no 3rd-party dependencies required here.
"""
__author__ = "Jaime Cristobal"
__date__ = "8/4/2020"

import enum


"""
These are the ampacities of copper conductor at a temperature rating of 
60, 75, and 90 degrees as specified by the 2002 National Electrical Code (NEC).

The wire sizes only taken into account here are AWG 10, 8, and 6.
"""
class Conductor90(enum.Enum):
    AWG_10 = 40.0
    AWG_8 = 55.0
    AWG_6 = 75.0


class Conductor75(enum.Enum):
    AWG_10 = 35.0
    AWG_8 = 50.0
    AWG_6 = 65.0


class Conductor60(enum.Enum):
    AWG_10 = 30.0
    AWG_8 = 40.0
    AWG_6 = 55.0


def calc_pow(amount):
    """
    Calculates the net total AC rating of the entire solar
    panel system on the roof.

    :param amount: N amount of solar panels

    :returns amnt_of_panels: list of N panels, power - AC power rating
    """
    amnt_of_panels = []
    power = []

    for i in range(0, amount):
        # amount of panels in the system
        panels = i + 1
        amnt_of_panels.append(panels)

        # append net power rating per amount of panels
        total_pow = panels * 301.7 * (97 / 100)
        pow_in_kw = total_pow / 1000
        power.append(float("%.3f" % pow_in_kw))

    return amnt_of_panels, power


def calc_current(amount):
    """
    Calculates the current statistics of a solar array.

    :param amount: N amount of solar panels

    :returns breaker_curr: current that will run to the breaker,
    :returns ocpd: breaker size,
    :returns cont_current: continuous current from modules to main service panel
    """
    breaker_curr = []
    ocpd = []
    cont_curr = []

    for i in range(0, amount):
        # find the breaker size
        panels = i + 1
        b_curr = 1.0 * panels * 1.25
        breaker_curr.append(b_curr)
        if b_curr <= 20:
            ocpd.append(20)
        elif b_curr <= 25:
            ocpd.append(25)
        else:
            ocpd.append(30)

        # find the continuous current: 1.0 x number of panels
        cont_curr.append(panels)

    return breaker_curr, ocpd, cont_curr


def wire_calc(temperature, breaker_size, ocpd, cont_curr):
    """
    Provides wire calculations such as a AWG wire sizes to be used, conductor factor
    rating, temperature factor for the wire, and the recommended breaker to be used
    so the entire house's electrical wiring doesn't blow in case something happens.

    :param temperature: MAX temperature in the area
    :param breaker_size: breaker size as calculated using the OCPD
    :param ocpd: the OCPD current of the array
    :param cont_curr: continuous current of the array
    :return: a set of list of the wire temperature factor rating, conductor factor rating,
             recommended breaker sizes, and wire AWG size used.
    """
    awg = []
    wires_used = []
    conductor_used = []
    recc_breaker = []
    max_temp = temperature + 41         # allow a 41 degrees of allowance from the area's record high

    conductor = 0.82
    if 123 <= max_temp <= 131:
        conductor = 0.76
    elif 132 <= max_temp <= 140:
        conductor = 0.71
    elif 141 <= max_temp <= 158:
        conductor = 0.58
    elif 159 <= max_temp <= 176:
        conductor = 0.41

    derate_awg_10 = float(Conductor90.AWG_10.value) * conductor * 1.0
    derate_awg_8 = float(Conductor90.AWG_8.value) * conductor * 1.0
    derate_awg_6 = float(Conductor90.AWG_6.value) * conductor * 1.0

    for i, j, k in zip(cont_curr, ocpd, breaker_size):
        wire = Conductor90.AWG_10
        #need_new_brkr = False

        # check the derate factor against the continuous, breaker, and OCPD current.
        check_awg_10 = check_awg(derate_awg_10, i, j, k)
        check_awg_8 = check_awg(derate_awg_8, i, j, k)
        check_awg_6 = check_awg(derate_awg_6, i, j, k)
        if check_awg_10:
            awg.append(10)
            wire = Conductor90.AWG_10.value
        elif check_awg_8:
            awg.append(8)
            wire = Conductor90.AWG_8.value
        elif check_awg_6:
            awg.append(6)
            wire = Conductor90.AWG_6.value
        #else: # part of the recommended breaker logic below (WILL NOT BE USED)
        #    need_new_brkr = True

        ### THIS FEATURE WILL NOT USED FOR NOW
        """
        # if the derating factor check failed and could not find a suitable wire, we change the breakers
        if need_new_brkr:
            new_brkr = k + 5

            loop_check = 0
            # find the recommended new breaker
            while True:
                if loop_check >= 5:
                    wire = -99
                    new_brkr = -99
                    break

                new_brkr += 5
                check_awg_10 = check_awg(derate_awg_10, i, j, new_brkr)
                check_awg_8 = check_awg(derate_awg_8, i, j, new_brkr)
                check_awg_6 = check_awg(derate_awg_6, i, j, new_brkr)
                if check_awg_10:
                    wire = Conductor90.AWG_10.value
                elif check_awg_8:
                    wire = Conductor90.AWG_8.value
                elif check_awg_6:
                    wire = Conductor90.AWG_6.value
                loop_check += 1
            recc_breaker.append(new_brkr)
        else:
            recc_breaker.append(k)
        """

        recc_breaker.append(k)
        conductor_used.append(conductor)
        wires_used.append(wire)

    return wires_used, conductor_used, recc_breaker, awg


def check_awg(derate, cont, ocpd, breaker_size):
    return derate > cont and derate > ocpd and derate > breaker_size
