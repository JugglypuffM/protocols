import subprocess
import re
import json
from urllib import request
from prettytable import PrettyTable
import sys


def parse_info(count, info):
    try:
        as_number = info['org'].split()[0][2::]
        provider = " ".join(info['org'].split()[1::])
    except KeyError:
        as_number, provider = '*', '*'
    return [f"{count}.", info['ip'], info['country'], as_number, provider]


def trace(address, table):
    tracert_proc = subprocess.Popen(["tracert", address], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    number = 0

    for raw_line in iter(tracert_proc.stdout.readline, ''):
        line = raw_line.decode("cp1251")
        ip = re.findall('\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}', line)

        if 'Трассировка завершена' in line:
            print(table)
            return
        if 'Не удается разрешить' in line:
            print('Неверный хост')
            return
        if 'Превышен интервал ожидания' in line:
            print('Время истекло')
            continue
        if ip:
            print(f'{"".join(ip)}')
            info = json.loads(request.urlopen('https://ipinfo.io/' + ip[0] + '/json').read())
            number += 1
            if 'bogon' in info:
                table.add_row([f"{number}.", info['ip'], '*', '*', '*'])
            else:
                table.add_row(parse_info(number, info))


if __name__ == '__main__':
    table = PrettyTable()
    table.field_names = ["number", "ip", "country", "AS number", "provider"]
    trace(sys.argv[-1], table)
