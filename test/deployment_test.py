import os
import json
from testutils import run, inspect, create_dockerfile

from klee.deploy import DEFAULT_DEPLOYMENT_FILE

# pylint: disable=unused-argument


def test_diff_an_existing_container(cleanup):
    deployment = """
---
containers:
 - name: "testcon1"
   image: "FreeBSD:latest"
 - name: "testcon2"
   image: "FreeBSD"
"""
    run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")
    run("container create --name testcon1 FreeBSD:latest")
    run("container create --name testcon2 FreeBSD:latest")
    assert _deploy_diff(deployment) == _diff_result()
    run("rmc testcon1")
    run("rmc testcon2")
    run("rmi FreeBSD:latest")


def test_diff_a_valid_container_endpoint(testimage_and_cleanup):
    deployment = """
---
containers:
 - name: "testcon"
   image: "FreeBSD:latest"
   endpoints:
       - network: testnet

networks:
 - name: "testnet"
   subnet: "10.13.37.0/24"
"""
    run("network create --subnet 10.13.37.0/24 testnet")
    run("container create --network testnet --name testcon FreeBSD:latest")
    assert _deploy_diff(deployment) == _diff_result()
    run("rmc testcon")
    run("rmn testnet")


def test_diff_existing_container_and_existing_mounts(testimage_and_cleanup):
    deployment = """
---
containers:
 - name: "testcon"
   image: "FreeBSD:latest"
   mounts:
       - type: volume
         source: teststorage
         destination: "/mnt/storage"

       - type: nullfs
         source: "/usr/local/man"
         destination: "/mnt/test_man"

volumes:
 - name: teststorage
"""
    run("volume create teststorage")
    run(
        "container create -m teststorage:/mnt/storage -m /usr/local/man:/mnt/test_man --name testcon FreeBSD:latest"
    )
    assert _deploy_diff(deployment) == _diff_result()
    run("rmc testcon")
    run("rmv teststorage")


def test_diff_nonexisting_container(cleanup):
    deployment = """
---
containers:
 - name: "testcon1"
   image: "FreeBSD:latest"
"""
    assert _deploy_diff(deployment) == _diff_result(
        containers={"testcon1": [{"type": "missing_on_host"}]}
    )


def test_diff_container_with_diverging_user_and_cmd(cleanup):
    deployment = """
---
containers:
 - name: "testcon1"
   image: "FreeBSD:latest"
   cmd: ["/bin/ls"]
   user: "ntpd"
"""
    run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")
    run("container create --name testcon1 FreeBSD:latest")
    assert _deploy_diff(deployment) == _diff_result(
        containers={
            "testcon1": [
                {
                    "property": "cmd",
                    "type": "not_equal",
                    "value_host": [
                        "/bin/sh",
                        "/etc/rc",
                    ],
                    "value_spec": [
                        "/bin/ls",
                    ],
                },
                {
                    "property": "user",
                    "type": "not_equal",
                    "value_host": "root",
                    "value_spec": "ntpd",
                },
            ]
        }
    )
    run("rmc testcon1")
    run("rmi FreeBSD:latest")


def test_diff_container_having_nonexisting_network(testimage_and_cleanup):
    deployment = """
---
containers:
 - name: "testcon"
   image: "FreeBSD:latest"
   endpoints:
       - network: testnet
"""
    run("container create --driver ipnet --name testcon FreeBSD:latest")
    assert _deploy_diff(deployment) == _diff_result(
        containers={
            "testcon": [
                {
                    "network": "testnet",
                    "type": "non_existing_network",
                }
            ]
        }
    )
    run("rmc testcon")


def test_diff_container_having_nonexisting_endpoint(testimage_and_cleanup):
    deployment = """
---
containers:
 - name: "testcon"
   image: "FreeBSD:latest"
   endpoints:
       - network: testnet

networks:
 - name: "testnet"
   subnet: "10.13.37.0/24"
"""
    run("network create --subnet 10.13.37.0/24 testnet")
    run("container create --driver ipnet --name testcon FreeBSD:latest")
    assert _deploy_diff(deployment) == _diff_result(
        containers={
            "testcon": [
                {
                    "container": "testcon",
                    "network": "testnet",
                    "type": "not_connected",
                },
            ],
        }
    )

    run("rmc testcon")
    run("rmn testnet")


def test_diff_container_with_endpoint_having_different_ip_addresses(
    testimage_and_cleanup,
):
    deployment = """
---
containers:
 - name: "testcon"
   image: "FreeBSD:latest"
   endpoints:
       - network: testnet
         ip_address: 10.13.37.137

networks:
 - name: "testnet"
   subnet: "10.13.37.0/24"
"""
    run("network create --subnet 10.13.37.0/24 testnet")
    run("container create --network testnet --name testcon FreeBSD:latest")
    assert _deploy_diff(deployment) == _diff_result(
        containers={
            "testcon": [
                {
                    "property": "ip_address",
                    "type": "not_equal",
                    "value_host": "10.13.37.1",
                    "value_spec": "10.13.37.137",
                },
            ],
        }
    )
    run("rmc testcon")
    run("rmn testnet")


