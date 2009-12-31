================================
Cookie-based HTTP Authentication
================================

.. Use headers in this order #=~-_

:toc: yes
:symrefs: yes
:sortrefs: yes
:compact: yes
:comments: yes
:inline: yes
:subcompact: yes

:author: Thomas Broyer
:contact: t.broyer@ltgt.net

:Abstract:
  Hypertext Transfer Protocol (HTTP) authentication is in little use
  in the public web, where most web sites and applications use an
  HyperText Markup Language (HTML) form for the user to provide his
  credentials, and cookies to maintain the "authenticated" session.

  Most of the time, the HTML form is sent back with a 200 (OK) status
  or as the target of a redirect. This is a problem for
  non-interactive user agents (web crawlers, download tools, etc.)
  that will treat the response as a success. It can even become a
  problem for interactive user agents (browsers) in some situations
  (asynchronous AJAX requests, "save link target as..." feature,
  etc.).

  The HTTP way of communicating a lack of authorization for a
  protected resource is through a 401 (Unauthorized) status. However,
  this requires sending a WWW-Authenticate header in the response.

  This document tries to reconcile the current practice of using HTML
  forms and cookies to authenticate users, and the 401 (Unauthorized)
  status requirement, by specifying the "Cookie" HTTP authentication
  scheme. It also goes beyond using HTML forms by allowing any content
  type to be returned in the 401 (Unauthorized) response body,
  provided that a cookie is used to authorize access to the protected
  resource.

  Finally, a new HTTP status code, 308 (Unauthorized, See Other), is
  also introduced for those cases where a redirection is deemed
  necessary, or at least better than a 401 (Unauthorized).

:date: 2010 Jan

.. note: Editorial Note (To be removed by RFC Editor before
   publication)

   Distribution of this document is unlimited. Please send comments to
   the ietf-http-auth mailing list at ietf-http-auth@osafoundation.org
   which may be joined by sending a message with subject "subscribe"
   to ietf-http-auth-request@osafoundation.org.

   Discussions of the ietf-http-auth mailing list are archived at
   http://lists.osafoundation.org/pipermail/ietf-http-auth/ .

   XML versions, latest edits and the issues list for this document
   are available from http://github.com/tbroyer/http-cookie-auth .


Introduction
############
`Hypertext Transfer Protocol (HTTP)` [RFC2616]_ authentication is in
little use in the public web, where most web sites and applications
use an `HyperText Markup Language (HTML)` [W3C.REC-html401-19991224]_
form for the user to provide his credentials, and cookies [RFC2965]_
to maintain the "authenticated" session.

