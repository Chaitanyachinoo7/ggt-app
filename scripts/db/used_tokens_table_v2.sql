alter table used_tokens
	add appointment_1_id int null after token;

alter table used_tokens
	add appointment_2_id int null after appointment_1_id;
