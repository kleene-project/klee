from testutils import run, CERTIFICATE_REQUIRED_ERROR, SELF_SIGNED_ERROR
from klee.config import config

EMPTY_LIST = [
    " CONTAINER ID    NAME   IMAGE   COMMAND   CREATED   STATUS   JID ",
    "─────────────────────────────────────────────────────────────────",
    "",
]


class TestHTTPConnections:
    # pylint: disable=no-self-use
    def test_connecting_with_ipv6_and_no_tls(self):
        successful_http_connection("--host http://[::1]:8080")

    def test_connecting_with_unixsocket_and_no_tls(self):
        successful_http_connection("--host http:///var/run/kleened.sock")

    def test_connecting_with_unixsocket_and_basic_tls(self):
        successful_http_connection(
            "--host https:///var/run/kleened.tlssock --tlsverify --tlscacert=/usr/local/etc/kleened/certs/ca.pem"
        )

        successful_http_connection(
            "--host https:///var/run/kleened.tlssock --no-tlsverify"
        )

    def test_connecting_with_ipv4_and_tls_using_client_authentication(self):
        successful_http_connection(
            "--host https://127.0.0.1:8085 --tlsverify --tlscacert=/usr/local/etc/kleened/certs/ca.pem --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
        )
        successful_http_connection(
            "--host https://127.0.0.1:8085 --no-tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
        )
        assert SELF_SIGNED_ERROR == "".join(
            http_connection(
                "--host https://127.0.0.1:8085 --tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem",
                exit_code=1,
            )
        )
        assert CERTIFICATE_REQUIRED_ERROR == "".join(
            http_connection("--host https://127.0.0.1:8085 --no-tlsverify", exit_code=1)
        )


def successful_http_connection(connection_config):
    result = http_connection(connection_config)
    assert result == EMPTY_LIST


def http_connection(connection_config, exit_code=0):
    return run(connection_config + " container ls", exit_code=exit_code)


class TestWebsocketConnections:
    # pylint: disable=no-self-use
    def test_connecting_with_ipv6_and_no_tls(self):
        successful_ws_connection("--host http://[::1]:8080")

    def test_connecting_with_unixsocket_and_no_tls(self):
        successful_ws_connection("--host http:///var/run/kleened.sock")

    def test_connecting_with_unixsocket_and_basic_tls(self):
        successful_ws_connection(
            "--host https:///var/run/kleened.tlssock --tlsverify --tlscacert=/usr/local/etc/kleened/certs/ca.pem"
        )

        successful_ws_connection(
            "--host https:///var/run/kleened.tlssock --no-tlsverify"
        )

    def test_connecting_with_ipv4_and_tls_using_client_authentication(self):
        successful_ws_connection(
            "--host https://127.0.0.1:8085 --tlsverify --tlscacert=/usr/local/etc/kleened/certs/ca.pem --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
        )
        successful_ws_connection(
            "--host https://127.0.0.1:8085 --no-tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
        )

        assert SELF_SIGNED_ERROR == "".join(
            ws_connection(
                "--host https://127.0.0.1:8085 --tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem",
                exit_code=1,
            )
        )
        assert CERTIFICATE_REQUIRED_ERROR == "".join(
            run(
                "--host https://127.0.0.1:8085 --no-tlsverify container ls", exit_code=1
            )
        )


def successful_ws_connection(connection_config):
    output = ws_connection(connection_config)
    assert output[2] == "/etc/hosts"


def ws_connection(connection_config, exit_code=0):
    return run(
        connection_config + " run FreeBSD:testing /bin/ls /etc/hosts",
        exit_code=exit_code,
    )
