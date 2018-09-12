#!/usr/bin/python3.4

import os
import sys
# threading module contains thread calls
import threading
# For processing arguments
import argparse 
# For SOCKET
import socket

# Defining a new subclass of the Thread class

class ClientThread(threading.Thread):

#Overriding the __init__(self [,args]) method to add additional arguments

      def __init__(self,ip,port,sock,fo_path):

#Calling super class to create thread
         threading.Thread.__init__(self)
         self.ip = ip
         self.port = port
         self.sock = sock
         self.fo_path = fo_path
         print("\n")
         print ("New thread started for [%s:%s]" %(self.ip,str(self.port)))

#Override the run(self [,args]) method to implement what the thread should do when started
      def run(self):
	
#Receiving the command from client using sock.recv() function
         
         msg1 = "Wellcome!"
         msg2 = "Currently, Sever is supporting <List>,<Put> and <Get> Commands"
         msg3 = "Please Enter you Command!"
         self.sock.send(msg1.encode())
         self.sock.send(msg2.encode())
         self.sock.send(msg3.encode())
         command = self.sock.recv(1024).decode()

         if command == "LIST" or command == "list":
            msg4 = "Displaying current directory files<>"
            self.sock.send(msg4.ecode())
            displayFiles(self.fo_path,self.sock)

         elif command == "PUT" or command == "put":
            recvFile()

         else:
            msg5 = "Name the File you want to <download>?"
            self.sock.send(msg5.encode())
            filename = self.sock.recv(1024).decode()
            sendFile(self.sock,filename)

#displaying all the files in a folder

def displayFiles(folderPath,sock):
      if os.path.isdir(folderPath):
         files = os.listdir(folderPath)
         for file in files:
             sock.send(file.encode())
      else:
         msg6 = "Folder doesn't Exits....Exiting!..."
         sock.send(msg6.encode())

# closing socket in case of error and exiting the program
         self.sock.close()
         sys.exit(1)
                
        	
def recvFile():
    print("Intentionally left blank!")

def sendFile(sock,filename):
      if os.path.isfile(filename):
          msg7 = "EXISTS"
          sock.send((msg7+str(os.path.getsize(filename))).encode())
          userResp = sock.recv(1024).decode()

          if userResp[:2] == "OK" or userResp[:2] == "ok":
             with open(filename,"rb") as fp:
                 bytesTosend = fp.read(1024)
                 sock.send(bytesTosend.encode())

#This while will check if there is remaining bytes in file, in case of images file or files longer than 1k
                 while(bytesTosend != ""):
                   bytesTosend = fp.read(1024)
                   sock.send(bytesTosend.encode())  
	
      else:
         msg8 = "<ERROR>: requested file doesn't exists"
         sock.send(msg8.encode())

#closing socket in case of error and exit the program
         sock.close() 		
         sys.exit(1)
  	
        	
def Main():

#Processing command line arguments
      parser = argparse.ArgumentParser(description="Supply PORT and FOLDER PATH to run FTP Sever properly!")
      parser.add_argument(
                          '-p',                      #short switch for port
                          '--port',                   #long switch for port
                           dest='port',
                           type=int,
                           default=5000,
                           help='Port is required for communication between server and client'
                         )
  
      parser.add_argument(
                          '-f',                         #short switch for folder path  
                          '--folder',                   #long switch for folder path
                          dest='fo_path',
                          default=None,
                          type=str,
                          help='Valid folder path is required to download files from directory'      
                         )

      args = parser.parse_args()
          
	
#defining tuple for bind() call
      host = '127.0.0.1'
      port =  int(args.port)
      threads = []
	
      try:
# socket.socket() call will create a new socket of type TCP and return the socket descriptor 
         tcpsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      except socket.error as messg:
         print("Caught Exception--> %s" %messg)

#This is because the previous execution has left the socket in a TIME_WAIT state, and can’t be immediately reused
      try:
         tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      except socket.error as messg:
         print("Caught Exception-->%s" %messg)

      try:
# bind() call will bind the ip address i.e. (127.0.0.1) and port i.e. (5000) on newly created TCP socket 
         tcpsock.bind((host,port))
      except socket.error as messg:
         print("Caught Exception--> %s" %messg)
		
      try: 
# listen() call listen for clients on Network. This sever can queue upto max 10 clients
         tcpsock.listen(10)
         print("<Sever Started:>*** Waiting for Incoming Connections***")
         print("\n\n")
      except socket.error as messg:
         print("Caught Exception--> %s" %messg)
	
      try:
#accept() call is blocking call and will accept the connection from clients. it will return new sock descriptor for read and writing on socket

         while True:
            (newtcpsock,(ip,port)) = tcpsock.accept()
            print("Got Connection! from [%s:%s]" %(ip,str(port)))	
            newThread = ClientThread(ip,port,newtcpsock,args.fo_path)

# This function will automatically call run method defined in class
            newThread.start()


#Append all the created threads in thread list so that we can join them. By joining all threads;
#Main thread will wait for all child threads to finish their jobs
            threads.append(newThread)

            for thread in threads:
              thread.join()
      except socket.error as messg:
        print("Caught Exception--> %s" %messg)

if __name__ == "__main__":
       Main()



