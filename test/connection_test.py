from testutils import run

EMPTY_LIST = [
    "CONTAINER ID    IMAGE    TAG    COMMAND    CREATED    STATUS    NAME",
    "--------------  -------  -----  ---------  ---------  --------  ------",
    "",
    "",
]

SELF_SIGNED_ERROR = [
    "unable to connect to kleened: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:1134)",
    "",
]

CERTIFICATE_REQUIRED_ERROR = [
    "unable to connect to kleened: [SSL: TLSV13_ALERT_CERTIFICATE_REQUIRED] tlsv13 alert certificate required (_ssl.c:2638)",
    "",
]


class TestHTTPConnections:
    # pylint: disable=no-self-use
    def test_connecting_with_ipv6_and_no_tls(self):
        assert successful_http_connection("--host http://[::1]:8080")

    def test_connecting_with_unixsocket_and_no_tls(self):
        assert successful_http_connection("--host http:///var/run/kleened.sock")

    def test_connecting_with_unixsocket_and_basic_tls(self):
        assert successful_http_connection(
            "--host https:///var/run/kleened.tlssock --tlsverify --tlscacert=/usr/local/etc/kleened/certs/ca.pem"
        )

        assert successful_http_connection(
            "--host https:///var/run/kleened.tlssock --no-tlsverify"
        )

    def test_connecting_with_ipv4_and_tls_using_client_authentication(self):
        assert successful_http_connection(
            "--host https://127.0.0.1:8085 --tlsverify --tlscacert=/usr/local/etc/kleened/certs/ca.pem --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
        )
        assert successful_http_connection(
            "--host https://127.0.0.1:8085 --no-tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
        )
        assert SELF_SIGNED_ERROR == http_connection(
            "--host https://127.0.0.1:8085 --tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
        )
        assert CERTIFICATE_REQUIRED_ERROR == http_connection(
            "--host https://127.0.0.1:8085 --no-tlsverify"
        )


def successful_http_connection(connection_config):
    result = http_connection(connection_config)
    return result == EMPTY_LIST


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

        assert SELF_SIGNED_ERROR == ws_connection(
            "--host https://127.0.0.1:8085 --tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
        )
        assert CERTIFICATE_REQUIRED_ERROR == run(
            "--host https://127.0.0.1:8085 --no-tlsverify container ls"
        )


def succesuful_ws_connection(connection_config):
    _, _, result, _, _ = ws_connection(connection_config)
    return result == "/etc/hosts"


def ws_connection(connection_config):
    return run(connection_config + " run --attach base /bin/ls /etc/hosts")
