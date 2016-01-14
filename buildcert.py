#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import datetime
from subprocess import call

#from ca import app, db
#from ca.models import Request

from OpenSSL import crypto, SSL
from os.path import exists, join

# taken from https://gist.github.com/ril3y/1165038
def create_cert(cert_name, cert_email):
    """
    If datacard.crt and datacard.key don't exist in cert_dir, create a new
    self-signed cert and keypair and write them into that directory.
    """

    if True:

        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 1024)

        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "DE"
        cert.get_subject().ST = "Eastern Germany"
        cert.get_subject().L = "Berlin"
        cert.get_subject().O = "Foerderverein Freie Netzwerke e.V."
        cert.get_subject().CN = "freifunk_%s" % cert_name
        cert.get_subject().emailAddress = cert_email
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha1')

	print "Certificate generated"
	print crypto.dump_certificate(crypto.FILETYPE_TEXT, cert)
#        open(join(cert_dir, CERT_FILE), "wt").write(
#            crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
#        open(join(cert_dir, KEY_FILE), "wt").write(
#            crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

create_cert('sam0815-test', "freifunk@it-solutions.geroedel.de")

quit(0)

for request in Request.query.filter(Request.generation_date == None).all():  # noqa
    prompt = "Do you want to generate a certificate for {}, {} ?"
    print(prompt.format(request.id, request.email))
    print("Type y to continue")
    confirm = input('>')
    if confirm in ['Y', 'y']:
        print('generating certificate')
        call([app.config['COMMAND_BUILD'], request.id, request.email])
        call([app.config['COMMAND_MAIL'], request.id, request.email])
        request.generation_date = datetime.date.today()
        db.session.commit()
        print()
    else:
        print('skipping generation \n')
