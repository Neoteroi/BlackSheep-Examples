# Example with cliet credential flow using a certificate

This folder contains an utility script that can be used to generate certificates
for app registrations in Azure Active Directory.

It is for Bash (it also works in the Git Bash for Windows, but it requires an
extra variable like explained below).
Example usage:

```bash
# Examples:
NAME=foo ./create-cert.sh

# With subject:
NAME=example SUBJECT="/C=IT/ST=TO/L=TO/O=E/OU=Example Team/CN=example.com" ./create-cert.sh

# With password for PFX:
NAME=example SUBJECT="/C=IT/ST=TO/L=TO/O=E/OU=Example Team/CN=example.com" PFX_PASS=FooFoo ./create-cert.sh
```

When using the Git Bash for Windows, include **MSYS_NO_PATHCONV=1**, like in:

```bash
MSYS_NO_PATHCONV=1 NAME=example SUBJECT="/C=IT/ST=TO/L=TO/O=E/OU=Example Team/CN=example.com" ./create-cert.sh
```
