# -*- coding: utf-8 -*-

SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
SECRET_KEY = 'foobar'
DIRECTORY = "tests/openvpn/easy-rsa/keys/"
COMMAND_MAIL = "tests/openvpn/clients/openvpn-mail-key"

CACERT_FILE = '/tmp/ffca.crt'
CAKEY_FILE = '/tmp/ffca.key'
NEWKEY_ALG = 'rsa'
NEWKEY_SIZE = 1024
NEWCERT_COUNTRY = "DE"
NEWCERT_STATE = "Eastern Germany"
NEWCERT_LOCATION = "Berlin"
NEWCERT_ORGANIZATION = "Foerderverein Freie Netzwerke e.V."
NEWCERT_DURATION = 10*365*24*60*60 # 10 years
NEWCERT_COMMENT = b'made for you with PyOpenSSL'
NEWCERT_SIGNDIGEST = "sha1"

