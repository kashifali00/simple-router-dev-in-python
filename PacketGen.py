#!/usr/bin/python3.4


#= Author:
#=
#= Module: Packet Generator Module
#=
#= Description:
#= Packet generator module, generates udp packets and send to router programming running on other end.
#= Also, it receives responses comming from Router module and display them on the screen
#========================================================================================================

import os
import sys
# threading module contains thread calls
import threading
# For processing arguments
import argparse
# For SOCKET
import socket
# to generate random number
import random

def sendPackets(udpsock,host,port):

  # UDP PACKET(1)
  ttl1 =random.randrange(1,4,1)
  pack1 = "1,"+"192.168.128.1"+",192.224.0.5,"+str(ttl1)+","+"testing_udp_packet1"
  udpsock.sendto(pack1.encode(),(host,port))

  messg0,addr0 = udpsock.recvfrom(1024);
  print(messg0.decode())

  # UDP PACKET(2)
  ttl2 =random.randrange(1,4,1)
  pack2 = "2,"+"192.168.128.7"+",192.168.128.1,"+str(ttl2)+","+"testing_udp_packet2"
  udpsock.sendto(pack2.encode(),(host,port))

  messg1,addr1 = udpsock.recvfrom(1024)
  print(messg1.decode())

 # UDP PACKET(3)
  ttl3 =random.randrange(1,4,1)
  pack3 = "3,"+"192.168.192.10"+",192.168.128.1,"+str(ttl3)+","+"testing_udp_packet3"
  udpsock.sendto(pack3.encode(),(host,port))

  messg2,addr2 = udpsock.recvfrom(1024)
  print(messg2.decode())
  
# UDP PACKET(4)
  ttl4 =random.randrange(1,4,1)
  pack4 = "4,"+"192.224.10.5"+",192.168.128.7,"+str(ttl4)+","+"testing_udp_packet4"
  udpsock.sendto(pack4.encode(),(host,port))
  messg3,addr3 = udpsock.recvfrom(1024)
  print(messg3.decode())

# UDP PACKET(5)
  ttl5 =random.randrange(1,4,1)
  pack5 = "5,"+"192.168.192.4"+",192.168.128.1,"+str(ttl5)+","+"testing_udp_packet5"
  udpsock.sendto(pack5.encode(),(host,port))
  messg4,addr4 = udpsock.recvfrom(1024)
  print(messg4.decode())


  
 

def Main():

#Processing command line arguments
      parser = argparse.ArgumentParser(description="Port no required to communicate")
      parser.add_argument(
                          '-p',                      #short switch for port
                          '--port',                   #long switch for port
                           dest='port',
                           type=int,
                           default=5000,
                           help='Port is required for communication between server and client'
                         )

      args = parser.parse_args()


      host = ''
      port = int(args.port) # command line arguments are always passed as a string, so converting string to int for port


      try:
         # socket.socket() call will create a new socket of type UDP and return the socket descriptor 
         udpsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
         print("\n")
         print("UPD socket created successfully!\n")
      except socket.error as messg:
         print("Failed to create UDP Socket [%s\n]" %messg)
         sys.exit()

      sendPackets(udpsock,host,port)

 
if __name__ == "__main__":
       Main()
