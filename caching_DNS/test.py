import socket
import dnslib
from dnslib import QTYPE

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = dnslib.DNSRecord()
data.add_question(dnslib.DNSQuestion("maps.google.com", QTYPE.A))
data.add_question(dnslib.DNSQuestion("www.youtube.ru", QTYPE.A))
data.add_question(dnslib.DNSQuestion("maps.google.com", QTYPE.AAAA))
data.add_question(dnslib.DNSQuestion("www.youtube.ru", QTYPE.AAAA))
data.add_question(dnslib.DNSQuestion("google.com", QTYPE.NS))
data.add_question(dnslib.DNSQuestion("yandex.ru", QTYPE.NS))
data.add_question(dnslib.DNSQuestion("173.194.73.198", QTYPE.PTR))
data.add_question(dnslib.DNSQuestion("gmail.com", QTYPE.MX))
data.add_question(dnslib.DNSQuestion("yandex.ru", QTYPE.MX))

socket.sendto(data.pack(), ('localhost', 53))
socket.close()
