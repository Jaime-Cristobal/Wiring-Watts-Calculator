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


def write_auto_col_sizing(exc_sheet, col, col_name, style, text_offset=0):
    """
    Auto sizes the column width on excel depending on the character length
    and offset given.

    :param exc_sheet: the workbook used by xlwt
    :param col: index of which column we are auto sizing
    :param col_name: the character text we are input in the col value
    :param style: changes things such as font, alignment, cell colour, etc.
    :param text_offset: offset to increase the width if auto sizing based on
                        character length is not satisfactory.
    """
    exc_sheet.write(0, col, col_name, style=style)
    exc_sheet.col(col).width = 256 * (len(col_name) + text_offset)


def main():
    total_system_amount = 25
    amount = 16
    amnt_of_panels, power = calc_pow(total_system_amount, 289.3, 0.97)
    breaker_curr, ocpd, cont_curr = calc_current(amount)

    # try to take this from another excel or json file
    cities = {"Moreno Valley": 117, "San Bernardino": 117, "Fontana": 117, "Riverside": 117,
              "Ontario": 117, "Perris": 114, "Banning": 114, "Hemet": 116, "Beaumont": 114,
              "Hesperia": 116, "Victorville": 116, "Yucca Valley": 123, "Indio": 123,
              "Palm Desert": 123, "Desert Hot Springs": 123, "Palm Springs": 123,
              "Menifee": 114}
    cities_calc = {}

    for city, temp in cities.items():
        wires, conductor, recc_breaker, awg = wire_calc(temp, ocpd, breaker_curr, cont_curr)
        cities_calc[city + " (" + str(temp) + "°)"] = [awg, wires, conductor, recc_breaker]

    wb = xlwt.Workbook()

    # horizontal style
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    horz_style = xlwt.XFStyle()
    horz_style.alignment = alignment

    # normal bold title style
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    style.font = font
    style.alignment = alignment

    # color style
    div_style = xlwt.XFStyle()
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = xlwt.Style.colour_map['black']
    div_style.pattern = pattern

    exc_sheet = wb.add_sheet("Power Rating")

    write_auto_col_sizing(exc_sheet, 0, "Panel Amount", style=style, text_offset=2)
    write_auto_col_sizing(exc_sheet, 1, "Power Rating (kW)", style=style, text_offset=2)
    write_auto_col_sizing(exc_sheet, 2, "OCPD (A)", style=style, text_offset=2)
    write_auto_col_sizing(exc_sheet, 3, "Breaker Size (A)", style=style, text_offset=2)
    write_auto_col_sizing(exc_sheet, 4, "Continuous Current (A)", style=style, text_offset=2)
    write_auto_col_sizing(exc_sheet, 6, " ", style=div_style, text_offset=0)

    for total_panel, net_pow in zip(amnt_of_panels, power):
        exc_sheet.write(total_panel, 0, total_panel, style=style)
        exc_sheet.write(total_panel, 1, net_pow, style=horz_style)

    for array_panels, brk_c, ocpd_s, cont_c in zip(range(1, amount + 1), breaker_curr, ocpd, cont_curr):
        exc_sheet.write(array_panels, 2, brk_c, style=horz_style)
        exc_sheet.write(array_panels, 3, ocpd_s, style=horz_style)
        exc_sheet.write(array_panels, 4, cont_c, style=horz_style)
        exc_sheet.write(array_panels, 6, " ", style=div_style)

    idx = 7
    for city, list_c in cities_calc.items():
        write_auto_col_sizing(exc_sheet, idx + 1, city, style)
        write_auto_col_sizing(exc_sheet, idx + 2, "Wire (AWG)", style, text_offset=2)
        write_auto_col_sizing(exc_sheet, idx + 3, "Conductor (A)", style, text_offset=2)
        write_auto_col_sizing(exc_sheet, idx + 4, "Temp. Factor", style, text_offset=2)
        write_auto_col_sizing(exc_sheet, idx + 5, "Recc. Breaker(A)", style, text_offset=3)

        # list[0] - AWG wire used
        # list[1] -
        for panels, wire, cond, temp_fact, brker in zip(range(1, len(amnt_of_panels) + 1),
                                             list_c[0], list_c[1], list_c[2], list_c[3]):
            exc_sheet.write(panels, idx + 1, panels, style=style)
            exc_sheet.write(panels, idx + 2, wire, style=horz_style)
            exc_sheet.write(panels, idx + 3, cond, style=horz_style)
            exc_sheet.write(panels, idx + 4, temp_fact, style=horz_style)
            exc_sheet.write(panels, idx + 5, brker, style=horz_style)
        idx += 7

    wb.save("Power_Rating_Table.xls")


if __name__ == "__main__":
    main()
