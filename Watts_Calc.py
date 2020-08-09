"""
This program calculate the AC net power rating and breaker sizes required for
N amount of solar panels placed on a roof.

There are no 3rd-party dependencies required here.
"""
__author__ = "Jaime Cristobal"
__date__ = "8/4/2020"

import enum


"""
These are the mpacities of copper conductor at a temperature rating of 
60, 75, and 90 degrees as specified by the 2002 National Electrical Code (NEC).

The wire sizes only taken into account here are AWG 10, 8, and 6.
"""
class Conductor90(enum.Enum):
    AWG_10 = 40
    AWG_8 = 55
    AWG_6 = 75


class Conductor75(enum.Enum):
    AWG_10 = 35
    AWG_8 = 50
    AWG_6 = 65


class Conductor60(enum.Enum):
    AWG_10 = 30
    AWG_8 = 40
    AWG_6 = 55


def calc_pow(amount):
    """
    Calculates the net total AC rating of the entire solar
    panel system on the roof.

    :param amount - N amount of solar panels

    :returns amnt_of_panels - list of N panels, power - AC power rating
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

    :param amount - N amount of solar panels

    :returns breaker_curr - current that will run to the breaker,
             ocpd - breaker size,
             cont_current - continuous current from modules to main service panel
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


def wire_calc(temperature, ocpd, breaker, cont_curr):
    """

    """
    awg_10 = 40
    awg_8 = 55
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

    derate_awg_10 = awg_10 * conductor * 1.0
    derate_awg_8 = awg_8 * conductor * 1.0

    for i, j, k in zip(cont_curr, breaker, ocpd):
        wire = awg_10
        derate = wire * conductor * 1.0
        need_new_brkr = False

        # check the derate factor against the continuous, breaker, and OCPD current.
        check_awg_10 = True if derate_awg_10 > i and derate_awg_10 > j and derate_awg_10 > k else False
        check_awg_8 = True if derate_awg_8 > i and derate_awg_8 > j and derate_awg_8 > k else False
        print("Temperature " + str(temperature))
        if check_awg_10:
            print(i)
            print("Using AWG 10")
            wire = awg_10
        elif check_awg_8:
            print(i)
            print("Using AWG 8")
            wire = awg_8
        else:
            print("Cont curr: " + str(i) + " Breaker Size: " + str(j) + " OCPD: " + str(k))
            print("Derate 8: " + str(derate_awg_8))
            print("Derate 10: " + str(derate_awg_10))
            print("ERROR")
            need_new_brkr = True

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
                check_awg_10 = True if derate_awg_10 > new_brkr else False
                check_awg_8 = True if derate_awg_8 * 1.0 > new_brkr else False
                if check_awg_10:
                    wire = awg_10
                    break
                elif check_awg_8:
                    wire = awg_8
                    break
                loop_check += 1
            recc_breaker.append(new_brkr)
        else:
        """
        recc_breaker.append(k)

        conductor_used.append(conductor)
        wires_used.append(wire)

    return wires_used, conductor_used, recc_breaker
