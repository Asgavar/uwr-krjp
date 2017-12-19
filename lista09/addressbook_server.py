#!/usr/bin/env python3.6

import socket
import sqlite3

import addressbook_pb2
from common import REQ_TYPES


class MessageReceiver:
    """
    Nasłuchuje na sockecie i czeka na wiadomości. W zależności od typu
    wiadomości którą otrzymał, podejmuje następujące działania:
        ContactEntry <-> Dodaje go do bazy
        ContactID <-> Usuwa z bazy kontakt o danym id
        ContactName, ContactPhone, ContactEmail <-> odsyła wynik wyszukiwania
    """
    def __init__(self, dba, sock):
        self.dba = dba
        self.sock = sock

    def _split_payload(self, payload):
        """
        Wycina nagłówek z requesta.
        """
        req_type = payload[:1]  # dlaczego [0] zwraca inny wynik niż [:1]?
        request = payload[1:]
        return req_type, request

    def _process(self, req_type, req_body):
        """
        Przetwarza request i zwraca coś co należy odesłać z powrotem.
        """
        routing = {
            REQ_TYPES.NEW: self.create_new,
            REQ_TYPES.UPDATE: self.update_contact,
            REQ_TYPES.DELETE: self.delete_by_id,
            REQ_TYPES.BY_NAME: self.get_by_name,
            REQ_TYPES.BY_PHONE: self.get_by_phone,
            REQ_TYPES.BY_EMAIL: self.get_by_email,
        }
        return routing[req_type](req_body)

    def listen_loop(self):
        while True:
            conn, addr = self.sock.accept()
            data = conn.recv(4096)  # załóżmy, że tyle wystarczy
            print(data)
            req_type, req_body = self._split_payload(data)
            print(f'req_type: {req_type}')
            print(f'req_body: {req_body}')
            response = self._process(int(req_type), req_body)
            conn.send(response)
            conn.close()

    def _dump_from_cursor_to_protobuf(self):
        """
        Zwraca aktualną zawartość kursora jako zserializowany ContactEntryList.
        """
        contact_list = addressbook_pb2.ContactEntryList()
        for record in dba.cr.fetchall():
            print(record)
            contact = contact_list.contact.add()
            contact.id = record[0]
            contact.name = record[1]
            contact.phone = record[2]
            contact.email = record[3]
            contact.last_viewed = record[4]
        return contact_list.SerializeToString()

    def create_new(self, request):
        msg = addressbook_pb2.ContactEntry()
        msg.ParseFromString(request)
        new_name = msg.name
        new_phone = msg.phone
        new_email = msg.email
        last_viewed = msg.last_viewed
        self.dba.create_contact(new_name, new_phone, new_email, last_viewed)
        return b''

    def update_contact(self, request):
        msg = addressbook_pb2.ContactEntry()
        msg.ParseFromString(request)
        self.dba.update_contact(msg.id, msg.name, msg.phone, msg.email)
        return b''

    def delete_by_id(self, request):
        msg = addressbook_pb2.ContactName()
        msg.ParseFromString(request)
        self.dba.delete_contact(msg.id)
        return b''

    def get_by_name(self, request):
        print(request)
        msg = addressbook_pb2.ContactName()
        msg.ParseFromString(request)
        desired_name = msg.name
        dba.find_contact_by_name(desired_name)
        response = self._dump_from_cursor_to_protobuf()
        return response

    def get_by_phone(self, request):
        msg = addressbook_pb2.ContactPhone()
        msg.ParseFromString(request)
        print(msg.phone)
        return b''

    def get_by_email(self, request):
        msg = addressbook_pb2.ContactEmail()
        msg.ParseFromString(request)
        print(msg.email)
        return b''


class DatabaseAccess:
    """
    Fizyczny dostęp do bazy danych.
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

    def _wildcard(self, parameter):
        """SQLite'owa składnia wildcardów."""
        return '%' + parameter + '%'

    def find_contact_by_name(self, desired_name):
        """Szuka według imienia i nazwiska."""
        self.cr.execute(
            'select * from Contacts where contact_name like ?',
            (self._wildcard(desired_name),)
        )

    def find_contact_by_phone(self, desired_phone):
        """Szuka według numeru telefonu."""
        self.cr.execute(
            'select * from Contacts where phone like ?',
            (self._wildcard(desired_phone),)
        )

    def find_contact_by_email(self, desired_email):
        """Szuka według adresu emailowego."""
        self.cr.execute(
            'select * from Contacts where email like ?',
            (self._wildcard(desired_email),)
        )

    def update_contact(self, contact_id, contact_name, phone, email):
        """Aktualizuje kontakt o id równym contact_id."""
        self.cr.execute(
            'update Contacts set contact_name=?, phone=?, email=? where contact_id=?',
            (contact_name, phone, email, contact_id)
        )
        self.connection.commit()

    def delete_contact(self, contact_id):
        """Usuwa kontakt o wskazanym id."""
        self.cr.execute(
            'delete from Contacts where contact_id = ?',
            (contact_id,)
        )
        self.connection.commit()

    def create_contact(self, contact_name, phone, email, last_viewed):
        """
        Tworzy nowy kontakt. Jego id jest przydzielane automatycznie.
        """
        # hereandnow = self._whattimeisit()
        self.cr.execute(
            'insert into Contacts values (null, ?, ?, ?, ?);',
            (contact_name, phone, email, last_viewed)
        )
        self.connection.commit()


if __name__ == '__main__':
    dba = DatabaseAccess('addressbook.db')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # recykling socketu
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 9000))
    s.listen()
    receiver = MessageReceiver(dba, s)
    receiver.listen_loop()
