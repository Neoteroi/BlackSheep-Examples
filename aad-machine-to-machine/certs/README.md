# Example with cliet credential flow using a certificate

This folder contains an utility script that can be used to generate certificates
for app registrations in Azure Active Directory.

It is for Bash (it should work also in the Git Bash for Windows).
Example usage:

```bash
# Examples:
NAME=foo ./create-cert.sh

# With subject:
NAME=example SUBJECT="/C=IT/ST=TO/L=TO/O=E/OU=Example Team/CN=example.com" ./create-cert.sh

# With password for PFX:
NAME=example SUBJECT="/C=IT/ST=TO/L=TO/O=E/OU=Example Team/CN=example.com" PFX_PASS=FooFoo ./create-cert.sh
```
