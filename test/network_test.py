import time
import json

from testutils import (
    container_get_netstat_info,
    extract_exec_id,
    inspect,
    prune,
    run,
    container_stopped_msg,
)


class TestNetworkSubcommand:
    # pylint: disable=no-self-use, unused-argument
    def test_assert_empty_network_listing_of_networks(self, testimage):
        # We need to create the test image on the first test,
        # otherwise the 'host_state["zfs"]' will be initialized before the test image is created.
        assert_empty_network_list()

    def test_add_remove_and_list_networks(self, host_state):
        name = "test_arl_networks"

        cmd = f"network create --interface testif --subnet 10.13.37.0/24 {name}"
        network_id, _ = run(cmd)
        assert len(network_id) == 12

        networks = list_networks()
        assert len(networks) == 1
        assert networks[0][1:13] == network_id

        network_id_remove, _ = run(f"network rm {name}")
        assert network_id_remove == network_id

        assert_empty_network_list()

    def test_inspect_network(self, host_state):
        name = "test_network_inspect"
        cmd = f"network create --interface testif --subnet 10.13.37.0/24 {name}"
        network_id, _ = run(cmd)
        assert inspect("network", "notexist") == "network not found"
        network_endpoints = inspect("network", network_id)
        assert network_endpoints["network"]["name"] == name
        run(f"network rm {network_id}")

    def test_prune_network(self, host_state):
        cmd = "network create --interface testif1 --subnet 10.13.37.0/24 test_prune1"
        network_id1, _ = run(cmd)
        cmd = "network create --interface testif2 --subnet 10.13.38.0/24 test_prune2"
        network_id2, _ = run(cmd)
        assert set(prune("network")) == set([network_id1, network_id2])

    def test_remove_network_by_id(self, host_state):
        network_id1, _ = run("network create --subnet 10.13.37.0/24 test_rm1")
        network_id2, _ = run("network create --subnet 10.13.38.0/24 test_rm2")
        network_id1_again, _ = run(f"network rm {network_id1}")
        network_id2_again, _ = run(f"network rm {network_id2[:8]}")
        assert network_id1 == network_id1_again
        assert network_id2 == network_id2_again
        assert_empty_network_list()

    def test_connectivity_of_container_connected_to_ipnet_network(self, testimage):
        network_id, _ = run("network create --subnet 10.13.37.0/24 test_conn")
        container_id, _ = run(
            "create -n test_conn -l ipnet FreeBSD /usr/bin/host -t A freebsd.org 1.1.1.1"
        )
        container_is_connected(container_id)
        run(f"rmc {container_id}")
        run(f"network rm {network_id}")

    def test_connectivity_of_container_connected_to_vnet_network(self, testimage):
        network_id, _ = run("network create -t bridge --subnet 10.13.37.0/24 test_vnet")
        container_id, _ = run(
            "container create --name disconn_network --driver vnet --network test_vnet FreeBSD /usr/bin/host -t A freebsd.org 1.1.1.1"
        )
        container_is_connected(container_id, driver="vnet")
        run(f"rmc {container_id}")
        run(f"network rm {network_id}")

    def test_connectivity_when_connecting_and_disconnecting_to_loopback_network(
        self, testimage_and_cleanup
    ):
        network_name = "test_nw_disconn"
        run(f"network create --subnet 10.13.38.0/24 {network_name}")
        container_id, _ = run(
            f"container create --network {network_name} -l ipnet FreeBSD /usr/bin/host -t A freebsd.org 1.1.1.1"
        )
        container_is_connected(container_id)
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        container_is_disconnected(container_id)

    def test_connectivity_when_connecting_and_disconnecting_to_vnet_network(
        self, testimage_and_cleanup
    ):
        network_name = "test_nw_disconn"
        cmd = f"network create -t bridge --subnet 10.13.37.0/24 {network_name}"
        run(cmd)

        cmd = f"container create --driver vnet --network {network_name} FreeBSD /usr/bin/host -t A freebsd.org 1.1.1.1"
        container_id, _ = run(cmd)
        container_is_connected(container_id, driver="vnet")
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        container_is_disconnected(container_id)

    def test_connect_and_disconnect_of_running_ipnet_container(self, testimage):
        run("network create -t loopback --subnet 10.13.37.0/24 test-ipnet")
        run("run --name disconn_ipnet -d -l ipnet FreeBSD sleep 10")

        assert not ip_in_container("disconn_ipnet", "10.13.37.1")
        assert [""] == run("network connect test-ipnet disconn_ipnet")
        assert ip_in_container("disconn_ipnet", "10.13.37.1")
        assert [""] == run("network disconnect test-ipnet disconn_ipnet")
        assert not ip_in_container("disconn_ipnet", "10.13.37.1")
        run("rmc -f disconn_ipnet")
        run("network rm test-ipnet")

    def test_disconnect_of_running_vnet_container(self, testimage):
        run("network create -t bridge --subnet 10.13.37.0/24 test-vnet")
        run("run --name disconn_vnet -n test-vnet -d -l vnet FreeBSD sleep 10")
        time.sleep(1)  # Takes time to add the IP, default gw etc. inside the jail

        # 10.13.37.2 since 10.13.37.1 is taken by the default gw
        assert ip_in_container("disconn_vnet", "10.13.37.2")
        assert interface_in_container("disconn_vnet", "epair0b")
        assert [""] == run("network disconnect test-vnet disconn_vnet")
        assert not ip_in_container("disconn_vnet", "10.13.37.2")
        assert not interface_in_container("disconn_vnet", "epair0b")
        run("rmc -f disconn_vnet")
        run("network rm test-vnet")

    def test_create_container_with_user_defined_ip_loopback(
        self, testimage_and_cleanup
    ):
        run("network create -t loopback --subnet 10.13.37.0/24 testnet9")
        container_id, _ = run(
            "container create --ip 10.13.37.13 --network testnet9 -l ipnet FreeBSD /usr/bin/netstat --libxo json -i -4"
        )
        netstat_info = container_get_netstat_info(container_id, driver="loopback")
        assert netstat_info[0]["address"] == "10.13.37.13"
        assert [""] == run(f"network disconnect testnet9 {container_id}")

    def test_create_container_with_user_defined_ip_vnet(self, testimage_and_cleanup):
        run("network create -t bridge --subnet 10.13.38.0/24 testnet9")
        container_id, _ = run(
            "container create --ip 10.13.38.13 --network testnet9 -l vnet FreeBSD /usr/bin/netstat --libxo json -i -4"
        )
        netstat_info = container_get_netstat_info(container_id, driver="vnet")
        assert netstat_info[0]["address"] == "10.13.38.13"
        assert [""] == run(f"network disconnect testnet9 {container_id}")

    def test_connect_container_with_user_defined_ip_loopback(
        self, testimage_and_cleanup
    ):
        container_name = "custom_ip3"
        network_name = "custom_ip3"
        run(f"network create -t loopback --subnet 10.13.37.0/24 {network_name}")
        cmd = f"container create --driver ipnet --name {container_name} FreeBSD /usr/bin/netstat --libxo json -i -4"
        container_id, _ = run(cmd)
        run(f"network connect --ip 10.13.37.13 {network_name} {container_name}")
        netstat_info = container_get_netstat_info(container_id, driver="loopback")
        assert netstat_info[0]["address"] == "10.13.37.13"
        assert [""] == run(f"network disconnect {network_name} {container_id}")

    def test_connect_container_with_user_defined_ip_vnet(self, testimage):
        container_name = "custom_ip3"
        network_name = "custom_ip3"
        cmd = f"network create -t loopback --interface testif -t bridge --subnet 10.13.38.0/24 {network_name}"
        network_id, _ = run(cmd)
        cmd = f"container create --name {container_name} --driver vnet FreeBSD /usr/bin/netstat --libxo json -i -4"
        container_id, _ = run(cmd)

        run(f"network connect --ip 10.13.38.13 {network_name} {container_name}")
        netstat_info = container_get_netstat_info(container_id, driver="vnet")
        assert netstat_info[0]["address"] == "10.13.38.13"
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        run(f"rmc {container_id}")
        run(f"network rm {network_name}")

    def test_create_a_internal_network(self, host_state):
        run("network create --internal --type loopback --subnet=10.13.38.0/24 testnet")
        network = inspect("network", "testnet")
        run("network rm testnet")
        assert network["network"]["internal"]

    def test_create_container_using_nonexisting_network(self, host_state):
        output = run(
            "container create --name invalid_network --network nonexisting FreeBSD /bin/ls",
            exit_code=1,
        )
        assert [
            "network not found",
            "could not connect container: network not found",
            "",
        ] == output[1:]
        run("rmc invalid_network")


