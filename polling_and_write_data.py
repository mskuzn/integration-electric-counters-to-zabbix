#!/usr/bin/python3
#в интеграцию запихнуть скрин и графики
#jсталось в интеграционном скрипте оставить ваты вместо киловатов
import serial
import time
import io
import codecs
import psycopg2
import random
import time
from pyzabbix import ZabbixMetric, ZabbixSender


class db_operations:
    def __init__(self, db, usr, hst, pswd):
       	self.connect = psycopg2.connect(database=db, user=usr, host=hst, password=pswd)
        self.cursor = self.connect.cursor()
        self.arr_items_to_fill = []
    def get_items_active_energy(self):
        self.cursor.execute("""select itemid, replace(hst.type_full, 'k_','') as k_transform, itm.name as itm_name,substring(key_ from '.*\[(.*)\].*') as dev_id, os as address from items itm
		inner join host_inventory hst on hst.hostid = itm.hostid
		where itm.name like 'active_energy';""") #'active_energy'
        for row in self.cursor:
            self.arr_items_to_fill.append(row)
        return self.arr_items_to_fill
    def send_to_history(self,itemid,value):
        insert_history="INSERT INTO history_uint VALUES ("+str(itemid)+",split_part(EXTRACT(EPOCH FROM now())::text,'.',1)::int,"+str(value)+",(('0.' || split_part(EXTRACT(EPOCH FROM now())::text,'.',2))::float)*10^(9)::int);"
        self.cursor.execute(insert_history)
#        print(insert_history)
#        print(self.cursor.statusmessage)
        self.connect.commit()
    def con_close(self):
        self.connect.close()


def add_crc16(in_hex_str): #Расчёт CRC передаём hex в виде текста пример: '1E010202020202020231A7'

    dat=codecs.decode(in_hex_str,'hex')
    crc = 0xFFFF 
    l = len(dat)
    i = 0
    while i < l:
        j = 0
        crc = crc ^ dat[i]
        while j < 8:
            if (crc & 0x1):
                mask = 0xA001
            else:
                mask = 0x00
            crc = ((crc >> 1) & 0x7FFF) ^ mask
            j += 1
        i += 1
    if crc < 0:
        crc -= 256
    b1=hex(crc % 256).replace('0x','')
    b2=hex(crc // 256).replace('0x','')
    if (len(b1)==1) : b1='0'+b1
    if (len(b2)==1) : b2='0'+b2
    result = (in_hex_str+b1+b2)
    return result


def get_data(msg): # добавить исключения
    ser = serial.Serial("/dev/ttyUSB0", timeout=0.2)
    ser.write(codecs.decode(msg, 'hex'))
    respon = ser.read(10)
    ser.close()
    return codecs.encode(respon, 'hex')

def address_to_hex(arg):
    z=hex(int(arg))
    z=z.replace('0x','')
    if len(z)==1:
        z='0'+z
    return z

#################


zabbix = db_operations('zabbix', 'zabbix', 'localhost', 'controller25')

items_arr = zabbix.get_items_active_energy()

for row in items_arr:
    itemid=row[0]
    k_transform=row[1]
    metric_type=row[2]
    dev_id=row[3]
    address=row[4]
#    value=2**random.randint(1, 10) #test

    node_id=address_to_hex(address)#'1e' для тестового
    password_hex='020202020202'#переключить на поля БД '02020202020202'

    massage_start_chennel=add_crc16((node_id+'00'))
    massage_connect=add_crc16((node_id+'0102'+password_hex))
#    massage_all_tariff=add_crc16((node_id+'0814F0'))
    massage_all_tariff=add_crc16((node_id+'050000')) #'050000' кое что есть
#    print('device'+'---'+dev_id+'---'+node_id)
    get_data(massage_start_chennel)
    get_data(massage_connect)
    k=list(str(get_data(massage_all_tariff)))#.replace('b','').replace('\'',''))
    if len(k)>10:
        value=int((k[6]+k[7]+k[4]+k[5]+k[10]+k[11]+k[8]+k[9]),16)
#        print(value)
        get_data(massage_all_tariff)
        zabbix.send_to_history(itemid,(value))
zabbix.con_close()
#    print('######')

#1e 10 00 1f 02 ffffffff07
#01 23 45 67 89
#перед подачей в БД сделать умножение на коэффициент
#    zabbix.send_to_history(itemid,value) 



#1049.12





