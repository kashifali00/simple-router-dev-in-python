#!/usr/bin/python3.4

#= Author:
#=
#= Module: Router A simulation Module
#=
#= Description:
#= Router module simulation the behavior of Router A mentioned in assignment diagram.
#= It receives the udp packets coming from packet generator module. Upon receiving the packets
#= it calculates ttl value of the packets and route the packet to its correct destination. Router
#= also mantains the statistic file, which contains packets relating information 
#========================================================================================================


import os
import sys
# threading module contains thread calls
import threading
# For processing arguments
import argparse 
# For SOCKET'
import socket
import ipaddress
import datetime

source_subnetmask=0


# Function statistic log the packet information into statistic.txt file

def statistic(statistic_file,destip,sourceip,packet_ID,router_name,routerA_cnt,routerB_cnt,routerC_cnt,unroutable_cnt,rcvd_pkt):

    #print("Packet ID= %d Source %s Destination %s Router %s RouterA_packets %d RouterB_packets %d RouterC_packets %d Unroutable_packets %d"
     #   %(int(packet_ID),sourceip,destip,router_name,routerA_cnt,routerB_cnt,routerC_cnt,unroutable_cnt))

     # open the statisfic for logging the routing information

    try:
     with open(statistic_file,"a") as fp:
       fp.write("Packet ID: [%d] srcIP:[%s] destIP:[%s] Packet_Routed_to:[%s] RA_pkts:[%d] RB_pkts:[%d] RC_pkts:[%d] Unroutable_packets: [%d] Total_Packet_Received:[%d]\n\n" %(int(packet_ID),sourceip,destip,router_name,routerA_cnt,routerB_cnt,routerC_cnt,unroutable_cnt,rcvd_pkt))
    finally:
      fp.close() 


# Function route_packet route the packet to correct destination and call statistic function for logging
# the packet information. it also opens routetable_file.txt for getting the information on which router to route 
# the packet or direct dilevery of packet if both machines on the same network. Also, calculates how many 
# packets was received by each counter.

def route_packet(routetable_file,statistic_file,destip,sourceip,expired_cnt,packet_ID,rcvd_pkt):
           global source_subnetmask
           unroutable_cnt=0
           dd_cnt=0;
           routerB_cnt=0
           routerC_cnt=0
           match_cnt=0

      #Open route table file for routing the udp packet to correct destination
           try:   
               with open(routetable_file,"r") as fp:
                # readlines() function return a list containing all lines in a file
                 subnet_mask = fp.readlines()
                 for mask in subnet_mask:
                    #split each line on the basis of " " and grab the router address or name
                      source_mask = mask.split(" ")
                             
                      # Get the subnet mask of the source
                      # Comparing sourceip from packet with subnet of route table, if both are matching then get the subnet mask of source
                      if((sourceip == source_mask[0])):
                        source_subnetmask = source_mask[1]
                        

                      # Compare the destination ip address with route table subnet and get the router address or name

                      if((destip == source_mask[0])):
                        router_name = source_mask[2]
                        if(router_name.rstrip('\n') == 'Router(B)'):
                          # Update the Router B packet counter
                          routerB_cnt = routerB_cnt+1
                          #print("routerB_cnt =%d" %(routerB_cnt))
                        else:
                          # update the Router C packet counter
                          routerC_cnt = routerC_cnt+1
                          #print("routerC_cnt =%d" %(routerC_cnt))

                      if not source_subnetmask:
                         unroutable_cnt = unroutable_cnt+1
                       
                      # Compare source and destination ip with source's subnet mask to find out, if the destination ip
                      # is on the same network or not. if the destination ip is not on the same network then send the 
                      # packet to router otherwise direct delivery of packet on the same network
          
               sip = int(ipaddress.ip_address(sourceip))
               dip = int(ipaddress.ip_address(destip))
               ssm = int(ipaddress.ip_address(source_subnetmask))
                      
               if((sip & ssm) == (dip & ssm)):
                 print("Delivering direct: packet ID=%d dest=%s" %(int(packet_ID),destip))
                 # update direct dilevery packet counter
                 dd_cnt = dd_cnt+1
                 
               #else:
                 #print("Delivering packet to [%s] packet ID=%d dest=%s" %(router_name.rstrip('\n'),int(packet_ID),destip))
 
           finally:           
               #print("Done with Route table file reading")
               fp.close()
               statistic(statistic_file,destip,sourceip,packet_ID,router_name,dd_cnt,routerB_cnt,routerC_cnt,unroutable_cnt,rcvd_pkt)
                                          
# Function Main() start the program execution. It parse the command line arguments and receive packets from
# packet generator module and calls the route_packet() function to route the packet to its correct destination
# Also, upon receiving the packet from generator module check the TTL value of the packet, if its reaching to
# 0 then drop the packet immediately

