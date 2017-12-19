#!/usr/bin/env python3.6

import datetime
import socket

import gi
gi.require_version('Gtk', '3.0')  # noqa: E402
from gi.repository import Gtk

import addressbook_pb2
import common
from common import REQ_TYPES


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
        contacts_view = Gtk.TreeView(contacts_model)
        text_renderer = Gtk.CellRendererText()
        column_labels = [
            'ID', 'Imię i Nazwisko', 'Telefon', 'Email', 'Ostatnio wyświetlony'
        ]
        search_options = [
            'imię i nazwisko', 'email', 'telefon'
        ]
        main_vbox.pack_end(contacts_view, True, True, 5)
        for x in range(len(column_labels)):
            col = Gtk.TreeViewColumn(column_labels[x], text_renderer, text=x)
            contacts_view.append_column(col)
        for x in range(len(search_options)):
            search_combo_box.append_text(search_options[x])
        # 0 -> imię i nazwisko
        search_combo_box.set_active(0)
        contacts_view.get_selection().connect(
            'changed', controller.on_contact_viewed
        )
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
        name = self.contact_name_entry.get_text().encode()
        phone = self.contact_phone_entry.get_text().encode()
        email = self.contact_email_entry.get_text().encode()
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
        find_options = {
            'imię i nazwisko': self.dao.find_contact_by_name,
            'email': self.dao.find_contact_by_email,
            'telefon': self.dao.find_contact_by_phone
        }
        selected = self.window.search_combo_box.get_active_text()
        search_input = self.window.search_entry.get_text()
        find_options[selected](search_input)

    def on_contact_viewed(self, selection):
        """
        Proxy przekazujący id obejrzanego kontaktu.
        Niestety, podłączenie się do sygnału 'changed' wysyłanego przez
        TreeSelection okazało się nie działać, ponieważ po jakiejkolwiek
        zmianie w rekordach (również aktualizacji daty) zaczyna on zwracać
        zupełnie niewłaściwe id w nieprzewidywalny (?) sposób.
        """
        selected_id = self._get_selected_id()
        print(selected_id)
        # self.dao.mark_contact_as_viewed(self._get_selected_id())

    def _get_selected_id(self):
        """Zwraca id aktualnie zaznaczonego kontaktu."""
        model, treeiter = self.window.selection.get_selected()
        if treeiter is None:
            return 'poszedł NoneType'
        return model[treeiter][0]


class MessageSender:
    """
    Interfejs między SQLite a aplikacją, mapuje swoje metody na wyrażenia SQL.
    Wszelkie zapytania do bazy w istocie modyfikują contacts_model,
    który jest wyświetlany na bieżąco przez AddressBookWindow.
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.response_objects = []
        self.contacts_model = Gtk.ListStore(int, str, str, str, str)
        self.find_all_contacts()

    def _send_to_server(self, req_type, request):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((self.host, self.port))
        payload = str(req_type).encode() + request
        self.sock.send(payload)
        # jeśli dodajemy lub kasujemy, odpowiedź nas nie interesuje
        if req_type not in (
            REQ_TYPES.BY_NAME,
            REQ_TYPES.BY_PHONE,
            REQ_TYPES.BY_EMAIL
        ):
            self.sock.close()
            return ''
        data = self.sock.recv(4096)
        self.sock.close()
        return data

    def _fill_response_objects(self, server_response):
        """
        Deserializacja i wrzucenie ContactEntry'ów do self.response_objects.
        """
        print(server_response)
        cont_entr_list = addressbook_pb2.ContactEntryList()
        cont_entr_list.ParseFromString(server_response)
        print(cont_entr_list)
        self.response_objects.clear()
        for cont_entr in cont_entr_list.contact:
            self.response_objects.append(cont_entr)

    def _populate_contacts_model(self):
        """
        Odczytanie wartości ContactEntry'ów w self.response_objects i
        wypełnienie złożonymi z nich krotkami Gtk.ListStore'a.
        """
        self.contacts_model.clear()
        for c in self.response_objects:
            self.contacts_model.append(
                [c.id, c.name, c.phone, c.email, c.last_viewed]
            )

    def find_all_contacts(self):
        self.find_contact_by_name(b'')  # ha!
        self._populate_contacts_model()

    def find_contact_by_name(self, desired_name):
        """Szuka według imienia i nazwiska."""
        req_message = addressbook_pb2.ContactName()
        req_message.name = desired_name
        response = self._send_to_server(REQ_TYPES.BY_NAME, req_message.SerializeToString())
        self._fill_response_objects(response)
        self._populate_contacts_model()

    def find_contact_by_phone(self, desired_phone):
        """Szuka według numeru telefonu."""
        req_message = addressbook_pb2.ContactPhone()
        req_message.phone = desired_phone
        response = self._send_to_server(REQ_TYPES.BY_PHONE, req_message.SerializeToString())
        self._fill_response_objects(response)
        self._populate_contacts_model()

    def find_contact_by_email(self, desired_email):
        """Szuka według adresu emailowego."""
        req_message = addressbook_pb2.ContactEmail()
        req_message.email = desired_email
        response = self._send_to_server(REQ_TYPES.BY_EMAIL, req_message.SerializeToString())
        self._fill_response_objects(response)
        self._populate_contacts_model()

    def update_contact(self, contact_id, contact_name, phone, email):
        """Aktualizuje kontakt o id równym contact_id."""
        req_message = addressbook_pb2.ContactEntry()
        req_message.id = contact_id
        req_message.name = contact_name
        req_message.phone = phone
        req_message.email = email
        req_message.last_viewed = ''  # w sumie nie ma tu większego znaczenia
        self._send_to_server(REQ_TYPES.UPDATE, req_message.SerializeToString())
        self.find_all_contacts()

    def delete_contact(self, contact_id):
        """Usuwa kontakt o wskazanym id."""
        self.find_all_contacts()

    def create_contact(self, contact_name, phone, email):
        """
        Tworzy nowy kontakt. Jego id jest przydzielane automatycznie.
        """
        hereandnow = self._whattimeisit()
        req_message = addressbook_pb2.ContactEntry()
        req_message.name = contact_name
        req_message.phone = phone
        req_message.email = email
        req_message.last_viewed = hereandnow
        self._send_to_server(REQ_TYPES.NEW, req_message.SerializeToString())
        self.find_all_contacts()

    def _whattimeisit(self):
        """
        Zwraca ładnie sformatowaną datę, np: wto 05 gru 2017 19:18:05.
        """
        return datetime.datetime.utcnow().strftime('%a %d %b %Y %H:%M:%S')


if __name__ == '__main__':
    dao = MessageSender(common.HOST, common.PORT)
    controller = AddressBookController(dao)
    window = AddressBookWindow(controller, dao.contacts_model)
    controller.set_window(window)
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    Gtk.main()
