#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask_mail import Message

from ca import app, db, mail
from ca.models import Request

import datetime
from subprocess import call
from os.path import exists, join

from OpenSSL import crypto, SSL
import tarfile


migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

requests_subcommands = Manager(usage="Handle certificate requests")
manager.add_command('requests', requests_subcommands)

certificates_subcommands = Manager(usage="Handle existing certificates")
manager.add_command('certificates', certificates_subcommands)


def mail_certificate(id, email):
    cert_createTar(id)
    with app.app_context():
        msg = Message(
                app.config['MAIL_SUBJECT'],
                sender=app.config['MAIL_FROM'],
                recipients=[email]
                )
        msg.body = render_template('mail.txt')
        certificate_path = "{}/freifunk_{}.tgz".format(
                app.config['DIRECTORY_CLIENTS'],
                id
                )
        with app.open_resource(certificate_path) as fp:
            msg.attach(
                    "freifunk_{}.tgz".format(id),
                    "application/gzip",
                    fp.read()
                    )
        mail.send(msg)


@requests_subcommands.command
def process():
    "Process new certificate requests"
    for request in Request.query.filter(Request.generation_date == None).all():  # noqa
        prompt = "Do you want to generate a certificate for {}, {} ?"
        print(prompt.format(request.id, request.email))
        print("Type y to continue")
        confirm = input('>')
        if confirm in ['Y', 'y']:
            print('generating key')
            new_key = create_key()
            print('generating certificate')
            new_cert_sn = Request.getMaxCertSn() + 1
            request.cert_sn = new_cert_sn
            new_cert = create_cert(request.id, request.email, request.cert_sn, new_key)
            cert_store(request.id, new_key, new_cert)
            print (crypto.dump_certificate(crypto.FILETYPE_TEXT, new_cert))
            mail_certificate(request.id, request.email)
#            request.generation_date = datetime.date.today()
            db.session.commit()
            print()
        else:
            print('skipping generation \n')


@requests_subcommands.command
def show():
    "Show new certificate requests"
    for request in Request.query.filter(Request.generation_date == None).all():  # noqa
        prompt = "ID: {} - Email: {}"
        print(prompt.format(request.id, request.email))


@certificates_subcommands.command
def send():
    "Send existing certificate again"
    print("Which existing certificate do you want to send again? Type the ID")
    send_again_id = input('>')
    print("Where should it be sent? Please type the Email")
    send_again_mail = input('>')
    try:
        mail_certificate(send_again_id, send_again_mail)
        print("OK")
    except:
        print("That didn't work.")


@certificates_subcommands.command
def show():
    "Show already existing certificates"
    for request in Request.query.filter(Request.generation_date != None).all():  # noqa
        prompt = "ID: {} - Email: {}"
        print(prompt.format(request.id, request.email))


# taken from https://gist.github.com/ril3y/1165038
def create_cert(cert_name, cert_email, cert_sn, cert_key):
    """
    If datacard.crt and datacard.key don't exist in cert_dir, create a new
    self-signed cert and keypair and write them into that directory.
    """

    # get required CA-data
    ca_cert_file = open(app.config['CACERT_FILE'], 'r')
    ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_cert_file.read())
    ca_key_file = open(app.config['CAKEY_FILE'], 'r')
    ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, ca_key_file.read())

    if True:

        # create a new cert
        cert = crypto.X509()
        cert.set_version(0x02)  # X509-Version 3
        cert.get_subject().C = app.config['NEWCERT_COUNTRY']
        cert.get_subject().ST = app.config['NEWCERT_STATE']
        cert.get_subject().L = app.config['NEWCERT_LOCATION']
        cert.get_subject().O = app.config['NEWCERT_ORGANIZATION']
        cert.get_subject().CN = "freifunk_%s" % cert_name
        cert.get_subject().emailAddress = cert_email
        cert.set_serial_number(cert_sn)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(app.config['NEWCERT_DURATION'])
        cert.set_issuer(ca_cert.get_subject())
        cert.set_pubkey(cert_key)

        # create cert extensions
        # as Python 3 uses unicode-strings we have to froce them to byte-strings
        #  https://github.com/pyca/pyopenssl/issues/15
        cert_ext = [
            crypto.X509Extension(b'basicConstraints', False, b"CA:FALSE"),
            crypto.X509Extension(b'nsComment', False, app.config['NEWCERT_COMMENT']),
            crypto.X509Extension(b'subjectKeyIdentifier', False, b'hash', subject=cert),
            crypto.X509Extension(b'authorityKeyIdentifier', False, b'keyid:always,issuer:always', issuer=ca_cert),
            crypto.X509Extension(b'extendedKeyUsage', False, b'TLS Web Client Authentication'),
            crypto.X509Extension(b'keyUsage', False, b'Digital Signature'),
        ]
        cert.add_extensions(cert_ext)

        cert.sign(ca_key, app.config['NEWCERT_SIGNDIGEST'])

        return (cert)


def create_key():
    """Create a key-pair as per config"""
    # create a key pair
    k = crypto.PKey()
    if app.config['NEWKEY_ALG'].lower() == 'rsa':
        keytype = crypto.TYPE_RSA
    elif app.config['NEWKEY_ALG'].lower() == 'dsa':
        keytype = crypto.TYPE_DSA
    k.generate_key(keytype, app.config['NEWKEY_SIZE'])
    # crypto.dump_privatekey(crypto.FILETYPE_PEM, k)
    return (k)


def cert_store(certid, keydata, certdata):
    keyfile = open(join(app.config['DIRECTORY'], 'freifunk_%s.key' % certid) ,'wb')
    keyfile.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, keydata))
    keyfile.close()
    certfile = open(join(app.config['DIRECTORY'], 'freifunk_%s.crt' % certid) ,'wb')
    certfile.write(crypto.dump_certificate(crypto.FILETYPE_PEM, certdata))
    certfile.close()


def cert_createTar(certid):
    """
    create a tar-archive with the default-config and users certificate
    """
    certtar = tarfile.open(join(app.config['DIRECTORY_CLIENTS'], 'freifunk_%s.tgz' %certid), 'w:gz')
    certtar.add(join(app.config['DIRECTORY'], 'freifunk_%s.key' % certid), ('freifunk_%s.key' % certid))
    certtar.add(join(app.config['DIRECTORY'], 'freifunk_%s.crt' % certid), ('freifunk_%s.crt' % certid))
    for templatefile in os.listdir('ca/templates/vpn03-files'):
        certtar.add(join('ca/templates/vpn03-files', templatefile), templatefile)
    certtar.close()


if __name__ == '__main__':
    manager.run()