Most of the time, the HTML form is sent back with a 200 (OK) status or
as the target of a redirect. This is a problem for non-interactive
user agents (web crawlers, download tools, etc.) that will treat the
response as a success. It can even become a problem for interactive
user agents (browsers) in some situations (AJAX requests, "save link
target as..." feature, etc.).

The HTTP way of communicating a lack of authorization for a protected
resource is through a 401 (Unauthorized) status. However, this
requires sending a WWW-Authenticate header in the response.

This document tries to reconcile the current practice of using HTML
forms and cookies to authenticate users, and the 401 (Unauthorized)
status requirement, by specifying the "Cookie" HTTP authentication
scheme. It also goes beyond using HTML forms by allowing any content
type to be returned in the 401 (Unauthorized) response body, provided
that a cookie is used to grant access to the protected resource.

Finally a new HTTP status code, 308 (Unauthorized, See Other), is also
introduced for those cases where a redirection is deemed necessary, or
at least better than a 401 (Unauthorized).

Notation Conventions
####################
The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in [RFC2119]_.

The terminology used here follows and extends that in the HTTP
specification [RFC2616]_.

Goals and Non Goals
###################
TODO: backwards compat with current UAs, easy migration path for web
sites (almost no-op).

Cookie Authentication Scheme
############################
.. Following paragraphs to be re-ordered and probably re-worded too.

The user credentials being passed through cookies, the
``Authorization`` and ``Proxy-Authorization`` request headers are
therefore not used.

The "cookie" authentication scheme cannot be used for proxy
authentication (within the value of a ``Proxy-Authenticate`` response
header) because, as defined in `Section 3.5` of [RFC2965]_: "Proxies
**MUST NOT** introduce ``Set-Cookie2`` (``Cookie``) headers of their
own in proxy responses (requests)".

When the origin server sends a 401 (Unauthorized) response containing
a WWW-Authenticate header with a cookie authentication scheme, the
response body gives instructions on how to create the appropriate
cookies.

.. JRE: probably better not to rely on Set-Cookie2

In most current web sites and web applications, the response body
would be an HTML document containing a form; when the form is
submitted, the server checks the user-provided form-data and upon
validation sends the appropriate ``Set-Cookie2`` response header
fields with a 303 (See Other) response redirecting back to the
protected resource.

The "cookie" authentication scheme is however not limited ot such
scenarios: the response body could be for example an SVG image with an
embedded XForms, or an HTML document with an embedded script that will
compute a hash of user-provided data and set the cookie by script
before reloading the resource, or some specific entity recognized by
the UA, which will authenticate using an out-of-band mechanism and set
the appropriate cookie before re-requesting the protected
resource. This last scenario might be better solved using another
authentication scheme, though this scenario would allow server-side
negotiation of the authentication mechanism using content-negotiation;
instead of the client negotiation traditionally used when sending
multiple ``WWW-Authenticate`` response headers.

Syntax (using the augmented Backus-Naur Form (BNF) defined in `Section
2.1` or [RFC2616]_::

  challenge           =  "Cookie" cookie-challenge

  cookie-challenge    = 1#( realm | [ form-action ] | cookie-name |
			[ secure-cookie-name ] |
                        [ form-username-field-name ] |
                        [ form-password-field-name ] |
                        [auth-param] )

  form-action         = "form-action" "=" <"> URI <">
  URI                 = absolute-URI | ( path-absolute [ "?" query ] )
  cookie-name         = "cookie-name" "=" token
  secure-cookie-name  = "secure-cookie-name" "=" token
  form-username-field-name = "form-username-field-name" "=" token
  form-password-field-name = "form-password-field-name" "=" token

  auth-param     = <defined in `Section 1.2`, [RFC2616]_>
  path-absolute  = <defined in `Section 3.3`, [RFC3986]_>
  quoted-string  = <defined in `Section 2.2`, [RFC2616]_>
  query          = <defined in `Section 3.4`, [RFC3986]_>
  token          = <defined in `Section 2.2`, [RFC2616]_>

.. compound::

  The meanings of the values of the directives used above are as
  follows:

  form-action
    **OPTIONAL**. The value of the *form-action* attribute is the URI
    reference of the resource that will set the cookies used for
    authenticating the user in subsequent requests. The value must
    resolve to an URI reference where the *scheme* part **MUST** be
    "http" or "https", the *authority* part containing no *userinfo*,
    the *host* and *abs_part* parts have the same constraints as the
    *Domain* and *Path* attributes of a ``Set-Cookie2`` response header
    respectively.

  cookie-name
    **REQUIRED**. The value of the *cookie-name* attribute is the name
    of the cookie that is checked by the server to authenticate the
    user; an UA thus could then inform the user this cookie is necessary
    to gain access to the protected resource, and eentually use a
    different, more secure, storage than for other cookies.

  secure-cookie-name
    **OPTIONAL**. In case the application uses a mix of secured and
    unsecured channels, the value of the *secure-cookie-name*
    attribute is the name of the cookie that is checked by the server
    to authenticate the user when the communication uses a secured
    channel, while the cookie named by the *cookie-name* attribute
    will be used for unsecured channel.

  form-username-field-name
    **OPTIONAL**. To be completed.

  form-password-field-name
    **OPTIONAL**. To be completed

  auth-param
    This directive allows for future extensions. Any unrecognized
    directive MUST be ignored.

The applicability of the cookie(s) (its *Domain*, *Port* and *Path*
attributes) defines the protection space.

New status code: 308 Unauthorized, See Other
############################################
TODO

Alternatives
############
* Allow a 401 without ``WWW-Authenticate``. Problem: it doesn't
  communicate the fact that cookies are used for authentication
  (vs. some other header, or as part of the request payload, as
  generally done with SOAP Web Services.

* `User Agent Authentication Forms` [W3C.NOTE-authentform-19990203]_

Acknowledgements
################
Thanks to those who raised the issue to the WHAT Working Group and the
World Wide Web Consortium's HTML WOrking Group; to Ian Hickson for his
summary of the issue and a similar proposed (tied to HTML though).

Many thanks to Julian Reschke for his encouragements and help with
xml2rfc, and to Joe Gregorio for his rst2rfc tool.

IANA Considerations
###################
This memo includes no request to IANA.

Security
########
As with any use of cookies, care should be taken by servers to avoid
cookie spoofing, and clients to prevent unexpected cookie sharing (see
`Section 6` and `Section 7` of [RFC2965]_).

However, using cookies for account information requires that some
additional measures be taken. Using `HTTP Over TLS` [RFC2818]_ or
other means or encrypting the conversation is sufficient to mitigate
most threats, though it requires that some additional measures be
taken, as described in this section.

To mitigate replay attacks (re-used of a sniffed cookie), the value of
the cookie used for authentication **SHOULD NOT** contain the users
credentials but rather a key associated with the authenticated
session, and this key **SHOULD** be renewed (and expired) frequently.

Sensitive information (such as the user's IBAN on an onlin store) and
sensitive actions (such as confirming an order) **SHOULD** only happen
on a secure channel such as `HTTP Over TLS` [RFC2818]_, and protected
with a secure cookie (a cookie with the *Secure* bit set) so that it
cannot be stolen on an unsecured channel.

This document does not specify how credentials are sent to the
*form-action* URL, though care should be taken that those credentials
cannot be sniffed. In the case of an HTML form, the *form-action*
**SHOULD** use a secure channel such as `HTTP Over TLS` [RFC2818]_.

TODO: document how *secure-cookie-name* helps with security by
preventing replay-attacks. The cookie must obviously have the *Secure*
attribute set.

TODO: add some words about CSRF (and find a normative
reference). Mention "logout" as a mean to mitigate CSRF.

Normative References
####################
.. [RFC2119] Bradner, S., "Key words for use in RFCs to Indicate
   Requirement Levels", BCP 14, RFC 2119, March 1997.
.. [RFC2616] 
.. [RFC2617]
.. [RFC2818]
.. [RFC2965]
.. [RFC3986]

Informative References
######################
.. [W3C.REC-html401-19991224]
.. [W3C.NOTE-authentform-19990203]

Examples
########
Most details of request and response headers has been omitted. Assume
that the user agent has no stored cookies.

Simple example (everything goes through TLS)
============================================
#. User Agent -> Server::

     GET /acme/ HTTP/1.1
     Host: www.example.net

#. Server -> User Agent::

     HTTP/1.1 401 Unauthorized
     WWW-Authenticate: Cookie realm="Acme"
	     form-action="/acme/login"
	     cookie-name=ACME_TICKET
     Content-Type: text/html

     <!DOCTYPE html>
     <title>Unauthorized</title>
     <form action=/acme/login method=POST>
     <input type=hidden name=referer value=/acme/ >
     <p><label>Username: <input name=user></label>
     <p><label>Password: <input name=pwd type=password></label>
     <p><button type=submit>Sign in</button>
     <p><a href=/acme/register>Register for an account</a>
     </form>

#. User Agent -> Server::

     POST /acme/login HTTP/1.1
     Host: www.example.net
     Content-Type: application/x-www-form-urlencoded

     referer=%2Facme%2F&user=Aladdin&password=open%20sesame

#. Server -> User Agent::

     HTTP/1.1 303 See Other
     Location: https://www.example.com/acme/
     Set-Cookie: ACME_TICKET="sdf354s5c1s8e1s"; Path="/acme"; Secure

#. User Agent -> Server::

     GET /acme/ HTTP/1.1
     Host: www.example.com
     Cookie: ACME_TICKET="sdf354s5c1s8e1s"

#. Server -> User Agent::

     HTTP/1.1 200 OK

Mixed HTTP/HTTPS example
========================
#. User Agent -> Server (HTTP)::

     GET /acme/ HTTP/1.1
     Host: www.example.com

#. Server -> User Agent::

     HTTP/1.1 401 Unauthorized
     WWW-Authenticate: Cookie realm="Acme"
	     form-action="https://secure.example.com/acme/login"
	     cookie-name=ACME_TICKET
	     secure-cookie-name=ACME_SECURE_TICKET
     Content-Type: text/html

     <!DOCTYPE html>
     <title>Unauthorized</title>
     <form action="https://secure.example.com/acme/login" action=POST>
     <input type=hidden name=referer value="http://www.example.com/acme/">
     <p><label>Username: <input name=user></label>
     <p><label>Password: <input name=pwd type=password></label>
     <p><button type=submit>Sign in</button>
     <p><a href="/acme/register">Register for an account</a>
     </form>

#. User Agent -> Server (HTTPS)::

     POST /acme/login HTTP/1.1
     Host: secure.example.com
     Content-Type: application/x-www-form-urlencoded

     referer=http%3A%2F%2Fwww.example.com%2Facme%2F&user=Aladdin&password=open%20sesame

#. Server -> User Agent::

     HTTP/1.1 303 See Other
     Location: http://www.example.com/acme/
     Set-Cookie: ACME_TICKET=ésdf354s5c1s8e1s"; Path="/acme";
	     Domain=".example.com"
     Set-Cookie: ACME_SECURE_TICKET="drg53d51fd535rg"; Path="/acme";
	     Domain=".example.com"; Secure

#. User Agent -> Server (HTTP)::

     GET /acme/ HTTP/1.1
     Host: www.example.com
     Cookie: ACME_TICKET="sdf354s5c1s8e1s"

#. Server -> User Agent::

     HTTP/1.1 200 OK

#. User Agent -> Server (HTTPS)::

     GET /acme/ HTTP/1.1
     Host: secure.example.com
     Cookie: ACME_SECURE_TICKET=drg53d51fd535rg"

#. Server -> User Agent::

     HTTP/1.1 200 OK

Cross-domain example
====================
TODO: using CSRF and server-to-server communication to achieve
cross-domain single sign-on between sso.some-co.com and
www.some-tm.net.

At some-tm.net, the 401 response body loads a javascript from
sso.some-co.com that sets a *temporary* cookie if already
authenticated, or redirects to sso.some-co.com otherwise. In the
former case, the server validates the temporary cookie by calling
sso.some-co.com and then sets the appropriate cookie to authenticate
the user at some-tm.net. On the latter case, the server then redirects
the browser back to some-tm.net with some token in the URL; this token
is validated the same way as with the temporary cookie and the browser
is then redirected back to the protected resource.

Fallback in case javascript is not available is a <meta refresh> (in a
<noscript>) to redirect the browser to sso.some-co.com. The process is
then similar to JA-SIG Central Authentication Service (CAS).

Or maybe these should be two distinct examples?

And do not forget the "single logout" issue.
