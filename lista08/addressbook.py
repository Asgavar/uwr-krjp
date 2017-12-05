#!/usr/bin/env python3.6

import datetime
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
        delete_contact_button = Gtk.Button('Usuń')
        top_hbox.pack_end(search_button, False, True, 0)
        top_hbox.pack_end(search_entry, False, True, 0)
        top_hbox.pack_end(search_combo_box, False, True, 0)
        top_hbox.pack_start(new_contact_button, False, True, 0)
        top_hbox.pack_start(edit_contact_button, False, True, 0)
        top_hbox.pack_start(delete_contact_button, False, True, 0)
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
        delete_contact_button.connect(
            'clicked', controller.on_delete_contact_button_clicked
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
        name = self.contact_name_entry.get_text()
        phone = self.contact_phone_entry.get_text()
        email = self.contact_email_entry.get_text()
        if self.intention == 'create':
            dao.create_contact(name, phone, email)
        elif self.intention == 'edit':
            dao.update_contact(self.selected_id, name, phone, email)
        self.destroy()

    def __init__(self, dao, intention, id_or_noid):
        """
        Parametr intention to 'create' lub 'edit'.
        Parametr id_or_noid może istnieć lub nie istnieć, zależnie od tego,
        czy chcemy zaktualizować istniejący rekord czy tylko stworzyć nowy.
        """
        self.dao = dao
        self.intention = intention
        self.selected_id = id_or_noid
        Gtk.Window.__init__(self)
        main_vbox = Gtk.VBox(margin=5, spacing=5)
        contact_name_label = Gtk.Label('Imię i Nazwisko')
        contact_phone_label = Gtk.Label('Telefon')
        contact_email_label = Gtk.Label('Email')
        contact_name_entry = Gtk.Entry()
        contact_phone_entry = Gtk.Entry()
        contact_email_entry = Gtk.Entry()
        main_vbox.pack_start(contact_name_label, False, True, 0)
        main_vbox.pack_start(contact_name_entry, False, True, 0)
        main_vbox.pack_start(contact_phone_label, False, True, 0)
        main_vbox.pack_start(contact_phone_entry, False, True, 0)
        main_vbox.pack_start(contact_email_label, False, True, 0)
        main_vbox.pack_start(contact_email_entry, False, True, 0)
        confirm_button = Gtk.Button('Potwierdź')
        confirm_button.connect('clicked', self.on_confirm_button_clicked)
        main_vbox.pack_end(confirm_button, False, True, 0)
        self.contact_name_entry = contact_name_entry
        self.contact_phone_entry = contact_phone_entry
        self.contact_email_entry = contact_email_entry
        self.add(main_vbox)


class AddressBookController:
    """
    Zawiera callbacki przypisane do poszczególnych elementów GUI, pośredniczy
    między tym, co widoczne na ekranie a interfejsem do bazy.
    """
    def __init__(self, dao):
        self.dao = dao

    def set_window(self, window):
        """Przerywa błędne koło zależności."""
        self.window = window

    def on_new_contact_button_clicked(self, button):
        """Wyświetla popupa z formularzem dodania."""
        # w tym przypadku 1337 jest tożsame z 'id jest zbędne'
        popup = ContactFormWindow(self.dao, 'create', 1337)
        popup.show_all()

    def on_edit_contact_button_clicked(self, button):
        """Ściąga id obecnie zaznaczonego kontaktu i odpala popupa edycji."""
        selected_id = self._get_selected_id()
        popup = ContactFormWindow(self.dao, 'edit', selected_id)
        popup.show_all()

    def on_delete_contact_button_clicked(self, button):
        """Za pomocą self.dao usuwa wybrany kontakt."""
        selected_id = self._get_selected_id()
        self.dao.delete_contact(selected_id)

    def on_search_button_clicked(self, button):
        """Ściąga z ComboBoxa pole, według którego wyszukujemy i szuka."""
        print('search button')

    def _get_selected_id(self):
        """Zwraca id aktualnie zaznaczonego kontaktu."""
        model, treeiter = self.window.selection.get_selected()
        return model[treeiter][0]


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
            create table if not exists Contacts (
                contact_id integer primary key,
                contact_name text,
                phone text,
                email text,
                last_viewed text
            );
            '''
        )
        self.connection.commit()
        self.find_all_contacts()

    def _populate_contacts_model(self):
        """
        Umieszcza wyniki czekające w kursorze na liście self.contacts_model,
        uprzednio ją czyszcząc.
        """
        self.contacts_model.clear()
        for contact in self.cr.fetchall():
            self.contacts_model.append(
                # innymi słowy każde z jego pól
                [contact[x] for x in range(len(contact))]
            )

    def find_all_contacts(self):
        """
        Aktualizuje listę-model wpisując do niego wszystkie kontakty w bazie.
        """
        self.cr.execute(
            'select * from Contacts;'
        )
        self._populate_contacts_model()

    def find_contact_by_name(self, desired_name):
        """Szuka według imienia i nazwiska."""
        self.cr.execute(
            'select * from Contacts where contact_name like %?%',
            (desired_name,)
        )

    def find_contact_by_phone(self, desired_phone):
        """Szuka według numeru telefonu."""
        self.cr.execute(
            'select * from Contacts where phone like %?%',
            (desired_phone,)
        )

    def find_contact_by_email(self, desired_email):
        """Szuka według adresu emailowego."""
        self.cr.execute(
            'select * from Contacts where email like %?%',
            (desired_email,)
        )

    def update_contact(self, contact_id, contact_name, phone, email):
        """Aktualizuje kontakt o id równym contact_id."""
        self.cr.execute(
            'update Contacts set contact_name=?, phone=?, email=? where contact_id=?',
            (contact_name, phone, email, contact_id)
        )
        self.connection.commit()
        self.find_all_contacts()

    def delete_contact(self, contact_id):
        """Usuwa kontakt o wskazanym id."""
        self.cr.execute(
            'delete from Contacts where contact_id = ?',
            (contact_id,)
        )
        self.connection.commit()
        self.find_all_contacts()

    def create_contact(self, contact_name, phone, email):
        """
        Tworzy nowy kontakt. Jego id jest przydzielane automatycznie.
        """
        hereandnow = self._whattimeisit()
        self.cr.execute(
            'insert into Contacts values (null, ?, ?, ?, ?);',
            (contact_name, phone, email, hereandnow)
        )
        self.connection.commit()
        self.find_all_contacts()

    def mark_contact_as_viewed(self, contact_id):
        """Zmienia czas ostatniego wyświetlenia danego kontaktu na <teraz>."""
        hereandnow = self._whattimeisit()
        self.cr.execute(
            'update Contacts set last_viewed ? where contact_id = ?;',
            (hereandnow, contact_id)
        )
        self.connection.commit()
        self.find_all_contacts()

    def _whattimeisit(self):
        """
        Zwraca ładnie sformatowaną datę, np: wto 05 gru 2017 19:18:05.
        """
        return datetime.datetime.utcnow().strftime('%a %d %b %Y %H:%M:%S')


if __name__ == '__main__':
    dao = DataAccess('adresy_test.db')
    controller = AddressBookController(dao)
    window = AddressBookWindow(controller, dao.contacts_model)
    controller.set_window(window)
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    Gtk.main()
    dao.connection.close()
