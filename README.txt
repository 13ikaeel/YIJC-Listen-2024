Please extract the QRcode.zip file before running server.py




List of Things to Fix (Could potentially pose security threats)

- Hardcoded Secret Key: Move `app.secret_key` to an environment variable to prevent exposure of sensitive keys.

- Hardcoded Server Tokens: Store the `PostmarkClient` server token in an environment variable to prevent unauthorized access if the code is leaked.

- Plaintext PINs in Email: Stop sending sensitive PINs via email in plaintext; use one-time secure links instead. (Minor)

- Plaintext PIN Storage: Hash PINs before storing them in the database to protect against database breaches.
