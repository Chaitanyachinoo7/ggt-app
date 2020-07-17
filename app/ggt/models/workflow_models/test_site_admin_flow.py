'''
def generate_full_schedule(location_id, start_date, day_count):
    record = __read_record_schedule_generation_rules_by_location_id(location_id):
    if(record):
        daily_hours =
        hourly_slots =

        #[Number of Days] x [Number of incremental slots] x [Multiplier]
        for count in range(day_count):
            schedule_day = (datetime.strptime(start_date, '%Y-%m-%d') +
                            timedelta(days=count)).strftime('%Y-%m-%d')  # e.g. 2020-06-28

            return __insert_record_patients(data)
        else:
            return False
    except Exception as err:
        logging.error("finalize_signup-failed: {}".format(err))
        return False
'''
