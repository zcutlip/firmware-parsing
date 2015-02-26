#!/usr/bin/env python
import sys
import struct

class TRXHeaderException(Exception):
    def __init__(self,msg):
        super(self.__class__,self).__init__(msg)

class TRXHeader(object):
    BIG_ENDIAN=0
    LITTLE_ENDIAN=1
    TRX_MAGIC_LE="HDR0"
    TRX_MAGIC_BE="0RDH"
    
    TRX_HEADER_SZ=28
    MAGIC_OFF   =  0
    MAGIC_LEN   =  4
    LENGTH_OFF  =  4
    LENGTH_LEN  =  4
    CRC_OFF     =  8
    CRC_LEN     =  4
    FLAGS_OFF   = 12
    FLAGS_LEN   =  2
    VER_OFF     = 14
    VER_LEN     = 2
    
    #The next three offsets are the the locations
    #in the TRX header that describe the offsets of
    #the firmware image partitions. They are offsets of offsets.
    PART_OFF1_OFF = 16
    PART_OFF1_LEN = 4
    PART_OFF2_OFF = 20
    PART_OFF2_LEN = 4
    PART_OFF3_OFF = 24
    PART_OFF3_LEN = 4
    
    def __init__(self,data):
        

        """
        from http://wiki.openwrt.org/doc/techref/header
         0                   1                   2                   3   
         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 
        +---------------------------------------------------------------+
        |                     magic number ('HDR0')                     |
        +---------------------------------------------------------------+
        |                  length (header size + data)                  |
        +---------------+---------------+-------------------------------+
        |                       32-bit CRC value                        |
        +---------------+---------------+-------------------------------+
        |           TRX flags           |          TRX version          |
        +-------------------------------+-------------------------------+
        |                      Partition offset[0]                      |
        +---------------------------------------------------------------+
        |                      Partition offset[1]                      |
        +---------------------------------------------------------------+
        |                      Partition offset[2]                      |
        +---------------------------------------------------------------+
        """
        fmt=""
        if(len(data) < self.TRX_HEADER_SZ):
            raise TRXHeaderException("Data is less than TRX Header size of: %d" % self.TRX_HEADER_SZ)
        
        self.__parse_hdr(data)
        self.data=data
        
    def __parse_hdr(self,data):
        self.hdr_sz=self.TRX_HEADER_SZ
        off=self.MAGIC_OFF
        self.magic=data[off:off+self.MAGIC_LEN]
        if self.magic == self.TRX_MAGIC_LE:
            self.endianness=self.LITTLE_ENDIAN
            uint32="<I"
            uint16="<H"
        elif self.magic == self.TRX_MAGIC_BE:
            self.endianness=self.BIG_ENDIAN
            uint32=">I"
            uint16=">H"
        else:
            raise TRXHeaderException("Invalid TRX header.")
        off=self.LENGTH_OFF
        trxlen=data[off:off+self.LENGTH_LEN]
        self.trxlen=struct.unpack(uint32,trxlen)
        
        off=self.CRC_OFF
        crc=data[off:off+self.CRC_LEN]
        self.crc=struct.unpack(uint32,crc)
        
        off=self.FLAGS_OFF
        flags=data[off:off+self.FLAGS_LEN]
        self.flags=struct.unpack(uint16,flags)
        
        off=self.VER_OFF
        ver=data[off:off+self.VER_LEN]
        self.ver=struct.unpack(uint16,ver)
        
        off=self.PART_OFF1_OFF
        p1_off=data[off:off+self.PART_OFF1_LEN]
        self.p1_off=struct.unpack(uint32,p1_off)
        
        off=self.PART_OFF2_OFF
        p2_off=data[off:off+self.PART_OFF2_LEN]
        self.p2_off=struct.unpack(uint32,p2_off)
        
        off=self.PART_OFF3_OFF
        p3_off=data[off:off+self.PART_OFF3_LEN]
        self.p3_off=struct.unpack(uint32,p3_off)
    
    def endianness_str(self):
        if self.endianness==self.BIG_ENDIAN:
            return "big endian"
        else:
            return "little endian"
        

class TRXHeaderFromFile(TRXHeader):
    def __init__(self,filename,trx_offset=0):
        cls=self.__class__
        fw_file=open(filename,"rb")
        fw_file.seek(trx_offset)
        data=fw_file.read(cls.TRX_HEADER_SZ)
        super(self.__class__,self).__init__(data)

def main(input_file,trx_offset=0):
    trx_header=TRXHeaderFromFile(input_file,trx_offset)
    print("Endianness:                      %s" % trx_header.endianness_str())
    print("Magic:                           %s" % trx_header.magic)
    print("Length of TRX header + image:    %d" % trx_header.trxlen)
    print("CRC:                             0x%08x" % trx_header.crc)
    print("Flags:                           0x%04x" % trx_header.flags)
    print("Version:                         0x%04x" % trx_header.ver)
    print("Partition 1 offset:              %d" % trx_header.p1_off)
    print("Partition 2 offset:              %d" % trx_header.p2_off)
    print("Partition 3 offset:              %d" % trx_header.p3_off)
    

def usage(status):
    print("Usage:   trxparser.py <firmware_image> [optional offset of TRX header]")
    print("Examples:")
    print("         trxparser.py firmware.bin")
    print("         trxparser.py firmware.bin 128")
    print("         trxparser.py firmware.bin 0x80")
    exit(status)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1],int(sys.argv[2],0))
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        usage(1)
    
