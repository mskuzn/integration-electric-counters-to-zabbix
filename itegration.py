#! /usr/bin/env python3
from zabbix.api import ZabbixAPI
import re

#Шаблоны для параметров API

create_host_param = {
    "host": None,
    "name":None,
    "interfaces": [
        {
            "type": 1,
            "main": 1,
            "useip": 1,
            "ip": "127.0.0.1",
            "dns": "",
            "port": "10050"
       }
    ],
    "groups": [
        {
            "groupid": "15"
        }
    ],
    "inventory_mode": 0,
    "inventory": {
        "type": None,
        "type_full": None,
        "name" : None
    }
}
create_item_param = {
    "name": None,
    "key_": None,
    "hostid": None,
    "type": 2,
    "value_type": 3,
    "units":None,
    "trends":731000,
    "history":73100

}

create_graph_param = {
    "name": None,
    "width": 900,
    "height": 200,
    "gitems": [
        {
            "itemid": None,
            "color": "00AA00"
        }
     ]
}


create_screen_param = {
    "name": "Active_power_current_value",
    "hsize": 1,
    "vsize": None,
    "screenitems": [
        {
            "resourcetype": 0,
            "resourceid": None,
            "rowspan": 1,
            "colspan": 1,
            "x": 0,
            "y": None,
            "height": 300,
            "width": 1000
          }
     ]
}


##################
zapi = ZabbixAPI(url='http://localhost/zabbix/', user='Admin', password='zabbix')
itegration_data = open('itegration_data.txt')

itegration_data_mass=[]
i=0
for line in itegration_data:
    line=line.replace('\n',"")
    mas_line=line.split('\t')

    tension=mas_line[0]
    place=mas_line[1]
    k_transform=mas_line[2]
    sn=mas_line[3]
    model=mas_line[4]
    net_address=mas_line[5]
    passwd=mas_line[6]

    create_host_param['host']=sn
    create_host_param['name']=model+"_"+sn
    create_host_param['inventory']['type']="limit_"+tension
    create_host_param['inventory']['type_full']="k_"+str(k_transform)
    create_host_param['inventory']['name']=place
    create_host_param['inventory']['alias']=model
    create_host_param['inventory']['os']=net_address
    create_host_param['inventory']['os_full']=passwd
#    try:
    host_id=zapi.do_request('host.create',create_host_param)['result']['hostids'][0]
#        try:
    create_item_param['name']='active_energy'
    create_item_param['key_']='active_energy[' + sn + ']'
    create_item_param['hostid']=host_id
    create_item_param['units']='kilovatt*chas'
    
    item_id=zapi.do_request('item.create',create_item_param)['result']['itemids'][0]


    create_graph_param['name']="active_energy | "+place+" | SN-"+str(sn)
    create_graph_param['gitems'][0]['itemid']=int(item_id)
    graph_id=zapi.do_request('graph.create',create_graph_param)['result']['graphids'][0]

    if i!=0:
        create_screen_param['screenitems'].append(create_screen_param['screenitems'][i-1].copy())
    create_screen_param['screenitems'][i]['resourceid']=int(graph_id)
    create_screen_param['screenitems'][i]['y']=int(i)
    i+=1
create_screen_param['vsize']=i+1
screen_id=zapi.do_request('screen.create',create_screen_param)['result']['screenids'][0]
#        except Exception:
#            print('faled_item_create')
#    except Exception:
#        print('faled_host_create')




