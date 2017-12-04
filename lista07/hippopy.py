#!/usr/bin/env python3.6

import math

import cairo
import gi
gi.require_version('Gtk', '3.0')  # noqa: E402
from gi.repository import Gtk


class HippopyWindow(Gtk.Window):
    """
    Boilerplate inicjalizacji i ustawiania interfejsu.
    """
    def on_draw_button_clicked(self, button):
        """
        Przekazuje zadanie hipopotamowi.
        """
        argvalue = self.argentry.get_text()
        opcode = self.opcodes_dropdown.get_active_text()
        # walidacja inputu
        if not all(d.isdigit() for d in argvalue):
            print('Nieprawidlowy parametr!')
            invalid_input_dialog = Gtk.MessageDialog(
                self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                'Nieprawidlowy parametr!'
            )
            invalid_input_dialog.run()
            invalid_input_dialog.destroy()
            return
        self.opcodes[opcode](float(argvalue))

    def __init__(self):
        Gtk.Window.__init__(self, title='Hippopy: rysujący hipopotam')
        self.set_resizable(False)
        self.hippo = Hippo()
        self.drawingarea = Gtk.DrawingArea()
        self.drawingarea.set_size_request(900, 900)
        self.drawingarea.connect('draw', self.hippo.draw)
        self.opcodes_dropdown = Gtk.ComboBoxText()
        self.argentry = Gtk.Entry()
        self.argentry.set_max_length(3)
        self.argentry.set_width_chars(3)
        self.opcodes = {
            'IDŹ NAPRZÓD': self.hippo._forward,
            'COFNIJ SIĘ': self.hippo._backward,
            'SKRĘĆ W LEWO X STOPNI': self.hippo._left,
            'SKRĘĆ W PRAWO X STOPNI': self.hippo._right,
            'PODNIEŚ PĘDZEL': self.hippo._penup,
            'OPUŚĆ PĘDZEL': self.hippo._pendown
        }
        listbox = Gtk.ListBox()
        row_drawingarea = Gtk.ListBoxRow()
        row_opcode_arg = Gtk.ListBoxRow()
        row_drawingarea.set_selectable(False)
        row_drawingarea.set_activatable(False)
        row_opcode_arg.set_selectable(False)
        row_opcode_arg.set_activatable(False)
        draw_button = Gtk.Button.new_with_label('Rysuj')
        draw_button.connect('clicked', self.on_draw_button_clicked)
        for opc in self.opcodes:
            self.opcodes_dropdown.append(opc, opc)
        self.opcodes_dropdown.set_active(0)
        opcode_arg_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        opcode_arg_hbox.pack_end(draw_button, False, False, 0)
        opcode_arg_hbox.pack_end(self.argentry, False, False, 0)
        opcode_arg_hbox.pack_end(self.opcodes_dropdown, False, True, 0)
        row_drawingarea.add(opcode_arg_hbox)
        row_opcode_arg.add(self.drawingarea)
        listbox.add(row_opcode_arg)
        listbox.add(row_drawingarea)
        self.add(listbox)


class Hippo:
    def __init__(self):
        self.x = 450  # 900/2 = srodek plotna
        self.y = 450
        self.angle = 0
        self.pen_active = True
        self.draw_instructions = []  # lista krotek zawierajacych dwie krotki

    def draw(self, drawingarea, context):
        """
        Callback przy kazdym wywolaniu wykonujacy instrukcje rysowania
        zawarte w liscie self.draw_instructions.
        """
        context.set_line_width(2)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_source_rgb(1, 0, 0)  # czerwony
        for instruction in self.draw_instructions:
            context.move_to(*(instruction[0]))  # startpoint
            context.line_to(*(instruction[1]))  # destination
            context.close_path()
            context.stroke()

    def _forward(self, dist):
        """
        Ruch odbywa sie poprzez stworzenie 'instrukcji ruchu' - dwoch punktow,
        docelowo polaczonych linia i dopisanie jej do listy instrukcji
        wykonywanych przy kazdym rysowaniu okna.
        """
        print(f'ide do przodu o {dist}')
        startpoint = (self.x, self.y)
        angle_in_radians = math.radians(self.angle)
        dest_x = self.x + dist * math.cos(angle_in_radians)
        dest_y = self.y + dist * math.sin(angle_in_radians)
        destination = (dest_x, dest_y)
        # jesli pedzel jest podniesiony, hipopotam po prostu sie przesuwa
        if self.pen_active:
            self.draw_instructions.append((startpoint, destination))
        self.x = dest_x
        self.y = dest_y

    def _backward(self, dist):
        print(f'ide w tyl o {dist}')
        startpoint = (self.x, self.y)
        angle_in_radians = math.radians(self.angle)
        dest_x = self.x - dist * math.cos(angle_in_radians)
        dest_y = self.y - dist * math.sin(angle_in_radians)
        destination = (dest_x, dest_y)
        if self.pen_active:
            self.draw_instructions.append((startpoint, destination))
        self.x = dest_x
        self.y = dest_y

    def _right(self, deg):
        """
        Sterowany przez uzytkownika hipopotam startuje z glowa skierowana
        w prawo i odmierza katy zgodnie ze wskazowkami zegara w stosunku do
        swojej pozycji startowej.
        Dzieki okresowosci funkcji trygonometrycznych nie trzeba przejmowac
        sie przekroczeniem zakresu [0, 360].
        """
        print(f'skrecam w prawo o {deg} stopni')
        self.angle += deg

    def _left(self, deg):
        print(f'skrecam w lewo o {deg} stopni')
        self.angle += 360 - deg

    def _penup(self, aparameterthatdoesnotmatteratall):
        print('podnosze pedzel')
        self.pen_active = False

    def _pendown(self, aparameterthatdoesnotmatteratall):
        print('opuszczam pedzel')
        self.pen_active = True


if __name__ == '__main__':
    window = HippopyWindow()
    window.set_default_size(900, 900)
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    Gtk.main()
