docker_swarm
============

Ansible role which helps to install and configure Docker Swarm cluster.

Supported actions:
 - Cluster initiation
 - Adding nodes
 - Rebuilding nodes
 - Removing nodes
 - Promoting/demoting nodes
 - Setting node's labels
 - Setting node's availability

The configuration of the role is done in such way that it should not be
necessary to change the role for any kind of configuration. All can be
done either by changing role parameters or by declaring completely new
configuration as a variable. That makes this role absolutely
universal. See the examples below for more details.

Please report any issues or send PR.


Examples
--------

Role of the node (manager/worker) is controlled by presence of the nodes in the
particular Ansible inventory group. Examples bellow assume the following
inventory:

```ini
[swarm:children]
managers
workers

[managers]
swarm01
swarm03
swarm05

[workers]
swarm02
swarm04
```

The group names can be controled by setting the `docker_swarm_group*` variables.


```yaml
---

- name: Example of how to initiate the cluster
  hosts: swarm
  roles:
    - role: docker
      tags: docker
    - role: docker_swarm
      tags: docker_swarm
      # Skip all docker_swarm tasks if we are not deploying to all Swarm cluster nodes
      when: >
        groups[docker_swarm_group] | difference(ansible_play_batch) | length == 0

- name: Example of how to set global labels (labels on all nodes)
  hosts: swarm
  vars:
    docker_swarm_node_labels:
      # Sets label cluster=test_cluster to all nodes
      cluster: test_cluster
  roles:
    - role: docker
      tags: docker
    - role: docker_swarm
      tags: docker_swarm
      # Skip all docker_swarm tasks if we are not deploying to all Swarm cluster nodes
      when: >
        groups[docker_swarm_group] | difference(ansible_play_batch) | length == 0

- name: Example of how configure individual nodes
  hosts: swarm
  vars:
    docker_swarm_nodes:
      swarm01:
        labels:
          # Sets additional label app=test
          app: test
        # Do not run any tasks on this node
        availability: drain
      swarm03:
        # Use eth1 to communicate with the cluster
        iface: eth1
      swarm05:
        # Remove the node swarm05 from the cluster
        # (the node can be removed from the inventory after the change was applied)
        state: absent
  roles:
    - role: docker
      tags: docker
    - role: docker_swarm
      tags: docker_swarm
      # Skip all docker_swarm tasks if we are not deploying to all Swarm cluster nodes
      when: >
        groups[docker_swarm_group] | difference(ansible_play_batch) | length == 0
```

New node can be added into the cluster by simply adding it into the inventory.
Node can be rebuild by destroying the node and running the role again on all
cluster. Promote/demote node to master/worker is simply done by moving the
node between the inventory groups. 


Role variables
--------------

Variables used by the role:

```yaml
# Group name for all nodes in the cluster (managers + workers)
docker_swarm_group: swarm

# Group name for manager nodes
docker_swarm_group_managers: managers

# Group name for worker nodes
docker_swarm_group_workers: workers

# Default node network interface through which the nodes in the cluster communicate
docker_swarm_node_iface: eth0

# Default node availability mode
docker_swarm_node_availability: active

# Default node labels
docker_swarm_node_labels: {}

# List of cluster nodes and their attributes (see examples in the README for details)
docker_swarm_nodes: {}
```


Limitations
-----------

- Node hostnames must be unique.
- Always run the play on all nodes of the cluster (all nodes of the group
  defined by the `docker_swarm_group` variable).
- It's not possible to demote all masters and promote all workers. There must
  always stay at least one master which doesn't change the role.
- Variable `docker_swarm_nodes` must be uniform across all nodes.


Dependencies
------------

- [`docker`](https://github.com/jtyr/ansible-docker) (optional)


License
-------

MIT


Author
------

Jiri Tyr
