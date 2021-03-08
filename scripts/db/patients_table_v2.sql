-- Add a new column to track the country
alter table patients add country varchar(5)

-- Set default country as 'US'
update patients set country='US' where 1=1