def test_diff_container_having_nonexisting_volume_mount(testimage_and_cleanup):
    deployment = """
---
containers:
 - name: "testcon"
   image: "FreeBSD:latest"
   mounts:
       - type: volume
         source: teststorage
         destination: "/mnt/storage"

volumes:
 - name: teststorage
"""
    run("volume create teststorage")
    run(
        "container create -m /usr/local/man:/mnt/test_man --name testcon FreeBSD:latest"
    )
    assert _deploy_diff(deployment) == _diff_result(
        containers={
            "testcon": [
                {
                    "destination": "/mnt/storage",
                    "source": "volume:teststorage",
                    "type": "mount_not_found",
                }
            ]
        }
    )
    run("rmc testcon")
    run("rmv teststorage")


def test_diff_container_having_mounted_volume_not_found(testimage_and_cleanup):
    deployment = """
---
containers:
 - name: "testcon"
   image: "FreeBSD:latest"
   mounts:
       - type: volume
         source: teststorage
         destination: "/mnt/storage"

volumes:
 - name: teststorage
"""
    run(
        "container create -m /usr/local/man:/mnt/test_man --name testcon FreeBSD:latest"
    )
    assert _deploy_diff(deployment) == _diff_result(
        containers={
            "testcon": [
                {"type": "mounted_volume_not_found", "volume_name": "teststorage"}
            ]
        }
    )
    run("rmc testcon")


def test_diff_container_having_nonexisting_nullfs_mount(testimage_and_cleanup):
    deployment = """
---
containers:
 - name: "testcon"
   image: "FreeBSD:latest"
   mounts:
       - type: nullfs
         source: "/usr/local/man"
         destination: "/mnt/test_man"
"""
    run("container create --name testcon FreeBSD:latest")
    assert _deploy_diff(deployment) == _diff_result(
        containers={
            "testcon": [
                {
                    "destination": "/mnt/test_man",
                    "source": "nullfs:/usr/local/man",
                    "type": "mount_not_found",
                }
            ]
        }
    )
    run("rmc testcon")


def test_diff_container_with_mounts_having_different_readonly(testimage_and_cleanup):
    deployment = """
---
containers:
 - name: "testcon"
   image: "FreeBSD:latest"
   mounts:
       - type: volume
         source: teststorage
         destination: "/mnt/storage"
         read_only: true

       - type: nullfs
         source: "/usr/local/man"
         destination: "/mnt/test_man"
         read_only: true

volumes:
 - name: teststorage
"""
    run("volume create teststorage")
    run(
        "container create -m teststorage:/mnt/storage -m /usr/local/man:/mnt/test_man --name testcon FreeBSD:latest"
    )
    assert _deploy_diff(deployment) == _diff_result(
        {
            "testcon": [
                {
                    "destination": "/mnt/test_man",
                    "source": "nullfs:/usr/local/man",
                    "type": "mount_readonly_diff",
                },
                {
                    "destination": "/mnt/storage",
                    "source": "volume:teststorage",
                    "type": "mount_readonly_diff",
                },
            ]
        }
    )
    run("rmc testcon")
    run("rmv teststorage")


def test_diff_container_with_mounts_having_different_sources(testimage_and_cleanup):
    deployment = """
---
containers:
 - name: "testcon"
   image: "FreeBSD:latest"
   mounts:
       - type: volume
         source: teststorage2
         destination: "/mnt/storage"

       - type: nullfs
         source: "/usr/local/man1"
         destination: "/mnt/test_man"

volumes:
 - name: teststorage
 - name: teststorage2
"""
    run("volume create teststorage")
    run("volume create teststorage2")
    run(
        "container create -m teststorage:/mnt/storage -m /usr/local/man:/mnt/test_man --name testcon FreeBSD:latest"
    )
    assert _deploy_diff(deployment) == _diff_result(
        {
            "testcon": [
                {
                    "host_source": "nullfs:/usr/local/man",
                    "spec_source": "nullfs:/usr/local/man1",
                    "type": "mount_unequal_source",
                },
                {
                    "host_source": "volume:teststorage",
                    "spec_source": "volume:teststorage2",
                    "type": "mount_unequal_source",
                },
            ]
        }
    )
    run("rmc testcon")
    run("rmv teststorage")
    run("rmv teststorage2")


def test_diff_container_with_mounts_having_different_destinations(
    testimage_and_cleanup,
):
    deployment = """
---
containers:
  - name: "testcon"
    image: "FreeBSD:latest"
    mounts:
        - type: volume
          source: teststorage
          destination: "/mnt/new_storage"

        - type: nullfs
          source: "/usr/local/man"
          destination: "/mnt/new_test_man"

volumes:
  - name: teststorage
"""
    run("volume create teststorage")
    run(
        "container create -m teststorage:/mnt/storage -m /usr/local/man:/mnt/test_man --name testcon FreeBSD:latest"
    )
    assert _deploy_diff(deployment) == _diff_result(
        containers={
            "testcon": [
                {
                    "host_destination": "/mnt/test_man",
                    "spec_destination": "/mnt/new_test_man",
                    "type": "mount_unequal_destination",
                },
                {
                    "host_destination": "/mnt/storage",
                    "spec_destination": "/mnt/new_storage",
                    "type": "mount_unequal_destination",
                },
            ]
        }
    )
    run("rmc testcon")
    run("rmv teststorage")


