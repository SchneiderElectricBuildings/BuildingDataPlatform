// Request a BDP API access token and print it.
//
// Usage:
//     node get_token.js

import 'dotenv/config';

const response = await fetch(
  `https://login.microsoftonline.com/${process.env.BDP_TENANT_ID}/oauth2/v2.0/token`,
  {
    method: 'POST',
    body: new URLSearchParams({
      client_id: process.env.BDP_CLIENT_ID,
      scope: process.env.BDP_SCOPES,
      client_secret: process.env.BDP_CLIENT_SECRET,
      grant_type: 'client_credentials',
    }),
  }
);
if (!response.ok) throw new Error(await response.text());

const body = await response.json();
console.log(body.access_token);
