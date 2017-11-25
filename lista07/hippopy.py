#!/usr/bin/env python3.6

import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class HippopyWindow(Gtk.Window):
    def on_draw_button_clicked(self, button):
        # TODO: walidacja inputu
        argvalue = self.argentry.get_text()
        print(argvalue)
        opcode = self.opcodes_dropdown.get_active_text()
        print(opcode)
        self.opcodes[opcode](argvalue)

    def __init__(self):
        Gtk.Window.__init__(self, title='Hippopy: rysujący hipopotam')
        self.hippo = Hippo()
        self.drawingarea = Gtk.DrawingArea()
        self.drawingarea.set_size_request(850, 850)
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
        self.position = (0, 0)
        self.angle = 0
        self.pen_active = True
        self.surface = cairo.SolidPattern(0, 0, 0)

    def draw(self, drawingarea, context):
        """
        'Baza' do rysowania. Zwraca instancje cairo.Context, za pomoca ktorej
        odbywa sie rysowanie.
        """
        # context.set_source_rgb(0.7, 0.2, 0)
        context.set_source(self.surface)
        # ctx.set_line_width(9)
        # ctx.translate(300, 300)
        # ctx.fill()
        x, y, x1, y1 = 0.1, 0.5, 0.4, 0.9
        x2, y2, x3, y3 = 0.6, 0.1, 0.9, 0.5
        context.scale(850, 850)
        context.set_line_width(0.001)
        context.move_to(x, y)
        context.curve_to(x1, y1, x2, y2, x3, y3)
        context.stroke()
        context.set_source_rgba(1, 0.2, 0.2, 0.6)
        context.set_line_width(0.02)
        context.move_to(x, y)
        context.line_to(x1, y1)
        context.move_to(x2, y2)
        context.line_to(x3, y3)
        context.stroke()
        return context

    def _forward(self, dist):
        print(f'ide do przodu o {dist}')

    def _backward(self, dist):
        print(f'ide w tyl o {dist}')

    def _right(self, deg):
        print(f'skrecam w prawo o {deg}')

    def _left(self, deg):
        print(f'skrecam w lewo o {deg}')

    def _penup(self, aparameterthatdoesnotmatteratall):
        print('podnosze pedzel')

    def _pendown(self, aparameterthatdoesnotmatteratall):
        print('opuszczam pedzel')


if __name__ == '__main__':
    window = HippopyWindow()
    window.set_default_size(900, 900)
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    window.drawingarea.show()
    Gtk.main()
