# -*- coding: utf-8 -*-

SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
SECRET_KEY = 'foobar'
DIRECTORY = "tests/openvpn/easy-rsa/keys/"
MAIL_FROM = "no-reply@ca.berlin.freifunk.net"
MAIL_SUBJECT = "Freifunk VPN03 Zugangsdaten"
DIRECTORY_CLIENTS = "/etc/openvpn/clients/"
CACERT_FILE = 'test/ffca.crt'
CAKEY_FILE = 'test/ffca.key'
NEWKEY_ALG = 'rsa'
NEWKEY_SIZE = 1024
NEWCERT_COUNTRY = "DE"
NEWCERT_STATE = "Eastern Germany"
NEWCERT_LOCATION = "Berlin"
NEWCERT_ORGANIZATION = "Foerderverein Freie Netzwerke e.V."
NEWCERT_DURATION = 10*365*24*60*60 # 10 years
NEWCERT_COMMENT = b'made for you with PyOpenSSL'
NEWCERT_SIGNDIGEST = "sha1"