def test_network_with_different_interface(cleanup):
    deployment = """
---
networks:
 - name: "testnet"
   subnet: "10.13.37.0/24"
   interface: testif0
"""
    run("network create --subnet 10.13.37.0/24 testnet")
    assert _deploy_diff(deployment) == _diff_result(
        networks={
            "testnet": [
                {
                    "property": "interface",
                    "type": "not_equal",
                    "value_host": "kleene0",
                    "value_spec": "testif0",
                }
            ]
        }
    )
    run("rmn testnet")


def test_network_with_different_subnet():
    deployment = """
---
networks:
 - name: "testnet"
   subnet: "10.13.38.0/24"
"""
    run("network create --subnet 10.13.37.0/24 testnet")
    assert _deploy_diff(deployment) == _diff_result(
        networks={
            "testnet": [
                {
                    "property": "subnet",
                    "type": "not_equal",
                    "value_host": "10.13.37.0/24",
                    "value_spec": "10.13.38.0/24",
                }
            ]
        }
    )
    run("rmn testnet")


def test_network_with_different_nat():
    deployment = """
---
networks:
 - name: "testnet"
   subnet: "10.13.37.0/24"
   nat: ""
"""
    run("network create --subnet 10.13.37.0/24 testnet")
    assert _deploy_diff(deployment) == _diff_result(
        networks={
            "testnet": [
                {
                    "property": "nat",
                    "type": "not_equal",
                    "value_host": "em0",
                    "value_spec": "",
                }
            ]
        }
    )
    run("rmn testnet")


# def test_diff_existing_container_wrong_image_snapshot():


class TestDeploymentImageCreate:

    def test_existing_and_correct_image(self, cleanup):
        deployment = """
---
images:
  - tag: "FreeBSD:latest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"
"""
        run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")
        assert _deploy_diff(deployment) == _diff_result()
        run("rmi FreeBSD:latest")

    def test_image_created_with_different_method_zfsclone(self, cleanup):
        deployment = """
---
images:
  - tag: "FreeBSD:latest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"
"""
        url = "file:///home/vagrant/kleened/test/data/minimal_testjail.txz"
        run(f"image create -t FreeBSD:latest fetch {url}")

        assert _deploy_diff(deployment) == _diff_result(
            images={
                "FreeBSD:latest": [
                    {
                        "image": "FreeBSD:latest",
                        "type": "base_image_wrong_dataset_origin",
                        "origin": None,
                    }
                ]
            }
        )
        run("rmi FreeBSD:latest")

    def test_image_created_with_different_method_fetch(self, cleanup):
        deployment = """
---
images:
  - tag: "FreeBSD:latest"
    method: "fetch"
    url: "file:///home/vagrant/kleened/test/data/minimal_testjail.txz"
"""
        run("image create -t FreeBSD:latest zfs-clone zroot/kleene_basejail")

        assert _deploy_diff(deployment) == _diff_result(
            images={
                "FreeBSD:latest": [
                    {
                        "image": "FreeBSD:latest",
                        "type": "base_image_wrong_dataset_origin",
                        "origin": "zroot/kleene_basejail",
                    }
                ]
            }
        )
        run("rmi FreeBSD:latest")

    def test_image_built_instead_of_created(self, cleanup):
        deployment = """
---
images:
  - tag: "FreeBSD:latest"
    method: "zfs-clone"
    zfs_dataset: "zroot/kleene_basejail"
"""
        run("image create -t FreeBSD:hidden zfs-clone zroot/kleene_basejail")
        create_dockerfile(["FROM FreeBSD:hidden", "RUN echo 'testing'"])
        run(f"build -t FreeBSD:latest {os.getcwd()}")

        image_id = inspect("image", "FreeBSD:hidden")["id"]
        assert _deploy_diff(deployment) == _diff_result(
            images={
                "FreeBSD:latest": [
                    {
                        "image": "FreeBSD:latest",
                        "type": "base_image_nonempty_instructions",
                    },
                    {
                        "image": "FreeBSD:latest",
                        "origin": f"zroot/kleene/image/{image_id}",
                        "type": "base_image_wrong_dataset_origin",
                    },
                ]
            }
        )
        run("rmi FreeBSD:latest")
        run("rmi FreeBSD:hidden")


def _deploy_diff(deployment):
    _create_deployment_file(deployment)
    result = "\n".join(run("deploy diff --json"))
    return json.loads(result)


def _diff_result(containers=None, images=None, networks=None):
    if containers is None:
        containers = {}

    if images is None:
        images = {}

    if networks is None:
        networks = {}

    return {"containers": containers, "images": images, "networks": networks}


def _create_deployment_file(content, path=DEFAULT_DEPLOYMENT_FILE):
    with open(DEFAULT_DEPLOYMENT_FILE, "w", encoding="utf8") as deploy_file:
        deploy_file.write(content)
