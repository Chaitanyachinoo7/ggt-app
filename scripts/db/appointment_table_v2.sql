
alter table appointments add country varchar(10) null after group_code;

alter table appointments add language varchar(10) null after sample_collection_location_id;

