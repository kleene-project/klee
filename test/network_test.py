from testutils import (
    container_get_netstat_info,
    create_container,
    extract_exec_id,
    remove_all_containers,
    remove_container,
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
        network_id = create_network(name, ifname="testif", subnet="10.13.37.0/24")
        assert len(network_id) == 12

        networks = list_non_default_networks()
        assert len(networks) == 1
        assert networks[0][1:13] == network_id

        network_id_remove = remove_network(name)
        assert network_id_remove == network_id

        assert_empty_network_list()

    def test_remove_network_by_id(self):
        name1 = "test_network_rm1"
        name2 = "test_network_rm2"
        network_id1 = create_network(name1, ifname="testif0", subnet="10.13.37.0/24")
        network_id2 = create_network(name2, ifname="testif1", subnet="10.13.37.1/24")
        network_id1_again = remove_network(network_id1)
        network_id2_again = remove_network(network_id2[:8])
        assert network_id1 == network_id1_again
        assert network_id2 == network_id2_again
        assert_empty_network_list()

    def test_create_container_connected_to_custom_network_with_default_driver(self):
        network_id = create_network(
            "test_create_conn", ifname="testif", subnet="10.13.37.0/24"
        )
        container_id = create_container(
            name="test_disconn_network",
            command="/usr/bin/host -t A freebsd.org 1.1.1.1",
            network="test_create_conn",
        )
        container_is_connected(container_id)
        remove_container(container_id)
        remove_network(network_id)

    def test_create_container_connected_to_custom_vnet_network(self):
        network_id = create_network(
            "test_vnet", ifname="testif", subnet="10.13.37.0/24", driver="vnet"
        )
        container_id = create_container(
            name="test_disconn_network",
            command="/usr/bin/host -t A freebsd.org 1.1.1.1",
            network="test_vnet",
        )
        container_is_connected(container_id, driver="vnet")
        remove_container(container_id)
        remove_network(network_id)

    def test_connection_and_disconnecting_container_to_loopback_network(self):
        container_name = "test_disconn_network"
        network_name = "test_nw_disconn"
        network_id = create_network(
            network_name, ifname="testif", subnet="10.13.37.0/24", driver="loopback"
        )
        container_id = create_container(
            name=container_name,
            command="/usr/bin/host -t A freebsd.org 1.1.1.1",
            network=network_name,
        )
        container_is_connected(container_id)
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        container_is_disconnected(container_id)
        remove_container(container_id)
        remove_network(network_id)

    def test_connection_and_disconnecting_container_to_vnet_network(self):
        container_name = "test_disconn_network"
        network_name = "test_nw_disconn"
        network_id = create_network(
            network_name, ifname="testif", subnet="10.13.37.0/24", driver="vnet"
        )
        container_id = create_container(
            name=container_name,
            command="/usr/bin/host -t A freebsd.org 1.1.1.1",
            network=network_name,
        )
        container_is_connected(container_id, driver="vnet")
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        container_is_disconnected(container_id)
        remove_container(container_id)
        remove_network(network_id)

    def test_create_container_with_user_defined_ip_loopback(self):
        container_name = "custom_ip1"
        network_name = "custom_ip1"
        network_id = create_network(
            network_name, ifname="testif", subnet="10.13.37.0/24", driver="loopback"
        )
        container_id = create_container(
            name=container_name,
            command="/usr/bin/netstat --libxo json -i -4",
            network=network_name,
            ip="10.13.37.13",
        )
        netstat_info = container_get_netstat_info(container_id, driver="loopback")
        assert netstat_info[0]["address"] == "10.13.37.13"
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        remove_container(container_id)
        remove_network(network_id)

    def test_create_container_with_user_defined_ip_vnet(self):
        container_name = "custom_ip2"
        network_name = "custom_ip2"
        network_id = create_network(
            network_name, ifname="testif", subnet="10.13.38.0/24", driver="vnet"
        )
        container_id = create_container(
            name=container_name,
            command="/usr/bin/netstat --libxo json -i -4",
            network=network_name,
            ip="10.13.38.13",
        )
        netstat_info = container_get_netstat_info(container_id, driver="vnet")
        assert netstat_info[0]["address"] == "10.13.38.13"
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        remove_container(container_id)
        remove_network(network_id)

    def test_connect_container_with_user_defined_ip_loopback(self):
        container_name = "custom_ip3"
        network_name = "custom_ip3"
        network_id = create_network(
            network_name, ifname="testif", subnet="10.13.37.0/24", driver="loopback"
        )
        container_id = create_container(
            name=container_name, command="/usr/bin/netstat --libxo json -i -4"
        )
        run(f"network connect --ip 10.13.37.13 {network_name} {container_name}")
        netstat_info = container_get_netstat_info(container_id, driver="loopback")
        assert netstat_info[0]["address"] == "10.13.37.13"
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        remove_container(container_id)
        remove_network(network_id)

    def test_connect_container_with_user_defined_ip_vnet(self):
        container_name = "custom_ip3"
        network_name = "custom_ip3"
        network_id = create_network(
            network_name, ifname="testif", subnet="10.13.38.0/24", driver="vnet"
        )
        container_id = create_container(
            name=container_name, command="/usr/bin/netstat --libxo json -i -4"
        )
        run(f"network connect --ip 10.13.38.13 {network_name} {container_name}")
        netstat_info = container_get_netstat_info(container_id, driver="vnet")
        assert netstat_info[0]["address"] == "10.13.38.13"
        assert [""] == run(f"network disconnect {network_name} {container_id}")
        remove_container(container_id)
        remove_network(network_id)

    def test_create_container_using_nonexisting_network(self):
        output = run(
            "container create --name invalid_network --network nonexisting base /bin/ls"
        )
        assert ["network not found", ""] == output[1:]


def container_is_connected(container_id, driver="loopback"):
    output = run(f"container start --attach {container_id}")
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
            "add net default: gateway 10.13.37.0",
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
    output = run(f"container start --attach {container_id}")
    exec_id = extract_exec_id(output)
    disconnected_output = [
        f"created execution instance {exec_id}",
        ";; connection timed out; no servers could be reached",
        "jail: /usr/bin/env -i /usr/bin/host -t A freebsd.org 1.1.1.1: failed",
        "",
        container_stopped_msg(exec_id, 1),
        "",
    ]
    assert disconnected_output == output


def remove_all_networks():
    networks = list_non_default_networks()
    for network in networks:
        if network[:4] == "host":
            continue
        remove_network(network[1:13])


def list_non_default_networks():
    tmp = run("network ls")
    _header, _header_line, _host_network, *networks, _ = tmp
    return networks


def assert_empty_network_list():
    expected_output = [
        " ID     NAME   DRIVER   SUBNET ",
        "───────────────────────────────",
        " host   host   host     n/a    ",
        "",
    ]
    output = run("network ls")
    assert expected_output == output


def remove_network(network_id):
    network_id, _ = run(f"network rm {network_id}")
    return network_id


def create_network(name, ifname, subnet, driver="loopback"):
    network_id, _ = run(
        f"network create --ifname {ifname} --subnet {subnet} --driver {driver} {name}"
    )
    return network_id
