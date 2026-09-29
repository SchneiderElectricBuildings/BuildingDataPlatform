#!/usr/bin/env node

/**
 * Request a BDP API access token with the OAuth 2.0 client credentials flow.
 *
 * The script reads the client credentials retrieved from the BDP Portal, requests an
 * access token from the Microsoft identity platform, then uses that token for one
 * REST call (GET /api/Sites) to prove it is accepted.
 *
 * Usage:
 *     node get_token.js
 *     node get_token.js --no-verify
 *     node get_token.js --print-token
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { parseArgs } from 'util';
import dotenv from 'dotenv';

const TENANT_ID_ENV = 'BDP_TENANT_ID';
const CLIENT_ID_ENV = 'BDP_CLIENT_ID';
const CLIENT_SECRET_ENV = 'BDP_CLIENT_SECRET';
const SCOPES_ENV = 'BDP_SCOPES';
const REQUIRED_VARS = [TENANT_ID_ENV, CLIENT_ID_ENV, CLIENT_SECRET_ENV, SCOPES_ENV];

const UAT_BASE_URL = 'https://ecostruxure-building-platform-api-uat.se.app';

const TOKEN_ERROR_HINTS = {
  invalid_client:
    "client secret is wrong or expired. Check BDP_CLIENT_SECRET and the credential 'Expires On' date in the portal.",
  unauthorized_client:
    'client ID not found in this tenant. Check BDP_CLIENT_ID and BDP_TENANT_ID.',
  invalid_scope: 'scope is not valid. Copy BDP_SCOPES exactly from the portal.',
  invalid_request:
    'request rejected. Check BDP_TENANT_ID and that every value is set.',
};

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// With --print-token, stdout carries only the token so it can be captured by a shell.
let log = (message) => console.log(message);

function tokenUrl(tenantId) {
  return `https://login.microsoftonline.com/${encodeURIComponent(tenantId)}/oauth2/v2.0/token`;
}

/**
 * Show only the edges of a secret value.
 */
function mask(value) {
  if (value.length <= 12) {
    return '***';
  }
  return `${value.slice(0, 6)}...${value.slice(-4)}`;
}

function printUsage() {
  console.log('Usage: node get_token.js [OPTIONS]');
  console.log('\nOptions:');
  console.log('  --no-verify              only request the token, skip the GET /api/Sites check');
  console.log('  --print-token            write only the access token to stdout (treat it as a secret)');
  console.log('  --base-url <url>         REST API host for the check (default: UAT host)');
  console.log('  --api-version 2.0|3.0    (default: 3.0)');
  console.log('  --timeout <seconds>      (default: 30)');
  console.log('  --help                   show this help message');
}

/**
 * Map Microsoft identity platform errors to actionable hints.
 */
function printTokenError(status, body) {
  let payload = {};
  try {
    payload = JSON.parse(body);
  } catch {
    // Non-JSON error body, fall through to the raw snippet.
  }

  const error = payload.error ?? '';
  const description = (payload.error_description ?? '').split(/\r?\n/)[0];

  if (TOKEN_ERROR_HINTS[error]) {
    console.error(`HTTP ${status} ${error}: ${TOKEN_ERROR_HINTS[error]}`);
  } else {
    console.error(`HTTP ${status}: ${error || body.substring(0, 400).trim()}`);
  }
  if (description) {
    console.error(`  ${description}`);
  }
}

async function requestToken(settings, timeoutMs) {
  const form = new URLSearchParams({
    client_id: settings[CLIENT_ID_ENV],
    scope: settings[SCOPES_ENV],
    client_secret: settings[CLIENT_SECRET_ENV],
    grant_type: 'client_credentials',
  });

  const response = await fetch(tokenUrl(settings[TENANT_ID_ENV]), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Accept: 'application/json',
    },
    body: form,
    signal: AbortSignal.timeout(timeoutMs),
  });

  const body = await response.text();
  return { status: response.status, ok: response.ok, body };
}

