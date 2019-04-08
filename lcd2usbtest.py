#-*- coding:utf-8 -*-
from lcd2usb import LCD
from lcd2usb import SMILE_SYMBOL
import time
import struct

g_u_gb_mapping = None
g_hzk16 = None

def get_gb_from_unicode(u):
    global g_u_gb_mapping
    if g_u_gb_mapping is None:
       g_u_gb_mapping = {}
       with open('unicode-gb2312.txt', 'r') as f:
           for i, line in enumerate(f):
               if i > 0:
                  kv = line.split(' ')
                  g_u_gb_mapping[kv[0]] = kv[1]
    return g_u_gb_mapping[u] 

def get_dot_info(c):
    global g_hzk16
    u = hex(ord(c)).upper()[2:]
    print '----unicode:' + u
    gb = get_gb_from_unicode(u)
    print '---gb:' + gb
    x = int(gb[0:2], 16) 
    y = int(gb[2:], 16) 
    offset = (94*(x-160-1)+(y-160-1))*32
    print '---offset:{}'.format(offset)
    if g_hzk16 is None:
       with open('HZK16.dat', 'rb') as f:
           g_hzk16 = f.read()
    dot = []
    for i in xrange(0, 16):
        tmp = []
        for j in xrange(0, 16):
            tmp.append(0)
        dot.append(tmp)

    for i in xrange(0, 16):
       for j in xrange(0, 2):
           b = g_hzk16[offset+i*2+j]
           b = struct.unpack('b', b) 
           for m in xrange(0, 8): 
               tmp = b[0] & (1<<(7-m)) 
               dot[i][j*8+m] = 1 if tmp > 0 else 0
    #print '-----dot:'
    #for i in xrange(0, 16):
    #    print '{}'.format(dot[i])

    return dot  

def get_udc_array(c):
    dot = get_dot_info(c) #16*16
    dot_ex = [] #20*16
    for i in xrange(0, 16):
        for j in xrange(0,20):
            dot_ex.append(0)  
 
    for i in xrange(0, 16):
        for j in xrange(0, 16):
            dot_ex[i*20+j+2] = dot[i][j]

    print '---dot_ex:'
    for i in xrange(0, 16):
        print '{}'.format(dot_ex[i*20:(i+1)*20])
  
    udc = []  # 8
    for i in xrange(0, 2):
        for j in xrange(0, 4):
            r = [] 
            for m in xrange(0, 8):
                tmp = 0
                data = dot_ex[(i*8+m)*20+j*5:(i*8+m)*20+(j+1)*5]
                for n in xrange(0, 5):  
                    tmp += data[n] * (1<<(4-n)) 
                r.append(tmp)
            udc.append(bytearray(r))
    return udc         
        
 

def write_chinese(c, col, row):
    udc_array = get_udc_array(c)
    for i in xrange(0, 8):
        lcd.define_char(i, udc_array[i])
    for j in xrange(0, 2):
        for i in xrange(0, 4):
            lcd.write(chr(j*4+i), col+i, row+j)    

lcd = LCD()
print lcd.info()
print lcd.version

lcd.clear()
lcd.write('', 0, 0)

texts = [u'蒋悦心真棒', u'辛欣真漂亮']

while True:
    col = 0
    row = 0 
    for text in texts:
       col = 0
       lcd.clear()
       lcd.write('', 0, 0)
       for c in text:
          lcd.clear()
          lcd.write('', 0, 0)
          write_chinese(c, col, row)  
          time.sleep(1)
          col += 4
          if col >= 20:
             col = 0
       row += 2
       if row >= 4:
          row = 0  
     
  


