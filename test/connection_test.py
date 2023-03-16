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


class TestContainerSubcommand:
    # pylint: disable=no-self-use
    def test_connecting_with_ipv6_and_no_tls(self):
        assert EMPTY_LIST == run("--host http://[::1]:8080 container ls")

    def test_connecting_with_unixsocket_and_no_tls(self):
        assert EMPTY_LIST == run("--host http:///var/run/kleened.sock container ls")

    def test_connecting_with_unixsocket_and_basic_tls(self):
        assert EMPTY_LIST == run(
            "--host https:///var/run/kleened.tlssock --tlsverify --tlscacert=/usr/local/etc/kleened/certs/ca.pem container ls"
        )

        assert EMPTY_LIST == run(
            "--host https:///var/run/kleened.tlssock --no-tlsverify container ls"
        )

    def test_connecting_with_ipv4_and_tls_using_client_authentication(self):
        assert EMPTY_LIST == run(
            "--host https://127.0.0.1:8085 --tlsverify --tlscacert=/usr/local/etc/kleened/certs/ca.pem --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem container ls"
        )
        assert EMPTY_LIST == run(
            "--host https://127.0.0.1:8085 --no-tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem container ls"
        )
        assert SELF_SIGNED_ERROR == run(
            "--host https://127.0.0.1:8085 --tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem container ls"
        )
        assert CERTIFICATE_REQUIRED_ERROR == run(
            "--host https://127.0.0.1:8085 --no-tlsverify container ls"
        )
