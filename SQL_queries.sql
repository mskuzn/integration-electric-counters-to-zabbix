
--Выборка хостов из группы energo_counters
with energo_counters as (select hg.hostid as gr_name from groups g
left join hosts_groups hg on hg.groupid=g.groupid
where g.name like 'energo_counters')

select * from items where hostid in (select * from energo_counters)
;
------------
