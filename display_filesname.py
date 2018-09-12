#!/usr/bin/python3.4
import os
import sys

def displayfiles(path):
   files = os.listdir(path)
   for file in files:
        print ("%s\n" %file)


def main():

   displayfiles(sys.argv[1])



if __name__ == '__main__':
    main()
