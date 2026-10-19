# Event Hub Consumer

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

## Goal

A runnable first check that your Event Hub credentials work and telemetry is flowing. Prints a few events and exits. It does not block waiting for data that may never come.

## Prerequisites

- Python 3.9 or later
- Connection string (See [Setup Credentials](../../docs/setup-credentials.md))
- Packages: `pip install -q -r requirements.txt`
- Network: Outbound AMQP on 5671, or 443 with the WebSocket transport

> [!NOTE]
> The connection string is the only value you need. The hub name travels inside it as
> `EntityPath`.
> 
> The Event Hub belongs to the **consumer**, not to the partner, which is why running two
> applications gives you two hubs, one per consumer.

## Steps

### 1. Install the dependencies 

First, go to the folder then run the following commands to install the dependencies and set the connection string in your environment.

```bash
cd examples/eventhub-consumer-python
pip install -q -r requirements.txt
```

> **Note:** `-q` means quiet. If all the requirements are already installed, nothing is printed.

### 2. Set the connection string

Choose one method.

**Option A:** `.env` file

1. Copy `.env.template` to `.env`.
2. Set your connection string:

    ```dotenv
    BDP_EVENTHUB_CONNECTION_STRING="Endpoint=sb://...;EntityPath=..."
    ```

**Option B:** environment variable

```bash
# bash
export BDP_EVENTHUB_CONNECTION_STRING="Endpoint=sb://...;EntityPath=..."
```

or

```powershell
# powershell
$env:BDP_EVENTHUB_CONNECTION_STRING = "Endpoint=sb://...;EntityPath=..."
```

If both are set, the environment variable wins.

### 3. Run the consumer

Run the consumer script to read events from the Event Hub.

```bash
python consume.py
```

> [!NOTE]
> **Windows:** if `python` prints "Python was not found; run without arguments to install from the Microsoft Store", use the Python launcher `py` instead. ex: `py consume.py`

#### Expected Outcome

- Exit code `0` when at least one event is read within the configured timeout.
- Exit code `1` when no events arrive during the run.
- Explicit output that differentiates transport, credential, and configuration issues.

Expected output sample:

```text
connecting at 2026-08-05T12:00:00+00:00, consumer group $Default, amqp (port 5671), replaying retained stream
[  1] partition=0 offset=12345 enqueued=2026-08-05T11:59:58+00:00 {Version, MessageType, Timestamp, Value, PointId, BuildingId}
received 1 event(s); stopping
```

## Notes

### Options

Here are the command-line options you can use to control the consumer's behavior. The defaults are suitable for a quick check, but you may want to adjust them for your own use.

| Flag | Effect |
| --- | --- |
| `--count N` | Stop after N events (default 10) |
| `--timeout S` | Stop after S seconds with no event (default 30) |
| `--from-latest` | Only new events, the default replays the retained stream |
| `--consumer-group NAME` | Use a dedicated group instead of `$Default` |
| `--raw` | Print the raw message body instead of a summary |
| `--transport websockets` | Tunnel AMQP over 443 instead of using 5671 |

### If port 5671 is blocked

Both transports are fully supported, choose by what your network allows.

| Transport | Port | Extra package |
| --- | --- | --- |
| `amqp` (default) | 5671 | none |
| `websockets` | 443 | `websocket-client` |

```bash
pip install websocket-client
python consume.py --transport websockets
```

**The missing package does not produce an error.** 

The Azure SDK swallows the `ImportError` inside its load-balancing loop and retries roughly every 30 seconds, so a client that should fail in one second instead sits there producing nothing at all. It is not a credentials problem, a rule problem or a firewall problem, and it looks like all three.

`consume.py` checks for the package up front and tells you, rather than inheriting the hang.

### Troubleshooting

The script exits non-zero and says so rather than hanging. In order of likelihood:

1. **Your consumer has no subscription rule**, or the rule filters out everything. It authenticates fine and receives nothing, this is the most common cause by a wide margin.
2. **Your company is not authorized for the site**, so there is no data to subscribe to.
3. **Another application is reading the same consumer group.** Event Hub consumer groups are not a load balancer; give each application its own with `--consumer-group`. The groups belong to the hub — read the ones you have from `GET /api/EventHubs`, and ask your Schneider Electric representative to add one if you need another.
4. **Port 5671 is blocked.** Use `--transport websockets`, which goes over 443.
5. **You passed `--from-latest` on a quiet stream.** It skips everything already retained, so a stream that is working but idle looks identical to one that is empty. Drop the flag to replay what is there.
6. **The connection string belongs to a different consumer.** It authenticates perfectly and delivers that consumer's data, which may be none of yours. Check the consumer name in the portal against the one you meant.

The first two need a configuration change on the platform side, contact your Schneider Electric representative with your consumer name and the environment. The rest are yours to change.

None of these produces an error message, which is why the script exits and reports what it saw rather than waiting.

### What a message looks like

For complete payload guidance (default shape, all-field groups, parser rules, and tradeoffs), see [Event Hub Message Payload](../../docs/eventhub-message-payload.md).


### Project Structure

Here is what each file does. The example is self-contained, it does not import any other files.

| File | Responsibility |
| --- | --- |
| `consume.py` | The complete example, dependency check, connection, bounded receive, summary or raw output |
| `requirements.txt` | Azure Event Hub SDK, and the optional WebSocket transport dependency |
| `.env.template` | Names the one environment variable, copy to `.env` and fill in |
| `README.md` / `SECURITY.md` | Usage and security posture |

## What's Next

- [Access Model and Permissions](../../docs/access-model-and-permissions.md)
- [Consuming Data](../../docs/consuming-data.md), payload selection and network requirements
- [Event Hub Message Payload](../../docs/eventhub-message-payload.md)