def Main():

      dropPacket = 0
      rcvd_pkt = 0

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
  
      parser.add_argument(
                          '-rf',                         #short switch for routing table file path  
                          '--rfile',                    #long switch for routing table file path
                          dest='routertablefile',
                          default=None,
                          type=str,
                          help='routing table file is required by router'      
                         )
      
      parser.add_argument(
                        '-sf',                           #short switch for statistic file path
                        '--sfile',
                        dest='statisticfile',
                        default=None,
                        type=str,
                        help='statistic file is required by router'
                        )

      args = parser.parse_args()


      host = '' #Symbolic name, listening on all available interfaces
      port = int(args.port) # command line arguments are always passed as a string, so converting string to int for port

      

      try:
           # socket.socket() call will create a new socket of type UDP and return the socket descriptor 
         udpsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
         print("\n")
         print("Running Router A simulation...")
         print("==========================================================\n\n")
         print("UDP socket created successfully!\n")
      except socket.error as messg:
         print("Failed to create UDP Socket [%s\n]" %messg)
         sys.exit()

#This is because the previous execution has left the socket in a TIME_WAIT state, and can’t be immediately reused
      try:
         udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         print("socket was in time_wait state, now has been reassigned\n")
      except socket.error as messg:
         print("Caught Exception-->%s" %messg)
         sys.exit()

      try:
# bind() call will bind the ip address i.e. (127.0.0.1) and port i.e. (5000) on newly created UDP socket 
         udpsock.bind((host,port))
         print("IP & Port binding on socket successful!\n\n")
      except socket.error as messg:
         print("Binding ip & port failed! [%s\n]" %messg)
         sys.exit()
      print("[Router:] Waiting for incoming UDP packets...\n")
      print("press [ctrl+c] to exit\n")

      print("==========================================================\n\n")
      while True:
        
         try:
#***************************  PACKET 1 *******************************************************************************************
            print("---------------Router receiving udp packets----------------\n")    
            udpPacket_data0,addr0 = udpsock.recvfrom(1024)
            rcvd_pkt = rcvd_pkt+1
            print("Packet1: %s\n\n" %udpPacket_data0.decode())

            #split the udp packet and grab the destination address of packet for route.
            #split function return a list of entries separate by "," so second entry on the list will be destination IP
            udp_pkt0 = udpPacket_data0.decode().split(",")
            destip_pack0 = udp_pkt0[2]
            srcip_pack0 = udp_pkt0[1]
            pkt_id0 = udp_pkt0[0]

            # Grab TTL value of the packet
            
            ttl_pkt0 = int(udp_pkt0[3])
           
            # decrement ttl value of the packet upon receiving, if value is equal to 0 then drop the packet
            ttl_pkt0 = ttl_pkt0-1
         
            if(ttl_pkt0 == 0):
               dropPacket = dropPacket+1
               print("UDP_Packet1 dropped!, TTL=%d, expired_pkt=%d" %(ttl_pkt0,dropPacket))
            else:
            # calling route_packet function to route the packet to router              
               route_packet(args.routertablefile,args.statisticfile,destip_pack0,srcip_pack0, dropPacket,pkt_id0,rcvd_pkt)
                    
                        
 
            udpsock.sendto(str.encode("[Router] Got packet(1)"),addr0)

#***************************  PACKET 2 *******************************************************************************************  

            udpPacket_data1,addr1 = udpsock.recvfrom(1024)
            rcvd_pkt = rcvd_pkt+1
            print("Packet2: %s\n\n" %udpPacket_data1.decode())

           #split the udp packet and grab the destination address of packet for route
            dest_addr1 = udpPacket_data1.decode().split(",")
            Destip_pack1 = dest_addr1[2]

            udp_pkt1 = udpPacket_data1.decode().split(",")
            destip_pack1 = udp_pkt1[2]
            srcip_pack1 = udp_pkt1[1]
            pkt_id1 = udp_pkt1[0]


            # Grab TTL value of the packet

            ttl_pkt1 = int(udp_pkt1[3])

            # decrement ttl value of the packet upon receiving, if value is equal to 0 then drop the packet
            ttl_pkt1 = ttl_pkt1-1

            if(ttl_pkt1 == 0):
               dropPacket = dropPacket+1
               print("UDP_Packet1 dropped!, TTL=%d, expired_pkt=%d" %(ttl_pkt1,dropPacket))
            else:
            # calling route_packet function to route the packet to router              
               route_packet(args.routertablefile,args.statisticfile,destip_pack1,srcip_pack1, dropPacket,pkt_id1,rcvd_pkt)

            udpsock.sendto(str.encode("[Router] Got packet(2)"),addr1)

