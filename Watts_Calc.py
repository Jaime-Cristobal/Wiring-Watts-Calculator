"""
This program calculate the AC net power rating and breaker sizes required for
N amount of solar panels placed on a roof.

The only dependency needed is xlwt to output an excel file.
Simply go on the terminal or Python command line and invoke the command:
    pip install xlwt
"""
__author__ = "Jaime Cristobal"
__date__ = "8/4/2020"

import xlwt


"""
Calculates the net total AC rating of the entire solar 
panel system on the roof.

:param amount - N amount of solar panels

:returns amnt_of_panels - list of N panels, power - AC power rating
"""
def calc_pow(amount):
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


"""
Calculates the current statistics of a solar array.

:param amount - N amount of solar panels

:returns breaker_curr - current that will run to the breaker,
         ocpd - breaker size,
         cont_current - continuous current from modules to main service panel
"""
def calc_current(amount):
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


"""

"""
def wire_calc(temperature, ocpd, breaker, cont_curr):
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

    for i, j, k in zip(cont_curr, breaker, ocpd):
        wire = awg_10
        derate = wire * conductor * 1.0
        need_new_brkr = False

        derate_awg_10 = awg_10 * conductor * 1.0
        derate_awg_8 = awg_8 * conductor * 1.0

        # check the derate factor against the continuous, breaker, and OCPD current.
        check_awg_10 = True if derate_awg_10 > i and derate_awg_10 > j and derate_awg_10 > k else False
        check_awg_8 = True if derate_awg_8 > i and derate_awg_8 > j and derate_awg_8 > k else False
        if check_awg_10:
            wire = awg_10
        elif check_awg_8:
            wire = awg_8
        else:
            need_new_brkr = True

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
            recc_breaker.append(k)

        conductor_used.append(conductor)
        wires_used.append(wire)

    return wires_used, conductor_used, recc_breaker


def main():
    amount = 22
    amnt_of_panels, power = calc_pow(amount)
    breaker_curr, ocpd, cont_curr = calc_current(amount)

    cities = {"Moreno Valley": 117, "San Bernardino": 117, "Fontana": 117, "Desert Hot Springs": 123}
    cities_calc = {}

    for city, temp in cities.items():
        wires, conductor, recc_breaker = wire_calc(temp, ocpd, breaker_curr, cont_curr)
        cities_calc[city] = [wires, conductor, recc_breaker]

    wb = xlwt.Workbook()

    # horizontal style
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_RIGHT
    horz_style = xlwt.XFStyle()
    horz_style.alignment = alignment

    # normal style
    style = xlwt.XFStyle()

    # font
    font = xlwt.Font()
    font.bold = True
    style.font = font
    style.alignment = alignment

    exc_sheet = wb.add_sheet("Power Rating")

    exc_sheet.write(0, 0, "Panel Amount", style=style)
    exc_sheet.write(0, 1, "Power Rating (kW)", style=style)
    exc_sheet.write(0, 2, "OCPD (A)", style=style)
    exc_sheet.write(0, 3, "Breaker Size (A)", style=style)
    exc_sheet.write(0, 4, "Continuous Current (A)", style=style)

    for panels, net_pow, brk_c, ocpd_s, cont_c in zip(amnt_of_panels, power, breaker_curr, ocpd, cont_curr):
        exc_sheet.write(panels, 0, panels, style=style)
        exc_sheet.write(panels, 1, net_pow, style=horz_style)
        exc_sheet.write(panels, 2, brk_c, style=horz_style)
        exc_sheet.write(panels, 3, ocpd_s, style=horz_style)
        exc_sheet.write(panels, 4, cont_c, style=horz_style)

    idx = 5
    panel = 0
    for city, list in cities_calc.items():
        exc_sheet.write(0, idx, city, style=style)
        for panels, wire, cond, brker in zip(range(1, len(amnt_of_panels) + 1), list[0], list[1], list[2]):
            exc_sheet.write(panels, idx, wire, style=horz_style)
            exc_sheet.write(panels, idx + 1, cond, style=horz_style)
            exc_sheet.write(panels, idx + 2, brker, style=horz_style)

        idx += 3

    wb.save("Power_Rating_Table.xls")


if __name__ == "__main__":
    main()
