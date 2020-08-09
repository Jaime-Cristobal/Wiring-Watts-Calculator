"""
This program calculate the AC net power rating and breaker sizes required for
N amount of solar panels placed on a roof.

The only dependency needed is xlwt to output an excel file.
Simply go on the terminal or Python command line and invoke the command:
    pip install xlwt
"""
__author__ = "Jaime Cristobal"
__date__ = "8/8/2020"

import xlwt

from Watts_Calc import calc_pow
from Watts_Calc import calc_current
from Watts_Calc import wire_calc


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