def container_is_connected(container_id, driver="loopback"):
    output = run(f"container start {container_id}")
    exec_id = extract_exec_id(output)
    if driver == "loopback":
        connected_output = [
            f"created execution instance {exec_id}",
            "Using domain server:",
            "Name: 1.1.1.1",
            "Address: 1.1.1.1#53",
            "Aliases: ",
            "",
            "freebsd.org has address 96.47.72.84",
            "",
            container_stopped_msg(exec_id),
            "",
        ]
    elif driver == "vnet":
        connected_output = [
            f"created execution instance {exec_id}",
            "add net default: gateway 10.13.37.1",
            "Using domain server:",
            "Name: 1.1.1.1",
            "Address: 1.1.1.1#53",
            "Aliases: ",
            "",
            "freebsd.org has address 96.47.72.84",
            "",
            container_stopped_msg(exec_id),
            "",
        ]
    else:
        connected_output = ["unknown driver used"]

    assert output == connected_output


def container_is_disconnected(container_id):
    output = run(f"container start {container_id}")
    exec_id = extract_exec_id(output)
    disconnected_output = [
        f"created execution instance {exec_id}",
        ";; connection timed out; no servers could be reached",
        "jail: /usr/bin/env /usr/bin/host -t A freebsd.org 1.1.1.1: failed",
        "",
        container_stopped_msg(exec_id, 1),
        "",
    ]
    assert disconnected_output == output


def list_networks():
    _header, _header_line, *networks = run("network ls")
    return networks[:-1]


def assert_empty_network_list():
    expected_output = [" ID   NAME   TYPE   SUBNET ", "───────────────────────────", ""]
    output = run("network ls")
    assert expected_output == output


def ip_in_container(container, ip):
    netstat_json = run(["exec", container, "/bin/sh", "-c", "netstat --libxo json -i"])
    interface_info = json.loads(netstat_json[1])
    addresses = {
        address_info["address"]
        for address_info in interface_info["statistics"]["interface"]
    }
    return ip in addresses


def interface_in_container(container, interface):
    netstat_json = run(["exec", container, "/bin/sh", "-c", "netstat --libxo json -i"])
    interface_info = json.loads(netstat_json[1])
    interfaces = {
        address_info["name"]
        for address_info in interface_info["statistics"]["interface"]
    }
    return interface in interfaces
