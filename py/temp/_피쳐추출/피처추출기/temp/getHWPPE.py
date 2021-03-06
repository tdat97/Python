import olefile
import os
import sys
import pprint
from bitstring import BitArray
import openpyxl
import numpy as np
import matplotlib.pyplot as plt


def OLE_Directory(file) :
    need_dir = []
    ole = olefile.OleFileIO(file)
    
    for dir in ole.listdir() :
        if dir[0] == 'PrvImage' or dir[0] == 'BinData' :
            if dir[0] == 'BinData' and len(dir) != 2 :
                continue
            need_dir.append('/'.join(dir))
    return need_dir


def OLE_Extraction(file) :
    print(0)
    ole = olefile.OleFileIO(file)
    print(1)
    dir = OLE_Directory(file)
    print(2)
    print(dir)
    OLE_Features = []
    OLE_Features.append(ole.header_signature)
    OLE_Features.append(ole.header_clsid)
    OLE_Features.append(ole.minor_version)
    OLE_Features.append(ole.byte_order)
    OLE_Features.append(ole.sector_shift)
    OLE_Features.append(ole.mini_sector_shift)
    OLE_Features.append(ole.reserved1)
    OLE_Features.append(ole.reserved2)
    OLE_Features.append(ole.num_dir_sectors)
    OLE_Features.append(ole.num_fat_sectors)
    OLE_Features.append(ole.transaction_signature_number)
    OLE_Features.append(ole.mini_stream_cutoff_size)
    for i in dir :
        print(i)
        data = ole.openstream(i).read()
        #print(data)
        #for v in get_n_gram_features(data):
        #    OLE_Features.append(v)
        OLE_Features.extend(get_n_gram_features(data))

    print(OLE_Features)
    
    #signature, Attribute0, Attribute1, EncryptVersion, KOGL, Book -> Header
    #print(line[:32],line[32:36],line[36:40],line[40:44],line[44:48],line[48:49],line[49:])
    return OLE_Features


def get_n_gram_features(data, p = 6): # 6번 압축
    two_gram_list = n_gram_list(data, 2) # n-gram뽑기
    num_two_gram = count_two_gram(two_gram_list) # shape(256,256)
    scaled_num_two_gram = min_max_scaling(num_two_gram) # shape(256,256)
    features = pooling(scaled_num_two_gram, p) # shape(4,4)
    features = features.flatten() # shape(16)
    features = features.round(4) # 소수4번째서 반올림
    
    return features


def n_gram_list(text, n): # 'text' -> [('t','e'), ('e','x'), ('x','t')]
    ng_list = []

    text_list = []
    for i in range(n):
        text_list.append(text[i:])

    n_gram_zip =zip(*text_list)
    for i in n_gram_zip:
        ng_list.append(i)

    return ng_list


def count_two_gram(two_gram_list):
    num_two_gram = [[0]*256 for i in range(256)]
    num_two_gram = np.array(num_two_gram)

    for i,j in two_gram_list:
        num_two_gram[i][j] += 1

    return num_two_gram


def min_max_scaling(num_two_gram):
    num_two_gram = num_two_gram.flatten()
    num_two_gram = np.log(num_two_gram + 1) # 값차이가 너무커서log사용

    minx = min(num_two_gram)
    maxx = max(num_two_gram)
    #값이 크신분들 작게
    num_two_gram[0] = minx
    num_two_gram[-1] = minx
    minx = min(num_two_gram)
    maxx = max(num_two_gram)
    
    for i in range(len(num_two_gram)): # 0~1 사이 값으로 바꿔줌
        num_two_gram[i] = (num_two_gram[i] - minx) / (maxx - minx)
        
    scaled_num_two_gram = num_two_gram.reshape(256, 256)
   
    return scaled_num_two_gram


def pooling(gram, n):

    for k in range(n): # n번 압축
        gramlen = len(gram) // 2
        new_gram = np.array([0.0]*gramlen*gramlen)
        new_gram = new_gram.reshape(gramlen, gramlen)
        
        for i in range(gramlen):
            for j in range(gramlen):
                new_gram[i][j] = max(gram[2*i][2*j], gram[2*i][2*j+1], \
                                 gram[2*i+1][2*j], gram[2*i+1][2*j+1])
        gram = new_gram
    
    #plt.imshow(gram, cmap='Greys', interpolation='nearest')
    #plt.show()

    return gram


def Usage(num):
    """
    This code written on Python 3.6
    Usage : python getHWPPE.py [Target file]
    """


def Except_Function(filename, error):
    print("error file :", filename)
    print(error)



if __name__ == '__main__' :
#    wb = openpyxl.Workbook()
#    wb.save('Feature.xlsx')
#    sheet = wb.active
    if len(sys.argv) == 2 :
        #directory = sys.argv[2]
        file = "./sample/NAVERCloud/바나나.hwp"
        #OLE_Directory(file)
        OLE_Features = OLE_Extraction(file)
        #print(OLE_Features)
#        sheet['B2'] = file
#        now = 3
#        for i in range(len(OLE_Features)) :
#            sheet.append(OLE_Features[i])
    else :
        print(Usage.__doc__)
