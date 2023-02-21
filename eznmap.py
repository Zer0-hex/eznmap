#!/usr/bin/python3
import re
import os
import sys
import subprocess

Min_rate = 3389 	# 最小速度，可以改成你喜欢的数字. 数字越大，速度越快，结果越不稳定. 内网环境可以改成： 7777
Help = '''
Usage:
	python3 eznmap.py [hosts file]		This file is live host list.

You can in Linux:
	$ nmap -sn 192.168.1.1/24 --min-rate=300 -oG LiveHosts.gnmap
	$ cat LiveHosts.gnmap | grep Up | awk '{print $2}' >> LiveHosts.txt
	$ python3 eznmap.py LiveHosts.txt
	Good luck!!!
'''

def main():
	args = sys.argv
	if len(args) != 2:
		print(Help)
		return
	with open(args[1], 'r') as f:
		Hosts = f.read().split('\n')
	Hosts = [i for i in Hosts if i != '']
	print('-+- Scan start -+-')
	for i in Hosts:
		if os.path.exists(i):
			print(f'[-] "{i}" File already exist. Skip scan...')
		else:
			os.mkdir(i)
			scan(i)
			print(f'[+] Scan {i} done ...')
			save_md(i)
	print('-+-  Scan end  -+-')


def scan(ip=''):

	cmd_scan_tcp = f"nmap -p- --min-rate {Min_rate} {ip} -oA {ip}/tcp_ports"
	cmd_scan_udp = f"nmap -p- --min-rate {Min_rate} -sU {ip} -oA {ip}/udp_ports"

	print('[+]', cmd_scan_tcp)
	print('[+]', cmd_scan_udp)

	p_scan_tcp = subprocess.Popen(cmd_scan_tcp, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
	p_scan_udp = subprocess.Popen(cmd_scan_udp, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")

	p_scan_tcp.wait()
	p_scan_udp.wait()

	with open(f'{ip}/tcp_ports.nmap', 'r') as f:
		tcp_ports = f.read()
	tcp_ports =  re.findall(r'\n([0-9]*)/tcp', tcp_ports)

	with open(f'{ip}/udp_ports.nmap', 'r') as f:
		udp_ports = f.read()
	udp_ports =  re.findall(r'\n([0-9]*)/tcp', udp_ports)

	ports = ','.join(list(set(tcp_ports + udp_ports)))

	cmd_server_scan = f"nmap -sT -sV -O --version-all -p{ports} {ip} -oA {ip}/server_info"
	cmd_vulner_scan = f"nmap -sT --script=vuln -p{ports} {ip} -oA {ip}/vuln_info"

	print('[+]', cmd_server_scan)
	print('[+]', cmd_vulner_scan)

	p_server_scan = subprocess.Popen(cmd_server_scan, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
	p_vulner_scan = subprocess.Popen(cmd_vulner_scan, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")

	p_server_scan.wait()
	p_vulner_scan.wait()

def save_md(ip=''):
	with open(f'{ip}/tcp_ports.nmap', 'r') as f:
		tcp_ports = f.read()

	with open(f'{ip}/udp_ports.nmap', 'r') as f:
		udp_ports = f.read()

	with open(f'{ip}/server_info.nmap', 'r') as f:
		server_info = f.read()

	with open(f'{ip}/vuln_info.nmap', 'r') as f:
		vuln_info = f.read()

	with open(f'{ip}/ports', 'r') as f:
		ports = f.read()
	ports = ports.split('\n')
	ports = ['- [ ] ' + i for i in ports if i != '']
	ports = '\n'.join(ports)

	md = f'''
# {ip}

## Port Scan

- Tcp Port Scan

```
{tcp_ports}
```

- Udp Port Scan

```
{udp_ports}
```

- Server Info

```
{server_info}
```

- Vuln Info

```
{vuln_info}
```

## Attack Port

{ports}

'''
	out_path = 'reports'
	if not os.path.exists(out_path):
		os.mkdir(out_path)

	with open(f'reports/{ip}.md', 'w') as f:
		f.write(md)

if __name__ == '__main__':
	main()
