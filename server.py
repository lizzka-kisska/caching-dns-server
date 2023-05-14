import datetime
import json
import socket

from creating_result import bytes_ns, bytes_a, bytes_soa
from updating_data import request_data

with open('cache.json', encoding="utf-8") as file:
    try:
        DICTIONARY = json.load(file)
    except json.decoder.JSONDecodeError:
        DICTIONARY = {'domain': []}


def parse_recv(line):
    try:
        if not line[0].endswith('.'):
            return b'The host name must end with a dot\n', ''
        if line[1] != 'ns' and line[1] != 'a' and line[1] != 'soa':
            return b'The record must be of type ns, a, soa\n', ''
        return line[0], line[1]
    except IndexError:
        return b'The host name must end with a dot and ' \
               b'the record must be of type ns, a, soa\n', ''


def check_cache(host, req_type, check_fresh):
    tmp = dict()
    for i in DICTIONARY['domain']:
        if host in i.keys() and req_type in i[host].keys():
            if check_fresh and check_ttl(i[host]['time'], i[host]['ttl']):
                tmp = i[host]
                return tmp
            elif not check_fresh:
                tmp = i[host]
                return tmp
    return tmp


def check_ttl(req_time, ttl):
    date, time = req_time.split(' ')
    d, t = date.split('-'), time.split(':')
    time1 = datetime.datetime.now()
    time2 = datetime.datetime(int(d[0]), int(d[1]), int(d[2]), int(t[0]), int(t[1]), int(t[2].split('.')[0]))

    time_res = time1 - time2

    if int(ttl) - time_res.total_seconds() >= 0:
        return True
    return False


def dump_data(data, host, req_type):
    for i in range(len(DICTIONARY['domain'])):
        if host in DICTIONARY['domain'][i].keys() and req_type in DICTIONARY['domain'][i][host].keys():
            DICTIONARY['domain'].pop(i)
            break
    DICTIONARY['domain'].append({host: data})
    with open('cache.json', 'w', encoding="utf-8") as f:
        json.dump(DICTIONARY, f)


def return_result(host, req_type):
    host_to_check = host[:-1]
    new_dict = check_cache(host_to_check, req_type, True)
    result = b''
    if new_dict:
        result += b'---CACHE RECORD---\n'
    else:
        new_dict = request_data(host_to_check, req_type)
        if new_dict and 'no servers' not in new_dict.keys():
            dump_data(new_dict, host_to_check, req_type)
            result += b'---FRESH RECORD---\n'
        elif 'no servers' in new_dict.keys():
            new_dict = check_cache(host_to_check, req_type, False)
            if not new_dict:
                return b'No servers could be reached and there is no data in the cache\n'
            result += b'---CACHE RECORD---\n'
        else:
            return b'Wrong domain\n'
    match req_type:
        case 'ns':
            result += bytes_ns(new_dict, host_to_check)
        case 'a':
            result += bytes_a(new_dict, host_to_check)
        case 'soa':
            result += bytes_soa(new_dict, host_to_check)
    return result


def process_data(data):
    if data == b'check':
        return b'The server is working!\n'
    elif data == b'-h' or data == b'--help':
        return b'Enter the full domain name(example.com.) and record type(ns, a, soa)\n' \
               b'To check connection, write the "check"\n' \
               b'To stop the connection, write the "exit"\n'
    else:
        host, req_type = parse_recv(data.decode("utf-8").split(' '))
        if req_type:
            return return_result(host, req_type)
        else:
            return host


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', 4444))
    sock.listen(1)

    while True:
        conn, addr = sock.accept()
        try:
            data = conn.recv(1024)
            if data == b'exit':
                break
            conn.sendall(process_data(data))
        finally:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()


if __name__ == '__main__':
    main()
