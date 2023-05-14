def bytes_ns(dictionary, host):
    result = f''
    # print(dictionary)
    for ns in dictionary['ns']:
        # print(ns)
        if dictionary['ns'][ns] and len(dictionary['ns'][ns]) == 2:
            result += f'{ns} internet address = {dictionary["ns"][ns][0]}\n{ns} ' \
                      f'has AAAA address {dictionary["ns"][ns][1]}\n'
        elif dictionary['ns'][ns] and dictionary['ns'][ns][0]:
            result += f'{ns} internet address = {dictionary["ns"][ns][0]}\n'
        else:
            result = f'no authoritative answers or incorrect host\n'
    return bytes(result, "utf-8")


def bytes_a(dictionary, host):
    result = f''
    for address in dictionary['a']:
        result += f'Name: {host}\nAddress: {address}\n'
    return bytes(result, "utf-8")


def bytes_soa(dictionary, host):
    # print(dictionary)
    result = f'origin = {dictionary["soa"][0]}\nmail addr = {dictionary["soa"][1]}\n' \
         f'serial = {dictionary["soa"][2]}\nrefresh = {dictionary["soa"][3]}\n' \
         f'retry = {dictionary["soa"][4]}\nexpire = {dictionary["soa"][5]}\n' \
         f'minimum = {dictionary["soa"][6]}\n'
    return bytes(result, "utf-8")
