# Agent instructions for pyControl4

pyControl4 is an asyncio client for the REST and WebSocket API built into Control4 controllers. The API is undocumented, and Home Assistant depends on this library's public methods.

## Checks

```bash
pip install -r requirements-dev.txt pytest black flake8 mypy
pytest
black --check .
flake8 pyControl4
mypy pyControl4
```

## Rules

- Command and variable names must come from something observed: a real Director's responses, captured app traffic, or the Snap One DriverWorks proxy docs. Do not derive one by analogy with another device; naming differs between them (`LIGHT_LEVEL`, `RelayState`, `Battery Level`).
- Director responses vary by device, driver and OS version. A key can be missing, and a variable with no value comes back as the string `"Undefined"`, which `director.py` converts to `None`. Check before indexing, and before calling `int()` or `bool()`.
- Renaming a public method or changing what it returns is a breaking change.
- Errors reported by the API are detected in `check_response_for_error`, not at call sites. It raises `C4Exception` or a subclass, with the full response text as the message.
- Never close an `aiohttp.ClientSession` that the caller passed in.
- The SSL and session setup in `websocket.py` is deliberate: Directors use self-signed certificates, and creating an SSL context inside the event loop blocks it. Read the comments there before changing it.
- Runtime dependencies are listed in both `setup.py` and `requirements.txt`; change them together. Keep `python-socketio-v4`, because Control4 only speaks Engine.IO v3.
- `APPLICATION_KEY` in `account.py` is the key the Control4 app itself sends, not a leaked secret. Leave it in the source.
- Docstrings are the published documentation. For methods that return API data, show an example of the structure or list the possible raw values.
