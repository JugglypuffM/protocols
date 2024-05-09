# Caching DNS server

## Requirements
`dnslib` python package

## Usage
To start server use:
```shell
python server.py
```

## Info
On start server loads and validates cache(happens every minute after start) then 
listens to 53 port, if it gets request then it checks if requested data is 
already stored in cache, if not then server makes a recursive call to higher 
dns and listens to its reply to add it to cache
