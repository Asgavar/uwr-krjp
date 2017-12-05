#!/usr/bin/env python3.6

import sqlite3

import gi
gi.require_version('Gtk', '3.0')  # noqa: E402
from gi.repository import Gtk


class AddressBookWindow(Gtk.Window):
    """
    Deklaruje, inicjalizuje i robi różne rzeczy z interfejsem w GTK+3.
    Otrzymuje też referencję do kontrolera i modelu zawierającego kontakty.
    """
    def __init__(self, controller, contacts_model):
        Gtk.Window.__init__(self, title='Książka Adresowa')
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
        # ustawianie callbacków
        new_contact_button.connect(
            'clicked', controller.on_new_contact_button_clicked
        )
        edit_contact_button.connect(
            'clicked', controller.on_edit_contact_button_clicked
        )
        search_button.connect(
            'clicked', controller.on_search_button_clicked
        )
        # przydadzą się później
        self.search_entry = search_entry
        self.search_combo_box = search_combo_box
        self.selection = contacts_view.get_selection()
        self.add(main_vbox)


class ContactFormWindow(Gtk.Window):
    """
    W zależności od parametru intention może być zarówno formularzem edycji,
    jak i tworzenia kontaktu. Nie ma kontrolera, sam komunikuje się z dao.
    """
    def on_confirm_button_clicked(self, button):
        """Sprawdza, jaka była intencja i robi odpowiednią rzecz."""
        create_contact_sql = ''
        edit_contact_sql = ''
        if self.intention == 'create':
            print('tworzę...')
        elif self.intention == 'edit':
            print('zmieniam...')

    def __init__(self, dao, intention):
        """Parametr intention to 'create' lub 'edit'."""
        self.dao = dao
        self.intention = intention
        Gtk.Window.__init__(self)
        main_vbox = Gtk.VBox(margin=5, spacing=5)
        contact_name_label = Gtk.Label('Imię i Nazwisko')
        contact_phone_label = Gtk.Label('Telefon')
        contact_email_label = Gtk.Label('Email')
        contact_name_entry = Gtk.Entry()
        contact_phone_entry = Gtk.Entry()
        contact_email_entry = Gtk.Entry()
        contact_name_entry.set_max_width_chars(10)
        contact_name_entry.set_max_length(10)
        main_vbox.pack_start(contact_name_label, False, True, 0)
        main_vbox.pack_start(contact_name_entry, False, True, 0)
        main_vbox.pack_start(contact_phone_label, False, True, 0)
        main_vbox.pack_start(contact_phone_entry, False, True, 0)
        main_vbox.pack_start(contact_email_label, False, True, 0)
        main_vbox.pack_start(contact_email_entry, False, True, 0)
        confirm_button = Gtk.Button('Potwierdź')
        main_vbox.pack_end(confirm_button, False, True, 0)
        self.add(main_vbox)


class AddressBookController:
    """
    Zawiera callbacki przypisane do poszczególnych elementów GUI, pośredniczy
    między tym, co widoczne na ekranie a interfejsem do bazy.
    """
    def __init__(self, dao):
        self.dao = dao

    def set_window(self, window):
        """Jeden prosty trik by rozwiązać problem circular dependency."""
        self.window = window

    def on_new_contact_button_clicked(self, button):
        """Wyświetla popupa z formularzem dodania."""
        print('new contact button')
        popup = ContactFormWindow(self.dao, 'create')
        popup.show_all()

    def on_edit_contact_button_clicked(self, button):
        """Ściąga id obecnie zaznaczonego kontaktu i odpala popupa edycji."""
        print('edit contact button')
        model, treeiter = self.window.selection.get_selected()
        popup = ContactFormWindow(self.dao, 'edit')
        popup.show_all()
        print(model[treeiter][0])

    def on_search_button_clicked(self, button):
        """Ściąga z ComboBoxa pole, według którego wyszukujemy."""
        print('search button')


class DataAccess:
    """
    Interfejs między SQLite a aplikacją, mapuje swoje metody na wyrażenia SQL.
    Wszelkie zapytania do bazy w istocie modyfikują contacts_model,
    który jest wyświetlany na bieżąco przez AddressBookWindow.
    """
    def __init__(self, db_file):
        """
        Tworzenie tabeli i modelu.
        Początkowe wypełnienie modelu danymi.
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
        # FIXME
        self.create_contact(1, 1, 1, 1)
        self.find_all_contacts()

    def find_all_contacts(self):
        """Zwraca wszystkie kontakty w bazie."""
        self.cr.execute(
            'SELECT * FROM Contacts;'
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
                    NULL,
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
    dao = DataAccess('adresy_test.db')
    controller = AddressBookController(dao)
    window = AddressBookWindow(controller, dao.contacts_model)
    controller.set_window(window)
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    Gtk.main()
