#!/usr/bin/env python3.6

import datetime
import sqlite3

import gi
gi.require_version('Gtk', '3.0')  # noqa: E402
from gi.repository import Gtk


class AddressBookWindow(Gtk.Window):
    """
    Deklaruje, inicjalizuje i robi różne rzeczy z interfejsem w GTK+3.
    Otrzymuje też referencję do 'modelu' zawierającego kontakty.
    """
    def __init__(self, contacts_model):
        Gtk.Window.__init__(self, title='Musiclib')
        main_vbox = Gtk.VBox(margin=5)
        top_hbox = Gtk.HBox(spacing=5)
        search_button = Gtk.Button(label='Szukaj')
        search_entry = Gtk.SearchEntry()
        search_combo_box = Gtk.ComboBoxText()
        new_contact_button = Gtk.Button('Dodaj')
        edit_contact_button = Gtk.Button('Edytuj')
        top_hbox.pack_end(search_button, False, True, 0)
        top_hbox.pack_end(search_entry, False, True, 0)
        top_hbox.pack_end(search_combo_box, False, True, 0)
        top_hbox.pack_start(new_contact_button, False, True, 0)
        top_hbox.pack_start(edit_contact_button, False, True, 0)
        main_vbox.pack_start(top_hbox, False, False, 0)
        # wg konwencji MVC tu chyba jest widok
        contacts_view = Gtk.TreeView(contacts_model)
        text_renderer = Gtk.CellRendererText()
        column_labels = [
            'ID', 'Imię i Nazwisko', 'Telefon', 'Email', 'Ostatnio wyświetlony'
        ]
        for x in range(len(column_labels)):
            col = Gtk.TreeViewColumn(column_labels[x], text_renderer, text=x)
            contacts_view.append_column(col)
        main_vbox.pack_end(contacts_view, True, True, 5)
        self.add(main_vbox)


class DataAccess:
    """
    Interfejs między SQLite a aplikacją, mapuje swoje metody na wyrażenia SQL.
    Wszelkie zapytania do bazy w istocie modyfikują contacts_model,
    który jest wyświetlany na bieżąco przez AddressBookWindow.
    """
    def __init__(self, db_file):
        """
        Tworzenie tabeli i modelu.
        """
        self.connection = sqlite3.connect(db_file)
        self.cr = self.connection.cursor()
        # odpowiednio id, imie & nazwisko, telefon, email i czas ostatniego
        # wyświetlenia, który zamiast być datą lub czasem jest stringiem,
        # bo pygobject ani myśli by zmapować ją na cos GTK+owego
        self.contacts_model = Gtk.ListStore(int, str, str, str, str)
        self.cr.execute(
            '''
            CREATE TABLE IF NOT EXISTS Contacts (
                contact_id integer primary key,
                contact_name text,
                phone text,
                email text,
                last_viewed text
            );
            '''
        )
        self.connection.commit()

    def find_all_contacts(self):
        """Zwraca wszystkie kontakty w bazie."""
        self.cr.execute(
            'SELECT * FROM Users;'
        )
        for contact in self.cr.fetchall():
            self.contacts_model.append(
                # innymi słowy każde z jego pól
                [contact[x] for x in range(len(contact))]
            )

    def find_contact_by_name(self, desired_name):
        """Zwraca kontakty zawierające desired_name w imieniu lub nazwisku."""
        pass

    def update_contact(self, contact_id, contact_name, phone, email):
        """Aktualizuje kontakt o id równym album_id."""
        pass

    def delete_contact(self, contact_id):
        """Usuwa kontakt o wskazanym id."""
        pass

    def create_contact(self, contact_id, contact_name, phone, email):
        """
        Tworzy nowy kontakt. Jego id jest przydzielane automatycznie.
        """
        # TODO
        self.cr.execute(
            '''
                INSERT INTO Contacts VALUES (
                "Wieńczysław Nieszczególny",
                "192-168-024",
                "wieniek@buziaczek.pl",
                "2017-12-04"
                );
            '''
        )
        self.connection.commit()

    def mark_contact_as_viewed(self, contact_id):
        """Zmienia czas ostatniego wyświetlenia danego kontaktu na {teraz}."""
        pass


if __name__ == '__main__':
    dao = DataAccess(':memory:')
    window = AddressBookWindow(dao.contacts_model)
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    Gtk.main()
