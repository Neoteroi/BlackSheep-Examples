#!/bin/bash

# Use this bash script to create certificates that can be used with
# Azure Active Directory
#
# Examples:
# NAME=foo ./create-cert.sh
#
# With subject:
# NAME=roberto SUBJECT="/C=IT/ST=TO/L=TO/O=E/OU=Example Team/CN=example.com" ./create-cert.sh
#
# With password for PFX:
# NAME=roberto SUBJECT="/C=IT/ST=TO/L=TO/O=E/OU=Example Team/CN=example.com" PFX_PASS=FooFoo ./create-cert.sh
#

source common.sh

if ! command -v openssl; then
    die "openssl is not installed; it is required for this script"
fi

if [ -z "$NAME" ]; then
    die 'missing `NAME`'
fi

if [ -z "$PFX_PASS" ]; then
    print_info "The generated PFX will NOT be password protected"
else
    print_info "The generated PFX will be password protected"
fi

PRIVATE_RSA_NAME=$NAME.pri.pem
PUBLIC_KEY_NAME=$NAME-publickey.cer
PFX_NAME=$NAME-for-aad.pfx

print_info "Generating private RSA key $PRIVATE_RSA_NAME - store this safely!"

# private RSA key
openssl genrsa -out $PRIVATE_RSA_NAME

print_info "Generating public key $PUBLIC_KEY_NAME"

# security certificate (public key) this one will be uploaded to Azure AD app registration

if [ -z "$SUBJECT" ]; then
    # the user will be prompted for subject information;
    # to avoid the prompt, provide with SUBJECT variable
    openssl req -new -x509 -key $PRIVATE_RSA_NAME -out $PUBLIC_KEY_NAME -days 365
else
    openssl req -new -x509 -key $PRIVATE_RSA_NAME -out $PUBLIC_KEY_NAME -days 365 -subj "$SUBJECT"
fi

print_info "Generating PFX certificate $PFX_NAME - store this safely!"

# PFX certificate containing the private key – this must be stored safely and is used to obtain access tokens!
openssl pkcs12 -export -in $PUBLIC_KEY_NAME -inkey $PRIVATE_RSA_NAME -out $PFX_NAME -passin pass: -passout pass:$PFX_PASS
