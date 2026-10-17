import time
import re

from testutils import (
    assert_empty_listing,
    container_interfaces,
    extract_exec_id,
    inspect,
    listing_ids,
    prune,
    remove_container,
    run,
    container_stopped_msg,
)


class TestNetworkSubcommand:
    # pylint: disable=no-self-use, unused-argument
    def test_assert_empty_network_listing_of_networks(self, testimage):
        assert_empty_listing("network ls")

    def test_add_remove_and_list_networks(self, testimage):
        name = "test_arl_networks"

        cmd = f"network create --interface testif --subnet 10.13.37.0/24 {name}"
        network_id, _ = run(cmd)
        assert len(network_id) == 12

        assert list_network_ids() == [network_id]

        network_id_remove, _ = run(f"network rm {name}")
        assert network_id_remove == network_id

        assert_empty_listing("network ls")

    def test_inspect_network(self, testimage):
        name = "test_network_inspect"
        cmd = f"network create --interface testif --subnet 10.13.37.0/24 {name}"
        network_id, _ = run(cmd)
        assert inspect("network", "notexist") == "network not found"
        network_endpoints = inspect("network", network_id)
        assert network_endpoints["network"]["name"] == name
        run(f"network rm {network_id}")

    def test_prune_network(self, testimage):
        cmd = "network create --interface testif1 --subnet 10.13.37.0/24 test_prune1"
        network_id1, _ = run(cmd)
        cmd = "network create --interface testif2 --subnet 10.13.38.0/24 test_prune2"
        network_id2, _ = run(cmd)
        assert set(prune("network")) == set([network_id1, network_id2])

    def test_prune_network_leaves_connected_networks_alone(self, testimage_and_cleanup):
        cmd = "network create --interface testif1 --subnet 10.13.37.0/24 test_prune_used"
        run(cmd)
        cmd = "network create --interface testif2 --subnet 10.13.38.0/24 test_prune_free"
        free_id, _ = run(cmd)
        run(
            "container create --name network_prune_test --network test_prune_used "
            "-l ipnet FreeBSD /bin/sleep 10"
        )

        assert prune("network") == [free_id]
        used_id = inspect("network", "test_prune_used")["network"]["id"]
        assert list_network_ids() == [used_id]

    def test_remove_a_network_that_does_not_exist(self, testimage):
        run("network create --subnet 10.13.37.0/24 test_rm_twice")
        run("network rm test_rm_twice")
        # NB: 'network rm' reports the failure but still exits 0, unlike
        # 'container rm', which exits 1 on "no such container".
        assert run("network rm test_rm_twice") == ["network not found.", ""]

    def test_remove_network_by_different_idents(self, testimage):
        network_id1, _ = run("network create --subnet 10.13.37.0/24 test_rm1")
        network_id2, _ = run("network create --subnet 10.13.38.0/24 test_rm2")
        network_id3, _ = run("network create --subnet 10.13.38.0/24 test_rm3")
        network_id1_again, _ = run(f"network rm {network_id1}")
        network_id2_again, _ = run(f"network rm {network_id2[:8]}")
        network_id3_again, _ = run("network rm test_rm3")
        assert network_id1 == network_id1_again
        assert network_id2 == network_id2_again
        assert network_id3 == network_id3_again
        assert_empty_listing("network ls")

    def test_create_a_internal_network(self, testimage):
        run("network create --internal --type loopback --subnet=10.13.38.0/24 testnet")
        network = inspect("network", "testnet")
        run("network rm testnet")
        assert network["network"]["internal"]

    def test_create_container_using_nonexisting_network(self, testimage):
        output = run(
            "container create --name invalid_network --network nonexisting FreeBSD /bin/ls",
            exit_code=1,
        )
        assert [
            "network not found",
            "could not connect container: network not found",
            "",
        ] == output[1:]
        remove_container("rmc invalid_network")

    def test_create_container_with_user_defined_ip_loopback(
        self, testimage_and_cleanup
    ):
        run("network create -t loopback --subnet 10.13.37.0/24 testnet9")
        container_id, _ = run(
            "container create --ip 10.13.37.13 --network testnet9 -l ipnet FreeBSD /bin/ls"
        )
        netstat_info = container_interfaces(container_id, ipv4_only=True)
        assert netstat_info[0]["address"] == "10.13.37.13"
        assert [""] == run(f"network disconnect testnet9 {container_id}")

    def test_create_container_with_user_defined_ip_vnet(self, testimage_and_cleanup):
        run("network create -t bridge --subnet 10.13.38.0/24 testnet9")
        container_id, _ = run(
            "container create --ip 10.13.38.13 --network testnet9 -l vnet FreeBSD /bin/ls"
        )
        netstat_info = container_interfaces(container_id, ipv4_only=True)
        assert netstat_info[0]["address"] == "10.13.38.13"
        assert [""] == run(f"network disconnect testnet9 {container_id}")

    def test_connect_container_with_user_defined_ip_loopback(
        self, testimage_and_cleanup
    ):
        container_name = "custom_ip3"
        network_name = "custom_ip3"
        run(f"network create -t loopback --subnet 10.13.37.0/24 {network_name}")
        cmd = f"container create --driver ipnet --name {container_name} FreeBSD /bin/ls"
        container_id, _ = run(cmd)
        run(f"network connect --ip 10.13.37.13 {network_name} {container_name}")
        netstat_info = container_interfaces(container_id, ipv4_only=True)
        assert netstat_info[0]["address"] == "10.13.37.13"
        assert [""] == run(f"network disconnect {network_name} {container_id}")

    def test_connect_container_with_user_defined_ip_vnet(self, testimage):
        container_name = "custom_ip3"
        network_name = "custom_ip3"
        cmd = f"network create -t loopback --interface testif -t bridge --subnet 10.13.38.0/24 {network_name}"
        network_id, _ = run(cmd)
        cmd = f"container create --name {container_name} --driver vnet FreeBSD /bin/ls"
        container_id, _ = run(cmd)

        run(f"network connect --ip 10.13.38.13 {network_name} {container_name}")
        netstat_info = container_interfaces(container_id, ipv4_only=True)
        assert netstat_info[0]["address"] == "10.13.38.13"
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        remove_container(f"rmc {container_id}")
        run(f"network rm {network_name}")

    def test_connect_and_disconnect_of_running_ipnet_container(self, testimage):
        run("network create -t loopback --subnet 10.13.37.0/24 test-ipnet")
        run("run --name disconn_ipnet -d -l ipnet FreeBSD sleep 10")

        assert not ip_in_container("disconn_ipnet", "10.13.37.1")
        assert [""] == run("network connect test-ipnet disconn_ipnet")
        assert ip_in_container("disconn_ipnet", "10.13.37.1")
        assert [""] == run("network disconnect test-ipnet disconn_ipnet")
        assert not ip_in_container("disconn_ipnet", "10.13.37.1")
        remove_container("rmc -f disconn_ipnet")
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
        remove_container("rmc -f disconn_vnet")
        run("network rm test-vnet")

    def test_remove_network_with_ipnet_running_stopped_containers_connected(
        self, testimage_and_cleanup
    ):
        run("network create -t bridge --subnet 10.20.30.0/24 testnet")
        run("run --name con_ipnet1 -n testnet -d -l ipnet FreeBSD sleep 10")
        run("run --name con_ipnet2 -n testnet -l ipnet FreeBSD /bin/ls")
        assert ip_in_container("con_ipnet1", "10.20.30.2")
        assert ip_in_container("con_ipnet2", "10.20.30.3")
        run("network rm testnet")
        assert not ip_in_container("con_ipnet1", "10.20.30.2")
        assert not ip_in_container("con_ipnet2", "10.20.30.3")
        run("stop con_ipnet1")

    def test_remove_network_with_vnet_running_stopped_containers_connected(
        self, testimage_and_cleanup
    ):
        run("network create -t bridge --subnet 10.20.30.0/24 testnet")
        run("run --name con_vnet1 -n testnet -l vnet FreeBSD sleep 10")
        run("run --name con_vnet2 -n testnet -d -l vnet FreeBSD /bin/ls")
        assert ip_in_container("con_vnet1", "10.20.30.2")
        assert ip_in_container("con_vnet2", "10.20.30.3")
        assert interface_in_container("con_vnet1", "epair0b")
        run("network rm testnet")
        assert not ip_in_container("con_vnet1", "10.20.30.2")
        assert not ip_in_container("con_vnet2", "10.20.30.3")
        assert not interface_in_container("con_vnet1", "epair0b")
        run("stop con_vnet1")

    def test_connectivity_of_container_connected_to_ipnet_network(self, testimage):
        network_id, _ = run("network create --subnet 10.13.37.0/24 test_conn")
        container_id, _ = run(
            "create -n test_conn -l ipnet FreeBSD /usr/bin/host -t A freebsd.org 1.1.1.1"
        )
        container_is_connected(container_id)
        remove_container(f"rmc {container_id}")
        run(f"network rm {network_id}")

    def test_connectivity_of_ipnet_container_on_a_bridge_network(self, testimage):
        # Same driver as the test above, different network type: NAT has to be
        # applied to a bridge interface rather than a loopback one.
        network_id, _ = run(
            "network create -t bridge --subnet 10.13.39.0/24 test_conn_bridge"
        )
        container_id, _ = run(
            "create -n test_conn_bridge -l ipnet FreeBSD /usr/bin/host -t A freebsd.org 1.1.1.1"
        )
        container_is_connected(container_id)
        remove_container(f"rmc {container_id}")
        run(f"network rm {network_id}")

    def test_connectivity_of_container_connected_to_vnet_network(self, testimage):
        network_id, _ = run("network create -t bridge --subnet 10.13.37.0/24 test_vnet")
        container_id, _ = run(
            "container create --name disconn_network --driver vnet --network test_vnet FreeBSD /usr/bin/host -t A freebsd.org 1.1.1.1"
        )
        container_is_connected(container_id, driver="vnet")
        remove_container(f"rmc {container_id}")
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