async function callSites(baseUrl, token, apiVersion, timeoutMs) {
  const url = `${baseUrl.replace(/\/+$/, '')}/api/Sites?take=5`;
  log(`GET ${url}`);

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'X-Api-Version': apiVersion,
      Accept: 'application/json',
    },
    signal: AbortSignal.timeout(timeoutMs),
  });
  const body = await response.text();

  if (!response.ok) {
    if (response.status === 401) {
      console.error('HTTP 401: the API rejected the token. Check BDP_SCOPES.');
    } else if (response.status === 403) {
      console.error('HTTP 403: token accepted, but your consumer is not authorized for this data.');
    } else {
      console.error(`HTTP ${response.status}: ${body.substring(0, 400).trim()}`);
    }
    return 1;
  }

  log(`status: ${response.status}`);
  let payload = [];
  try {
    payload = body ? JSON.parse(body) : [];
  } catch {
    payload = [];
  }
  const items = Array.isArray(payload) ? payload : payload.items ?? [];
  if (Array.isArray(items)) {
    log(`items: ${items.length}`);
    for (const item of items.slice(0, 5)) {
      if (item && typeof item === 'object') {
        log(`  - ${item.id ?? '-'} | ${item.name ?? '-'}`);
      }
    }
  }
  return 0;
}

async function main(argv) {
  let parsed;
  try {
    parsed = parseArgs({
      args: argv,
      options: {
        'no-verify': { type: 'boolean', default: false },
        'print-token': { type: 'boolean', default: false },
        'base-url': { type: 'string', default: UAT_BASE_URL },
        'api-version': { type: 'string', default: '3.0' },
        timeout: { type: 'string', default: '30' },
        help: { type: 'boolean', short: 'h' },
      },
      allowPositionals: false,
      strict: true,
    });
  } catch (err) {
    console.error(err.message);
    printUsage();
    return 2;
  }

  if (parsed.values.help) {
    printUsage();
    return 0;
  }

  const apiVersion = parsed.values['api-version'];
  if (apiVersion !== '2.0' && apiVersion !== '3.0') {
    console.error('--api-version must be 2.0 or 3.0');
    return 2;
  }

  const timeoutSeconds = parseInt(parsed.values.timeout, 10);
  if (isNaN(timeoutSeconds) || timeoutSeconds <= 0) {
    console.error('--timeout must be a positive integer');
    return 2;
  }
  const timeoutMs = timeoutSeconds * 1000;

  if (parsed.values['print-token']) {
    log = (message) => console.error(message);
  }

  // dotenv never overrides variables already set in the environment.
  dotenv.config({ path: path.join(__dirname, '.env'), quiet: true });
  dotenv.config({ path: path.join(process.cwd(), '.env'), quiet: true });

  const settings = {};
  for (const name of REQUIRED_VARS) {
    if (process.env[name]) {
      settings[name] = process.env[name];
    }
  }
  const missing = REQUIRED_VARS.filter((name) => !settings[name]);
  if (missing.length > 0) {
    console.error(
      `missing ${missing.join(', ')}. Set them in your environment or in a .env file in this folder (see docs/retrieve-client-credentials.md)`
    );
    return 2;
  }

  log(`POST ${tokenUrl(settings[TENANT_ID_ENV])}`);

  let accessToken;
  try {
    const { status, ok, body } = await requestToken(settings, timeoutMs);
    if (!ok) {
      printTokenError(status, body);
      return 1;
    }

    let tokenResponse;
    try {
      tokenResponse = JSON.parse(body);
    } catch {
      console.error('token endpoint returned a non-JSON response');
      return 1;
    }

    accessToken = tokenResponse.access_token;
    if (!accessToken) {
      console.error('token endpoint response has no access_token');
      return 1;
    }

    log('token: acquired');
    log(`  token_type: ${tokenResponse.token_type ?? '-'}`);
    log(`  expires_in: ${tokenResponse.expires_in ?? '-'} seconds`);
    log(`  access_token: ${mask(accessToken)}`);

    let exitCode = 0;
    if (!parsed.values['no-verify']) {
      exitCode = await callSites(parsed.values['base-url'], accessToken, apiVersion, timeoutMs);
    }

    if (parsed.values['print-token'] && exitCode === 0) {
      console.log(accessToken);
    }
    return exitCode;
  } catch (err) {
    if (err.name === 'TimeoutError') {
      console.error('network error: request timed out');
    } else {
      console.error(`network error: ${err.cause?.message ?? err.message}`);
    }
    return 1;
  }
}

process.exitCode = await main(process.argv.slice(2));