#***************************  PACKET 3 *******************************************************************************************

            udpPacket_data2,addr2 = udpsock.recvfrom(1024)
            rcvd_pkt = rcvd_pkt+1
            print("Packet3: %s\n\n" %udpPacket_data2.decode())

           #split the udp packet and grab the destination address of packet for route
            dest_addr2 = udpPacket_data2.decode().split(",")
            Destip_pack2 = dest_addr2[2]

            udp_pkt2 = udpPacket_data2.decode().split(",")
            destip_pack2 = udp_pkt2[2]
            srcip_pack2 = udp_pkt2[1]
            pkt_id2 = udp_pkt2[0]


            # Grab TTL value of the packet

            ttl_pkt2 = int(udp_pkt2[3])

            # decrement ttl value of the packet upon receiving, if value is equal to 0 then drop the packet
            ttl_pkt2 = ttl_pkt2-1

            if(ttl_pkt2 == 0):
               dropPacket = dropPacket+1
               print("UDP_Packet1 dropped!, TTL=%d, expired_pkt=%d" %(ttl_pkt2,dropPacket))
            else:
            # calling route_packet function to route the packet to router              
               route_packet(args.routertablefile,args.statisticfile,destip_pack2,srcip_pack2, dropPacket,pkt_id2,rcvd_pkt)

            udpsock.sendto(str.encode("[Router] Got packet(3)"),addr2)

#***************************  PACKET 4 *******************************************************************************************


            udpPacket_data3,addr3 = udpsock.recvfrom(1024)
            rcvd_pkt = rcvd_pkt+1
            print("Packet4: %s\n\n" %udpPacket_data3.decode())

           #split the udp packet and grab the destination address of packet for route
            dest_addr3 = udpPacket_data3.decode().split(",")
            Destip_pack3 = dest_addr3[2]

            udp_pkt3 = udpPacket_data3.decode().split(",")
            destip_pack3 = udp_pkt3[2]
            srcip_pack3 = udp_pkt3[1]
            pkt_id3 = udp_pkt3[0]


            # Grab TTL value of the packet

            ttl_pkt3 = int(udp_pkt3[3])

            # decrement ttl value of the packet upon receiving, if value is equal to 0 then drop the packet
            ttl_pkt3 = ttl_pkt3-1

            if(ttl_pkt3 == 0):
               dropPacket = dropPacket+1
               print("UDP_Packet1 dropped!, TTL=%d, expired_pkt=%d" %(ttl_pkt3,dropPacket))
            else:
            # calling route_packet function to route the packet to router              
               route_packet(args.routertablefile,args.statisticfile,destip_pack3,srcip_pack3, dropPacket,pkt_id3,rcvd_pkt)

            # send response back to packet generator module
            udpsock.sendto(str.encode("[Router] Got packet(4)"),addr3)





#***************************  PACKET 5 *******************************************************************************************

            udpPacket_data4,addr4 = udpsock.recvfrom(1024)
            rcvd_pkt = rcvd_pkt+1
            print("Packet5: %s\n\n" %udpPacket_data4.decode())

           #split the udp packet and grab the destination address of packet for route
            dest_addr4 = udpPacket_data4.decode().split(",")
            Destip_pack4 = dest_addr4[2]

            udp_pkt4 = udpPacket_data4.decode().split(",")
            destip_pack4 = udp_pkt4[2]
            srcip_pack4 = udp_pkt4[1]
            pkt_id4 = udp_pkt4[0]


            # Grab TTL value of the packet

            ttl_pkt4 = int(udp_pkt4[3])

            # decrement ttl value of the packet upon receiving, if value is equal to 0 then drop the packet
            ttl_pkt4 = ttl_pkt4-1

            if(ttl_pkt4 == 0):
               dropPacket = dropPacket+1
               print("UDP_Packet1 dropped!, TTL=%d, expired_pkt=%d" %(ttl_pkt4,dropPacket))
            else:
            # calling route_packet function to route the packet to router              
               route_packet(args.routertablefile,args.statisticfile,destip_pack4,srcip_pack4, dropPacket,pkt_id4,rcvd_pkt)

            # send response back to packet generator module
            udpsock.sendto(str.encode("[Router] Got packet(5)"),addr4)


#************************** Reveiving UDP Packets Ends here **********************************************************************


         except socket.error as messg:
           print("Error! Receving data failed! [%s\n]" %messg)
           fp.close()
               
# Press ctrl+c to exit the program
         except KeyboardInterrupt:
             print("\n\n")
             print("ctrl+c was pressed! ... Exiting the program!...\n\n")
             break;

       

if __name__ == "__main__":
       Main()
