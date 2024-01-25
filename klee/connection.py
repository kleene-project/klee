import ssl
from contextlib import asynccontextmanager

from urllib.parse import urlparse

import httpx
import websockets

from .client.client import Client
from .printing import echo_bold
from .config import config

URL_TEMPLATE = "{scheme}://{host}{endpoint}"

ERROR_TLSKEY_WITH_TLSCERT = (
    "When '--tlscert' is set you must also provide the '--tlskey'"
)


def valid_connection_params():
    valid = True

    if (
        config.host.query != ""
        or config.host.params != ""
        or config.host.fragment != ""
    ):
        echo_bold("Could not parse the '--host' parameter")
        valid = False

    if config.tlscert is not None and config.tlskey is None:
        echo_bold(ERROR_TLSKEY_WITH_TLSCERT)
        valid = False

    return valid


def request(endpoint, kwargs):
    if not valid_connection_params():
        return

    transport_kwargs = {}
    if config.host.scheme == "https":
        # Configuring TLS if it is used
        if config.tlscacert is not None:
            verify = config.tlscacert
        else:
            verify = config.tlsverify

        if config.tlscert is not None:
            cert = (config.tlscert, config.tlskey)
        else:
            cert = None

        transport_kwargs.update({"cert": cert, "verify": verify})

    else:
        transport_kwargs.update({"verify": False})

    if config.host.netloc == "":
        # If the connection is to a unix-socket
        url = urlparse(f"{config.host.scheme}://localhost").geturl()
        transport = httpx.HTTPTransport(uds=config.host.path, **transport_kwargs)
    else:
        url = config.host.geturl()
        transport = httpx.HTTPTransport(**transport_kwargs)

    # Try to connect to backend
    client = Client(base_url=url, timeout=60.0)
    return endpoint(transport, client=client, **kwargs)


@asynccontextmanager
async def create_websocket(endpoint):
    cafile = None
    tls_ctx = None
    url_scheme = "ws"
    server_hostname = None
    if config.host.scheme == "https":
        # Configuring TLS if it is used
        if config.tlscacert is not None:
            cafile = config.tlscacert

        tls_ctx = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH, cafile=cafile
        )

        if not config.tlsverify:
            tls_ctx.verify_mode = ssl.CERT_NONE

        if config.tlscert is not None:
            tls_ctx.load_cert_chain(config.tlscert, keyfile=config.tlskey)

        url_scheme = "wss"

    if config.host.netloc == "":
        # If the connection is to a unix-socket
        uri = URL_TEMPLATE.format(
            scheme=url_scheme, host="localhost", endpoint=endpoint
        )
        if config.host.scheme == "https":
            server_hostname = "localhost"
        else:
            server_hostname = None

        async with websockets.unix_connect(
            config.host.path, uri=uri, ssl=tls_ctx, server_hostname=server_hostname
        ) as websocket:
            yield websocket

    else:
        uri = URL_TEMPLATE.format(
            scheme=url_scheme, host=config.host.netloc, endpoint=endpoint
        )
        async with websockets.connect(uri, ssl=tls_ctx) as websocket:
            yield websocket
