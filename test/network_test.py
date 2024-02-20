import json

from testutils import (
    container_get_netstat_info,
    create_container,
    extract_exec_id,
    remove_all_containers,
    remove_container,
    inspect,
    prune,
    run,
    container_stopped_msg,
)


class TestNetworkSubcommand:
    @classmethod
    def setup_class(cls):
        remove_all_containers()
        remove_all_networks()

    # pylint: disable=no-self-use
    def test_assert_empty_network_listing_of_networks(self):
        assert_empty_network_list()

    def test_add_remove_and_list_networks(self):
        name = "test_arl_networks"

        cmd = f"network create --interface testif --subnet 10.13.37.0/24 {name}"
        network_id, _ = run(cmd)
        assert len(network_id) == 12

        networks = list_non_default_networks()
        assert len(networks) == 1
        assert networks[0][1:13] == network_id

        network_id_remove = remove_network(name)
        assert network_id_remove == network_id

        assert_empty_network_list()

    def test_inspect_network(self):
        name = "test_network_inspect"
        cmd = f"network create --interface testif --subnet 10.13.37.0/24 {name}"
        network_id, _ = run(cmd)
        assert inspect("network", "notexist") == "network not found"
        network_endpoints = inspect("network", network_id)
        assert network_endpoints["network"]["name"] == name
        remove_network(network_id)

    def test_prune_network(self):
        cmd = "network create --interface testif1 --subnet 10.13.37.0/24 test_prune1"
        network_id1, _ = run(cmd)
        cmd = "network create --interface testif2 --subnet 10.13.38.0/24 test_prune2"
        network_id2, _ = run(cmd)
        assert set(prune("network")) == set([network_id1, network_id2])

    def test_remove_network_by_id(self):
        network_id1, _ = run("network create --subnet 10.13.37.0/24 test_rm1")
        network_id2, _ = run("network create --subnet 10.13.38.0/24 test_rm2")
        network_id1_again = remove_network(network_id1)
        network_id2_again = remove_network(network_id2[:8])
        assert network_id1 == network_id1_again
        assert network_id2 == network_id2_again
        assert_empty_network_list()

    def test_create_container_connected_to_custom_network_with_ipnet_driver(self):
        network_id, _ = run("network create --subnet 10.13.37.0/24 test_conn")
        container_id, _ = run(
            "create -n test_conn -l ipnet FreeBSD:testing /usr/bin/host -t A freebsd.org 1.1.1.1"
        )
        container_is_connected(container_id)
        remove_container(container_id)
        remove_network(network_id)

    def test_create_container_connected_to_custom_vnet_network(self):
        network_id, _ = run("network create -t bridge --subnet 10.13.37.0/24 test_vnet")
        container_id, _ = run(
            "container create --name disconn_network --driver vnet --network test_vnet FreeBSD:testing /usr/bin/host -t A freebsd.org 1.1.1.1"
        )
        container_is_connected(container_id, driver="vnet")
        remove_container(container_id)
        remove_network(network_id)

    def test_connection_and_disconnecting_container_to_loopback_network(self):
        network_name = "test_nw_disconn"
        network_id, _ = run(f"network create --subnet 10.13.37.0/24 {network_name}")
        cmd = f"container create --name disconn_network --network {network_id} -l ipnet FreeBSD:testing /usr/bin/host -t A freebsd.org 1.1.1.1"
        container_id, _ = run(cmd)
        container_is_connected(container_id)
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        container_is_disconnected(container_id)
        remove_container(container_id)
        remove_network(network_id)

    def test_connection_and_disconnecting_container_to_vnet_network(self):
        network_name = "test_nw_disconn"
        cmd = f"network create -t bridge --subnet 10.13.37.0/24 {network_name}"
        network_id, _ = run(cmd)

        cmd = f"container create --name disconn_network2 --driver vnet --network {network_name} FreeBSD:testing /usr/bin/host -t A freebsd.org 1.1.1.1"
        container_id, _ = run(cmd)
        container_is_connected(container_id, driver="vnet")
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        container_is_disconnected(container_id)
        remove_container(container_id)
        remove_network(network_id)

    def test_create_container_with_user_defined_ip_loopback(self):
        container_name = "custom_ip1"
        network_name = "custom_ip1"
        cmd = f"network create -t loopback --subnet 10.13.37.0/24 {network_name}"
        network_id, _ = run(cmd)
        cmd = f"container create --name {container_name} --ip 10.13.37.13 --network {network_name} -l ipnet FreeBSD:testing /usr/bin/netstat --libxo json -i -4"
        container_id, _ = run(cmd)

        netstat_info = container_get_netstat_info(container_id, driver="loopback")
        assert netstat_info[0]["address"] == "10.13.37.13"
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        remove_container(container_id)
        remove_network(network_id)

    def test_create_container_with_user_defined_ip_vnet(self):
        container_name = "custom_ip2"
        network_name = "custom_ip2"
        cmd = f"network create -t bridge --subnet 10.13.38.0/24 {network_name}"
        network_id, _ = run(cmd)
        cmd = f"container create --name {container_name} --ip 10.13.38.13 --driver vnet --network {network_name} FreeBSD:testing /usr/bin/netstat --libxo json -i -4"
        container_id, _ = run(cmd)
        netstat_info = container_get_netstat_info(container_id, driver="vnet")
        assert netstat_info[0]["address"] == "10.13.38.13"
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        remove_container(container_id)
        remove_network(network_id)

    def test_connect_container_with_user_defined_ip_loopback(self):
        container_name = "custom_ip3"
        network_name = "custom_ip3"
        cmd = f"network create -t loopback --subnet 10.13.37.0/24 {network_name}"
        network_id, _ = run(cmd)
        cmd = f"container create --driver ipnet --name {container_name} FreeBSD:testing /usr/bin/netstat --libxo json -i -4"
        container_id, _ = run(cmd)
        run(f"network connect --ip 10.13.37.13 {network_name} {container_name}")
        netstat_info = container_get_netstat_info(container_id, driver="loopback")
        assert netstat_info[0]["address"] == "10.13.37.13"
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        remove_container(container_id)
        remove_network(network_id)

    def test_connect_container_with_user_defined_ip_vnet(self):
        container_name = "custom_ip3"
        network_name = "custom_ip3"
        cmd = f"network create -t loopback --interface testif -t bridge --subnet 10.13.38.0/24 {network_name}"
        network_id, _ = run(cmd)
        cmd = f"container create --name {container_name} --driver vnet FreeBSD:testing /usr/bin/netstat --libxo json -i -4"
        container_id, _ = run(cmd)

        run(f"network connect --ip 10.13.38.13 {network_name} {container_name}")
        netstat_info = container_get_netstat_info(container_id, driver="vnet")
        assert netstat_info[0]["address"] == "10.13.38.13"
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        remove_container(container_id)
        remove_network(network_id)

    def test_create_a_internal_network(self):
        network_id, _ = run(
            "network create --internal --type loopback --subnet=10.13.38.0/24 testnet"
        )

        network_json = run(f"network inspect {network_id}")
        network = json.loads("".join(network_json))
        assert network["network"]["internal"]

    def test_create_container_using_nonexisting_network(self):
        output = run(
            "container create --name invalid_network --network nonexisting FreeBSD:testing /bin/ls"
        )
        assert [
            "network not found",
            "could not connect container: network not found",
            "",
        ] == output[1:]


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


def remove_all_networks():
    networks = list_non_default_networks()
    for network in networks:
        # if network == "":
        #    continue
        remove_network(network[1:13])


def list_non_default_networks():
    _header, _header_line, *networks = run("network ls")
    return networks[:-1]


def assert_empty_network_list():
    expected_output = [" ID   NAME   TYPE   SUBNET ", "───────────────────────────", ""]
    output = run("network ls")
    assert expected_output == output


def remove_network(network_id):
    network_id, _ = run(f"network rm {network_id}")
    return network_id


def network_create(command):
    network_id, _ = run(f"network create {command}")
    return network_id


def create_network(name, ifname, subnet, driver="loopback"):
    network_id, _ = run(
        f"network create --ifname {ifname} --subnet {subnet} --driver {driver} {name}"
    )
    return network_id
