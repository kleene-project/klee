from testutils import run, remove_all_containers


class TestNetworkSubcommand:
    @classmethod
    def setup_class(cls):
        remove_all_containers()
        remove_all_networks()

    # pylint: disable=no-self-use
    def test_empty_network_listing_of_networks(self):
        assert empty_network_list()

    def test_add_remove_and_list_networks(self):
        name = "test_arl_networks"
        network_id = create_network(name, ifname="testif", subnet="10.13.37.0/24")
        assert len(network_id) == 12

        networks = list_non_default_networks()
        assert len(networks) == 1
        assert networks[0][:12] == network_id

        network_id_remove = remove_network(name)
        assert network_id_remove == network_id

        assert empty_network_list()


    def test_remove_network_by_id(self):
        name1 = "test_remove1"
        name2 = "test_remove2"
        network_id1 = create_network(name1, ifname="testif0", subnet="10.13.37.0/24")
        network_id2 = create_network(name2, ifname="testif1", subnet="10.13.37.1/24")
        network_id1_again = remove_network(network_id1)
        network_id2_again = remove_network(network_id2)
        assert network_id1 == network_id1_again
        assert network_id2 == network_id2_again


def remove_all_networks():
    networks = list_non_default_networks()
    for network in networks:
        remove_network(network[:12])


def list_non_default_networks():
    _header, _header_line, _default_network, _host_network, *networks, _, _ = run("network ls")
    return networks


def empty_network_list():
    HEADER = 'ID            NAME     DRIVER    SUBNET'
    HEADER_LINE = '------------  -------  --------  -------------'
    DEFAULT_NETWORK = '  default  loopback  172.17.0.0/16'
    HOST_NETWORK = 'host          host     host'
    header, header_line, default_network, host_network, _, _ = run("network ls")
    assert header == HEADER
    assert header_line == HEADER_LINE
    assert default_network[12:] == DEFAULT_NETWORK
    assert host_network == HOST_NETWORK
    return True


def remove_network(network_id):
    network_id, _ = run(f"network rm {network_id}")
    return network_id


def create_network(name, ifname, subnet, driver="loopback"):
    network_id, _ = run(f"network create --ifname {ifname} --subnet {subnet} --driver {driver} {name}")
    return network_id
