import pytest

from testutils import (
    run,
    shell,
    CERTIFICATE_REQUIRED_ERROR,
    SELF_SIGNED_ERROR,
    EMPTY_CONTAINER_LIST,
)

# flake8: noqa: F401
# pylint: disable=no-self-use, unused-argument, unused-import
# from fixtures import host_state, create_testimage


@pytest.fixture()
def testimage_and_cleanup(create_testimage, host_state):
    yield host_state

    run("container prune -f")

    zfs_now = set(shell("zfs list -H -o name -r zroot/kleene").split("\n"))
    assert host_state["zfs"] == zfs_now


class TestHTTPConnections:

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
        assert SELF_SIGNED_ERROR in "".join(
            http_connection(
                "--host https://127.0.0.1:8085 --tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem",
                exit_code=1,
            )
        )
        assert CERTIFICATE_REQUIRED_ERROR in "".join(
            http_connection("--host https://127.0.0.1:8085 --no-tlsverify", exit_code=1)
        )


def successful_http_connection(connection_config):
    result = http_connection(connection_config)
    assert result == EMPTY_CONTAINER_LIST


def http_connection(connection_config, exit_code=0):
    return run(connection_config + " container ls", exit_code=exit_code)


class TestWebsocketConnections:

    def test_connecting_with_ipv6_and_no_tls(self, testimage_and_cleanup):
        successful_ws_connection("--host http://[::1]:8080")

    def test_connecting_with_unixsocket_and_no_tls(self, testimage_and_cleanup):
        successful_ws_connection("--host http:///var/run/kleened.sock")

    def test_connecting_with_unixsocket_and_basic_tls(self, testimage_and_cleanup):
        successful_ws_connection(
            "--host https:///var/run/kleened.tlssock --tlsverify --tlscacert=/usr/local/etc/kleened/certs/ca.pem"
        )

        successful_ws_connection(
            "--host https:///var/run/kleened.tlssock --no-tlsverify"
        )

    def test_connecting_with_ipv4_and_tls_using_client_authentication(
        self, testimage_and_cleanup
    ):
        successful_ws_connection(
            "--host https://127.0.0.1:8085 --tlsverify --tlscacert=/usr/local/etc/kleened/certs/ca.pem --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
        )
        successful_ws_connection(
            "--host https://127.0.0.1:8085 --no-tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem"
        )

        assert SELF_SIGNED_ERROR in "".join(
            ws_connection(
                "--host https://127.0.0.1:8085 --tlsverify --tlscert=/usr/local/etc/kleened/certs/client-cert.pem --tlskey=/usr/local/etc/kleened/certs/client-key.pem",
                exit_code=1,
            )
        )
        assert CERTIFICATE_REQUIRED_ERROR in "".join(
            run(
                "--host https://127.0.0.1:8085 --no-tlsverify container ls", exit_code=1
            )
        )


def successful_ws_connection(connection_config):
    output = ws_connection(connection_config)
    assert output[2] == "/etc/hosts"


def ws_connection(connection_config, exit_code=0):
    return run(
        connection_config + " run FreeBSD:latest /bin/ls /etc/hosts",
        exit_code=exit_code,
    )
