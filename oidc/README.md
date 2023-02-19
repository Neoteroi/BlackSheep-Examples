# OIDC Examples
Working examples of OpenID Connect integrations in BlackSheep applications.

---

This repository contains examples of OpenID Connect integration with three
identity providers:

- [Auth0](https://auth0.com)
- [Okta](https://www.okta.com)
- [Azure Active Directory](https://azure.microsoft.com/en-us/products/active-directory)

## Basic examples (id_token only)

The files whose names start with "basic_" are configured to obtain only
an `id_token`. This is useful when the same application that integrates with
OpenID Connect does not need an access token for another API and all it needs
is to _identify_ users. The values in these files describe real applications
configured in tenants owned by the owner of this repository.

App registrations for these examples only need to be configured with authentication
URL `http://localhost:5000/authorization-callback` and enable issuing `id_token`s.

## Running the examples

1. create a Python virtual environment, and activate it
2. install dependencies `pip install -r requirements.txt`
3. run one of the basic examples `python basic_auth0.py`
4. navigate to [http://localhost:5000](http://localhost:5000)
5. click on the sign-in link, follow the instructions to sign-up / sign-in

:warning: these examples only work with `localhost`!!!

### Azure Active Directory

This example can be tested using any Microsoft account, signing-in in the
demo app inside the Azure tenant Neoteroi.

![AAD demo](./docs/aad-demo.png)

After sign-in, the application shows user claims.

![AAD demo claims](./docs/aad-demo-claims.png)

### Auth0

This example can be tested by anyone, since the application in Auth0 enable
creating an account in the Neoteroi account in Auth0.

![Auth0 demo](./docs/auth0-demo.png)

![Auth0 demo with Google](./docs/auth0-demo-with-google.png)

### Okta

This example illustrates navigating to a sign-in page, but cannot be tested
fully because the Okta account is not configured to enable sign-up.

![Okta demo](./docs/okta-demo.png)

## Examples with scopes (id_token and access_token)

The files whose names start with "scopes_" are configured to obtain, together
with an `id_token`, an `access_token` for an API. These require secrets which,
of course, are not exposed in this repository.

App registrations for these examples are slightly more complex, since they
require configuring an API with scopes. Describing these details is beyond the
scope of this repository. For more information on this subject, refer to the
documentation of the identity providers (for example, for [Auth0 here](https://auth0.com/docs/get-started/apis/api-settings))
