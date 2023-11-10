from testutils import run, CERTIFICATE_REQUIRED_ERROR, SELF_SIGNED_ERROR
from klee.config import config

EMPTY_LIST = [
    " CONTAINER ID    NAME   IMAGE   TAG   COMMAND   CREATED   STATUS ",
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
                "--host https://127.0.0.1:8085 --tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
            )
        )
        assert CERTIFICATE_REQUIRED_ERROR == "".join(
            http_connection("--host https://127.0.0.1:8085 --no-tlsverify")
        )


def successful_http_connection(connection_config):
    result = http_connection(connection_config)
    assert result == EMPTY_LIST


def http_connection(connection_config):
    return run(connection_config + " container ls")


class TestWebsocketConnections:
    # pylint: disable=no-self-use
    def test_connecting_with_ipv6_and_no_tls(self):
        assert succesuful_ws_connection("--host http://[::1]:8080")

    def test_connecting_with_unixsocket_and_no_tls(self):
        assert succesuful_ws_connection("--host http:///var/run/kleened.sock")

    def test_connecting_with_unixsocket_and_basic_tls(self):
        assert succesuful_ws_connection(
            "--host https:///var/run/kleened.tlssock --tlsverify --tlscacert=/usr/local/etc/kleened/certs/ca.pem"
        )

        assert succesuful_ws_connection(
            "--host https:///var/run/kleened.tlssock --no-tlsverify"
        )

    def test_connecting_with_ipv4_and_tls_using_client_authentication(self):
        assert succesuful_ws_connection(
            "--host https://127.0.0.1:8085 --tlsverify --tlscacert=/usr/local/etc/kleened/certs/ca.pem --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
        )
        assert succesuful_ws_connection(
            "--host https://127.0.0.1:8085 --no-tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
        )

        assert SELF_SIGNED_ERROR == "".join(
            ws_connection(
                "--host https://127.0.0.1:8085 --tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
            )
        )
        assert CERTIFICATE_REQUIRED_ERROR == "".join(
            run("--host https://127.0.0.1:8085 --no-tlsverify container ls")
        )


def succesuful_ws_connection(connection_config):
    output = ws_connection(connection_config)
    _, _, result, _, _, _ = output
    return result == "/etc/hosts"


def ws_connection(connection_config):
    return run(connection_config + " run --attach FreeBSD:testing /bin/ls /etc/hosts")
