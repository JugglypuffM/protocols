import pickle
import socket
import sys
import time
import dnslib
from dnslib import QTYPE

higher_dns = ('1.1.1.1', 53)
cache = {}


def resolve_request(request):
    if request:
        parsed_request = dnslib.DNSRecord.parse(request)
        filtered_request = filter_request(parsed_request)
        if filtered_request:
            for question in filtered_request.questions:
                sender.sendto(dnslib.DNSRecord(dnslib.DNSHeader(), q=question).pack(), higher_dns)
                print('Request to {}:{} with question {}:{}'.format(higher_dns[0], higher_dns[1], question.qname,
                                                                    question.qtype))


def filter_request(request):
    hits = []
    for question in request.questions:
        if question.qname in cache and question.qtype in cache[question.qname]:
            _, end = cache[question.qname][question.qtype]
            print(
                'Record:{} type:{} ends:{} contains in '
                'cache'.format(
                    question.qname, question.qtype,
                    time.ctime(end)))
            hits.append(question)
        else:
            print(
                'Record:{} type:{} not in cache'.format(
                    question.qname, question.qtype))
    for question in hits:
        request.questions.remove(question)
    return request if request else None


def resolve_reply(reply):
    parsed_reply = dnslib.DNSRecord.parse(reply)
    rr = parsed_reply.auth if (parsed_reply.q.qtype == QTYPE.PTR) else parsed_reply.rr
    question = parsed_reply.q.qtype
    for record in rr:
        name = parsed_reply.q.qname if (parsed_reply.q.qtype == QTYPE.PTR) else record.rname
        end = int(time.time()) + record.ttl
        if name in cache:
            cache[name][question] = (
                record, end)
            print(
                'Record:{} type:{} ends:{} updated in cache'.format(
                    name, question,
                    time.ctime(end)))
        else:
            cache[name] = {question: (
                record, end)}
            print(
                'Record:{} type:{} ends:{} added in cache'.format(
                    name, question,
                    time.ctime(end)))


def load_cache():
    global cache
    try:
        with open('saved_cache.pickle', 'rb') as f:
            cache = pickle.load(f)
            validate_cache()
            print("Cache found")
    except IOError:
        print("Cache not found")


def validate_cache():
    removed = []
    for rname in cache:
        for rtype in cache[rname]:
            _, end = cache[rname][rtype]
            if end < int(time.time()):
                removed.append((rname, rtype))
    for rname, rtype in removed:
        del cache[rname][rtype]
        if not cache[rname]:
            del cache[rname]


if __name__ == "__main__":
    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listener.bind(("localhost", 53))
    listener.settimeout(0)
    sender.settimeout(0)
    timer = time.time()

    try:
        load_cache()
        print("Listening for requests")
        while True:
            try:
                new_request, client = listener.recvfrom(1024)
                print('\nRequest from {}:{}'.format(client[0], client[1]))
                resolve_request(new_request)
            except OSError:
                pass
            try:
                new_reply, addr = sender.recvfrom(1024)
                print('\nReply from {}:{}'.format(addr[0], addr[1]))
                resolve_reply(new_reply)
            except OSError:
                pass
            if time.time() - timer > 60:
                validate_cache()
                timer = time.time()
            time.sleep(0.1)
    finally:
        print("Closing sockets")
        listener.close()
        sender.close()
        print("Saving cache")
        with open('saved_cache.pickle', 'wb') as f:
            pickle.dump(cache, f)
        time.sleep(1)
        sys.exit(0)
