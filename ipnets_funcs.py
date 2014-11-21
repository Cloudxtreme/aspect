def dec2ip(ip):
     return '.'.join([str((ip >> 8 * i) & 255) for i in range(3, -1, -1)])
		
def ip2dec(ip):
    return sum([int(q) << i * 8 for i, q in enumerate(reversed(ip.split(".")))])

def calcnet(net,mask):
	mask1 = mask + 1
	net1 = dec2ip(ip2dec(net)+pow(2,31-mask))
	if mask >= 29:
	    return (net,mask1),(net1,mask1)
	return (net,mask1),(net1,mask1), calcnet(net,mask1),calcnet(net1,mask1)
