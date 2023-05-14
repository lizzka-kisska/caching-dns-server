import datetime
import re
import subprocess

reg_ex_ns = re.compile(r'nameserver = (.+)')
reg_ex_ip4 = re.compile(r'(.+)\tinternet address = (.+)')
reg_ex_ip6 = re.compile(r'(.+)\thas AAAA address (.+)')
reg_ex_a = re.compile(r'Address: (.+)')
reg_ex_soa = re.compile(r'.+= (.+)')


def request_data(host, request_type):
    command = f'nslookup -type={request_type} ' + host
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        return error
    look_up_result = output.decode("utf=8")
    if look_up_result.find('**') != -1:
        return {}
    elif look_up_result.find(';;') != -1:
        return {'no servers': ''}
    # print(look_up_result)
    # return output.decode("utf=8")
    match request_type:
        case 'ns':
            return create_ns_dict(look_up_result)
        case 'a':
            return create_a_dict(look_up_result)
        case 'soa':
            return create_soa_dict(look_up_result)


def create_ns_dict(look_up_result):
    servers = reg_ex_ns.findall(look_up_result)
    address_v4 = reg_ex_ip4.findall(look_up_result)
    address_v6 = reg_ex_ip6.findall(look_up_result)
    data = dict()
    data = {'ns': {}, 'ttl': str(datetime.datetime.now())}
    for ns in servers:
        data['ns'][ns[:-1]] = []
    for ip4 in address_v4:
        data['ns'][ip4[0]].append(ip4[1])
    for ip6 in address_v6:
        data['ns'][ip6[0]].append(ip6[1])
    # print(data)
    return data


def create_a_dict(look_up_result):
    addresses = reg_ex_a.findall(look_up_result)
    data = dict()
    data = {'a': addresses, 'ttl': str(datetime.datetime.now())}
    return data


def create_soa_dict(look_up_result):
    records = reg_ex_soa.findall(look_up_result)
    data = dict()
    data = {'soa': records, 'ttl': str(datetime.datetime.now())}
    return data
