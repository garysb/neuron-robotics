#control.py source code

import os
import socket
import sys, getopt
import StringIO
import shutil
import binascii

def xsend(cmd,data):	
    import binascii
    s.send(  cmd +'\n')
    if data:
        print "sending data"
        s.send('Content-Length: '+str(len(data))+'\n'+'CRC32: '+str(binascii.crc32(data))+'\n')
        s.send(data)

def readline():
    d=[]
    while 1:
        c=s.recv(1)
        d.append(c)
        # We support just sane line-endings here.
        if c=='\n':
            break
    return ''.join(d)

def recvdata():
    print "Waiting for data..."
    header_lines=[readline() for x in range(2)]
    header=dict([x.rstrip().split(': ') for x in header_lines])
    content_length=int(header['Content-Length'])
    crc32=int(header['CRC32'])
    print("Content-Length: %d"%content_length)
    recvbytes=0
    content=[]
    print "Receiving data..."
    while recvbytes<content_length:
        recvstring=s.recv(min(content_length-recvbytes,2048))
        recvbytes+=len(recvstring)
        print "Received: %d bytes (%3.1f%%)\r"%(recvbytes,(100.*recvbytes/content_length)),
        content.append(recvstring)
    print "Received %d bytes."%recvbytes
    content=''.join(content)
    if crc32 != binascii.crc32(content):
        print "*** CRC error!"
    return content

def PrintResult():
    res = eval(recvdata())
    print '-----------begin-----------'
    print "%i Errors" % res[0]
    if res[0]>0:
        t = res[1]
        for i in t:
            print ">",i,
    print '------------end------------'


HOST = 'localhost'    # The remote host
PORT = 7777              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

print "control.py by Raul Aguaviva"

args = sys.argv[1:]


if args[0] == '-p':
    print 'put!!!!!!!!'
    try:
        f=open(args[1],'rb')
        datos = f.read()
        f.close()      
        xsend ("put " + args[2],datos)
    except:
        print "can't find file:", args[1]
elif args[0] == '-g':
    print 'get!!!!!!!!'
    xsend ("get "+ args[1],0)
    try:
        datos = recvdata()
        f=open(args[2],'wb')
        f.write(datos)
        f.close()      
    except:
        print "can't find file:", args[1]
elif args[0] == '-e':
    print 'eval!!!!!!!!'
    xsend ("eval", repr(args[1]))
    PrintResult()
elif args[0] == '-x':
    t = args;
    t.pop(0)
    xx = ' '.join(t)
    print 'exec!!!!!!!!'
    xsend ("exec", repr(xx))
    PrintResult()
elif args[0] == '-xf':
    t = args;
    t.pop(0)
    xx = ' '.join(t)
    print 'execfile!!!!!!!!'
    #cmd = "try:\n    execfile('"+xx+"',globals())\nexcept:\n    print 'error'\n"
    cmd = "execfile('"+xx+"',globals())"
    xsend ("exec", repr(cmd))  #  "execfile('caca',globals())"
    PrintResult()
else:
    print "command " + args[0] + "not found" 

s.close()
