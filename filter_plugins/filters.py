def swarm_nodes_matching_field_value(hostvars, variable, field='stdout', nodes=None, value='true'):
    ret = []

    for node in hostvars.keys():
        if (
                (
                    nodes is None or
                    (
                        isinstance(nodes, list) and
                        node in nodes or
                        node == nodes
                    )
                ) and
                variable in hostvars[node] and
                field in hostvars[node][variable] and
                hostvars[node][variable][field] == value):
            ret.append(node)

    return ret


def swarm_nodes_membership(hostvars, value='active', nodes=None):
    variable = 'docker_swarm__check_membership_result'
    field = 'stdout'

    return swarm_nodes_matching_field_value(hostvars, variable, field, nodes, value)


def swarm_nodes_managership(hostvars, value='true', nodes=None):
    variable = 'docker_swarm__check_manager_result'
    field = 'stdout'

    return swarm_nodes_matching_field_value(hostvars, variable, field, nodes, value)


def swarm_nodes_xmote(hostvars, node, group, is_manager=True):
    ret = []

    active = swarm_nodes_membership(hostvars)
    managers = swarm_nodes_managership(hostvars)

    for n in hostvars:
        # Promote - node is active and is not manager and is in managers group
        # Demote  - node is active and is     manager and is in workers  group
        if (
                (
                    not is_manager and
                    n in active and
                    n not in managers and
                    n in group
                ) or (
                    is_manager and
                    n in active and
                    n in managers and
                    n in group
                )):
            ret.append(n)

    return ret


def swarm_nodes_availability(hostvars, avail_result, data, default):
    ret = []

    if avail_result is None or 'stdout_lines' not in avail_result:
        return ret

    nodes_avail = {}

    for line in avail_result['stdout_lines']:
        node, avail = line.split(':')
        nodes_avail[node] = avail

    for node in hostvars.keys():
        availability = default.lower()

        if node in nodes_avail:
            if node in data and 'availability' in data[node]:
                availability = data[node]['availability'].lower()

            if nodes_avail[node].lower() != availability:
                ret.append({'node': node, 'availability': availability})

    return ret


def swarm_nodes_remove(hostvars, node, data):
    ret = []

    for k, v in data.items():
        if (
                'state' in v and
                v['state'] == 'absent'):
            ret.append(k)

    return ret


def swarm_node_ip(hostvars, node, iface):
    iface_key = 'ansible_%s' % iface
    ip = None

    if (
            node in hostvars and
            iface_key in hostvars[node] and
            'ipv4' in hostvars[node][iface_key] and
            'address' in hostvars[node][iface_key]['ipv4']):
        ip = hostvars[node][iface_key]['ipv4']['address']

    return ip


def swarm_node_get_default_value(data, key, node, default=None):
    val = default

    if node in data and key in data[node]:
        val = data[node][key]

    return val


def swarm_node_iface(data, node, default=None):
    return swarm_node_get_default_value(data, 'iface', node, default)


def swarm_node_availability(data, node, default=None):
    return swarm_node_get_default_value(data, 'availability', node, default)


def swarm_node_get_field_value(hostvars, node, variable, field='stdout'):
    ret = None

    if (
            node in hostvars and
            variable in hostvars[node] and
            field in hostvars[node][variable]):
        ret = hostvars[node][variable][field]

    return ret


def swarm_node_set_labels(hostvars, node, data, default):
    ret = []

    if (
            node not in hostvars or
            'docker_swarm_labels_result' not in hostvars[node] or
            'results' not in hostvars[node]['docker_swarm_labels_result']):
        return ret

    current = {}

    for result in hostvars[node]['docker_swarm_labels_result']['results']:
        if 'item' in result and 'stdout_lines' in result:
            c_node = result['item']
            current[c_node] = {}

            for pair in result['stdout_lines']:
                k, v = pair.split('=', 1)

                current[c_node][k] = v

    required = {}

    for r_node in current.keys():
        required[r_node] = dict(default)

        if r_node in data and 'labels' in data[r_node]:
            required[r_node].update(data[r_node]['labels'])

    for n in current.keys():
        for k in set(current[n]) - set(required[n]):
            ret.append({'node': n, 'command': "--label-rm %s" % k})

        for k, v in required[n].items():
            if k not in current[n] or str(v) != current[n][k]:
                ret.append({'node': n, 'command': "--label-add %s=%s" % (k, v)})

    return ret


class FilterModule(object):
    def filters(self):

        return {
            'swarm_nodes_membership': swarm_nodes_membership,
            'swarm_nodes_managership': swarm_nodes_managership,
            'swarm_nodes_matching_field_value': swarm_nodes_matching_field_value,
            'swarm_nodes_xmote': swarm_nodes_xmote,
            'swarm_nodes_availability': swarm_nodes_availability,
            'swarm_nodes_remove': swarm_nodes_remove,
            'swarm_node_ip': swarm_node_ip,
            'swarm_node_iface': swarm_node_iface,
            'swarm_node_availability': swarm_node_availability,
            'swarm_node_get_field_value': swarm_node_get_field_value,
            'swarm_node_set_labels': swarm_node_set_labels,
        }
