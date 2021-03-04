-- Add new column country to locations table
alter table locations add country varchar(5)

-- Update default country as 'US'
update locations set country='US' where 1=1