def container_is_connected(container_id, driver="loopback"):
    output = run(f"container start {container_id}")
    exec_id = extract_exec_id(output)
    if driver == "loopback":
        expected_prefix = [f"created execution instance {exec_id}"]
    elif driver == "vnet":
        expected_prefix = [
            f"created execution instance {exec_id}",
            "add net default: gateway 10.13.37.1",
        ]
    else:
        raise AssertionError(f"unknown driver used: {driver}")

    assert output[: len(expected_prefix)] == expected_prefix
    assert output[len(expected_prefix) : len(expected_prefix) + 5] == [
        "Using domain server:",
        "Name: 1.1.1.1",
        "Address: 1.1.1.1#53",
        "Aliases: ",
        "",
    ]
    # Assert the *shape* of the answer rather than freebsd.org's current A record,
    # which changes independently of Kleene.
    assert re.fullmatch(
        r"freebsd\.org has address \d{1,3}(\.\d{1,3}){3}",
        output[len(expected_prefix) + 5],
    )
    assert output[len(expected_prefix) + 6 :] == [
        "",
        container_stopped_msg(exec_id),
        "",
    ]


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


def list_network_ids():
    return listing_ids(run("network ls"))


def ip_in_container(container, ip):
    interfaces = container_interfaces(container)
    return ip in {interface["address"] for interface in interfaces}


def interface_in_container(container, interface_name):
    interfaces = container_interfaces(container)
    return interface_name in {interface["name"] for interface in interfaces}
