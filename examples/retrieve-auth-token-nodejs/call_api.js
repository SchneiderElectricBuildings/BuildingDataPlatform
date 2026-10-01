// Get a BDP API access token, reuse it while valid, and call the REST API.
//
// Usage:
//     node call_api.js

import 'dotenv/config';

const API_BASE_URL = 'https://ecostruxure-building-platform-api-uat.se.app';
const TOKEN_URL = `https://login.microsoftonline.com/${process.env.BDP_TENANT_ID}/oauth2/v2.0/token`;

let token = null;
let expiresAt = 0;

// Return a valid token, requesting a new one only when needed.
async function getToken() {
  // Refresh one minute early so a token never expires in the middle of a call.
  if (token === null || Date.now() > expiresAt - 60_000) {
    console.log('requesting a new token');
    const response = await fetch(TOKEN_URL, {
      method: 'POST',
      body: new URLSearchParams({
        client_id: process.env.BDP_CLIENT_ID,
        scope: process.env.BDP_SCOPES,
        client_secret: process.env.BDP_CLIENT_SECRET,
        grant_type: 'client_credentials',
      }),
    });
    if (!response.ok) throw new Error(await response.text());
    const body = await response.json();
    token = body.access_token;
    expiresAt = Date.now() + body.expires_in * 1000;
  }

  return token;
}

async function getSites() {
  const response = await fetch(`${API_BASE_URL}/api/Sites`, {
    headers: {
      Authorization: `Bearer ${await getToken()}`,
      'X-Api-Version': '3.0',
    },
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

// The first call requests a token, the second one reuses it.
console.log(await getSites());
console.log(await getSites());
