import os
import glob
import csv
import datetime
import paramiko
import base64
import random
from PIL import Image

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id,
    whoami
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_batch_execute,
    exec_update,
    read_row,
    read_rows
)

from ggt.lib.storage import (
    file_exists_in_insurance_cards,
    upload_insurance_card_from_base64_string
)

from ggt.lib.email import render_template

import ggt.lib.constants as c


from ggt.lib.adapters.google_adapter import (
    serve_file
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

session_id = generate_session_id()
local_outbound_file_path = get_config_val('vendors.healthtrackrx.local_outbound_file_path')
outbound_file_prefix = get_config_val('vendors.healthtrackrx.outbound_file_prefix')
local_insurance_card_file_path = get_config_val('vendors.healthtrackrx.local_insurance_card_file_path')

async def task_process_misc():
    print('\n\n************************************************\n\n')
    log_generic(
        type=INFO,
        function=whoami(),
        task_session_id=session_id,
        info='Begin Processing Misc Task')

    # upload_insurance_images_to_gcp()
    # sync_appointments_with_schedule_slots()
    # upload_insurance_images_to_gcp_with_small_table()
    # process_email_notifications()
    await upload_insurance_files_from_gstore()

    log_generic(
        type=INFO,
        function=whoami(),
        task_session_id=session_id,
        info='End Processing Misc Task')
    print('\n\n************************************************\n\n')



async def upload_insurance_files_from_gstore():
    try:
        print('converting insurance image files to PDF')
        file_buffer = []
        orders = [400034,400040,400041,400046,400047,400050,400051,400057,400058,400059,400061,400062,400063,400075,400076,400078,400083,400085,400114,400137,400141,400148,400151,400152,400157,400162,400166,400187,400207,400224,400230,400233,400234,400235,400236,400241,400247,400259,400266,400277,400278,400284,400285,400295,400303,400316,400324,400337,400338,400340,400342,400343,400349,400361,400364,400376,400381,400395,400407,400408,400424,400427,400429,400432,400434,400435,400456,400461,400464,400466,400472,400473,400479,400480,400481,400484,400485,400730,400741,400742,400743,400746,400817,400877,400879,400890,400893,400947,400948,401006,401086,401676,401925,401926,401928,402067,402123,402140,402143,402144,402153,402159,402164,402165,402167,402173,402189,402296,402424,402886,402888,403148,403262,403601,403847,403852,404005,404136,404247,404318,404834,404886,405098,405181,405235,405455,405733,405839,406097,406099,407572,407726,407788,407812,407816,407850,407900,407908,407923,407946,407987,408013,408017,408044,408123,408188,408247,408248,408302,408357,408371,408574,408577,409494,409502,409546,409585,409659,409664,409671,409675,409677,409703,409708,409712,409714,409717,409718,409724,409728,409849,409888,409940,409960,409966,409974,409977,409984,409998,410003,410024,410046,410113,410117,410140,410147,410227,410251,410318,410349,410405,410443,410446,410474,410484,410504,410506,410507,410510,410516,410531,410547,410564,410613,410615,410639,410683,410685,410706,410719,410749,410770,410773,410821,410824,410840,410862,410863,410869,410890,410896,410899,410909,410927,410928,410930,410932,410933,410935,410946,410950,410953,410962,410963,410966,410971,410973,410991,410996,411009,411026,411046,411058,411075,411085,411094,411099,411101,411108,411125,411130,411140,411142,411155,411160,411162,411176,411187,411199,411206,411211,411214,411235,411237,411261,411262,411264,411265,411271,411289,411306,411307,411308,411309,411314,411317,411319,411321,411328,411332,411333,411375,411409,411414,411426,411480,411493,411498,411499,411501,411506,411513,411536,411539,411540,411545,411548,411562,411566,411568,411576,411581,411596,411608,411615,411616,411621,411625,411631,411649,411651,411655,411658,411659,411661,411691,411714,411715,411785,411795,411848,411910,411926,411972,412008,412038,412054,412186,412214,412219,412232,412245,412279,412288,412365,412367,412384,412444,412499,412508,412544,412558,412616,412636,412738,412798,412827,412832,412927,412938,412946,412947,412951,412984,413000,413017,413021,413111,413118,413159,413179,413789,414104,414214,414234,414243,414245,414327,414390,414414,414436,414444,414453,414468,414608,414609,414641,414670,414675,414682,414685,414686,414725,414740,414754,414762,414796,414813,414818,414824,414829,414861,414868,414878,414939,414959,414997,415027,415033,415043,415073,415100,415105,415182,415190,415192,415212,415214,415271,415282,415301,415337,415369,415426,415637,415639,415694,415769,415772,415995,415999,416002,416027,416029,416070,416072,416082,416091,416092,416105,416109,416150,416153,416160,416162,416167,416185,416191,416242,416264,416279,416328,416341,416350,416409,416462,416528,416543,416547,416557,416599,416641,416661,416677,416681,416724,416825,416845,416852,416856,416871,416878,416915,416936,417035,417070,417080,417085,417157,417249,417266,417268,417280,417281,417349,417350,417352,417356,417358,417423,417495,417510,417517,417535,417542,417566,417568,417583,417602,417608,417644,417656,417671,417673,417686,417713,417714,417722,417746,417762,417768,417791,417823,417826,417852,417860,417897,417935,417947,417958,417970,417986,417990,418038,418041,418052,418085,418086,418089,418095,418102,418106,418120,418125,418147,418157,418173,418181,418185,418189,418192,418214,418219,418228,418230,418232,418253,418269,418275,418280,418293,418368,418398,418405,418412,418438,418439,418441,418461,418473,418495,418501,418524,418532,418575,418577,418585,418595,418612,418613,418635,418646,418649,418654,418658,418671,418677,418678,418685,418686,418687,418701,418709,418714,418715,418721,418727,418765,418768,418769,418819,418821,418823,418834,418846,418869,418886,418890,418893,418895,418898,418903,418905,418929,418936,418942,418943,418948,418950,418952,418955,418963,418978,418980,418982,418994,418997,419000,419001,419010,419012,419016,419091,419106,419115,419152,419192,419196,419301,419318,419364,419367,419381,419384,419416,419460,419530,419541,419548,419553,419562,419564,419579,419581,419627,419629,419638,419676,419677,419690,419723,419727,419729,419731,419849,419869,419930,420011,420021,420176,420217,420234,420260,420267,420280,420283,420284,420310,420314,420318,420322,420338,420342,420343,420351,420384,420391,420402,420408,420409,420411,420413,420437,420443,420468,420478,420493,420499,420515,420521,420563,420564,420592,420597,420618,420625,420629,420641,420687,420716,420735,420748,420752,420768,420790,420796,420800,420807,420829,420840,420847,420849,420850,420852,420895,420897,420947,420951,420998,420999,421027,421102,421160,421205,421206,421207,421215,421220,421247,421276,421282,421337,421340,421363,421368,421388,421395,421425,421455,421462,421464,421467,421468,421471,421479,421503,421536,421543,421582,421611,421618,421644,421666,421749,421756,421777,421778,421780,421788,421795,421807,421840,421848,421857,421858,421860,421868,421878,421879,421904,421932,421933,421962,421981,422024,422066,422070,422151,422153,422173,422269,422334,422340,422341,422347,422369,422375,422376,422378,422396,422402,422404,422456,422467,422502,422507,422521,422572,422603,422612,422652,422694,422704,422738,422803,422808,422813,422814,422824,422845,422894,422898,422908,422932,422936,422956,423037,424488,424756,426208,426215,426859,428833,428844,428847,428852,428907,429254,429497,429528,429624,429649,429666,429745,429765,429814,429823,429824,429853,429892,429917,429924,429935,429950,429962,429969,429970,430021,430028,430039,430055,430059,430060,430069,430073,430076,430079,430080,430084,430088,430089,430091,430094,430095,430098,430126,430165,430166,430170,430175,430178,430180,430196,430246,430250,430290,430292,430299,430340,430343,430358,430362,430384,430386,430400,430411,430418,430420,430429,430456,430457,430465,430483,430508,430511,430512,430521,430525,430526,430531,430535,430561,430575,430594,430597,430670,430741,430763,430767,430776,430781,430814,430819,430822,430829,430839,430841,430845,430851,430872,430887,430917,430930,430948,430949,430965,430966,430971,430972,430976,430980,430983,430985,430992,430995,431010,431014,431027,431029,431032,431035,431038,431040,431066,431105,431106,431109,431118,431129,431130,431132,431136,431150,431159,431161,431174,431175,431178,431181,431186,431188,431191,431223,431748,453310,460332,468581,469451,470464,470599,471882,472239,472993,473379,473486,473512,473700,474904,474932,477794,477815,478061,478075,478789,479145,479148,481113,481114,481209,481393,481419,481686,481692,481697,482050,482079,482604,483062,483103,483111,483134,483175,483182,483184,483187,483188,483246,483251,483302,483347,483374,483427,483428,483434,483445,483450,483452,483502,483509,483514,483516,483562,483585,483596,483599,483638,483643,483646,483660,483700,483729,483792,483878,483883,483950,483970,484000,484006,484156,484270,484398,484631,484646,484731,484855,484888,484904,484941,485005,485041,485555,485645,485656,485686,485797,485910,485914,485915,485927,485982,486128,486132,486141,486154,486211,486219,486241,486247,486250,486471,486492,486529,486536,486565,486628,486652,486707,486745,486752,486766,486789,486790,486801,486809,486831,486850,486863,486960,486980,486989,486991,487013,487034,487055,487082,487120,487176,487223,487255,487268,487271,487280,487290,487316,487321,487326,487330,487334,487343,487347,487349,487352,487369,487377,487384,487385,487393,487399,487412,487448,487450,487457,487464,487477,487490,487506,487513,487514,487517,487518,487519,487525,487545,487552,487555,487567,487572,487576,487587,487611,487612,487622,487627,487635,487639,487648,487671,487681,487684,487691,487695,487705,487706,487711,487713,487745,487755,487782,487788,487793,487817,487831,487840,487845,487864,487867,487877,487895,487902,487919,487921,487941,487946,487975,487984,487989,487992,487996,488015,488020,488026,488031,488035,488041,488059,488061,488065,488069,488072,488079,488083,488102,488112,488113,488117,488120,488124,488130,488133,488141,488152,488153,488164,488179,488189,488190,488196,488218,488220,488227,488233,488245,488255,488294,488300,488301,488308,488329,488331,488332,488339,488342,488352,488358,488365,488366,488371,488374,488375,488389,488399,488419,488420,488421,488422,488445,488449,488457,488461,488463,488472,488483,488498,488500,488513,488538,488545,488566,488570,488571,488574,488582,488584,488594,488602,488603,488620,488649,488650,488654,488655,488658,488659,488660,488664,488682,488683,488685,488707,488708,488728,488743,488746,488752,488759,488760,488762,488770,488771,488773,488803,488808,488821,488828,488836,488845,488847,488850,488852,488869,488870,488899,488904,488918,488921,488922,488924,488948,488954,488964,488975,488980,488983,488984,488985,488986,488988,488991,489000,489001,489011,489012,489019,489032,489038,489071,489085,489089,489098,489101,489105,489115,489121,489124,489134,489155,489183,489206,489207,489209,489217,489222,489223,489226,489232,489236,489241,489252,489265,489273,489281,489284,489292,489321,489324,489329,489347,489367,489377,489382,489385,489412,489418,489421,489422,489425,489429,489431,489435,489437,489458,489472,489476,489499,489502,489503,489506,489507,489523,489526,489527,489531,489533,489535,489540,489553,489554,489578,489591,489592,489604,489606,489616,489625,489647,489652,489653,489659,489660,489661,489664,489672,489677,489681,489685,489702,489711,489714,489719,489730,489733,489743,489746,489747,489757,489762,489765,489766,489779,489780,489781,489782,489783,489794,489800,489803,489804,489808,489813,489815,489835,489843,489881,489892,489925,489948,489949,489951,489954,489959,489968,489975,489978,489988,490029,490036,490039,490051,490061,490062,490077,490080,490083,490095,490100,490101,490116,490128,490135,490144,490147,490149,490163,490171,490177,490181,490184,490193,490207,490224,490264,490268,490287,490301,490305,490306,490321,490326,490333,490342,490344,490347,490353,490354,490355,490359,490362,490400,490404,490407,490490,490491,490497,509902,516023,516052,519549,520267,520757,520878,521309,521325,521333,521349,521379,521391,521393,521395,521419,521467,521486,521493,521494,521525,521534,521539,521540,521546,521555,521556,521562,521564,521567,521571,521572,521593,521634,521652,521657,521668,521674,521827,521864,521874,521880,521907,521911,521916,521930,521990,521992,522012,522045,522050,522052,538212,557432,558610,562454,562494,562775,568426,569401,569422,569434,569844,572085,572115,574244,574380,575003,575031,575167,575915,575972,576021,576037,576273,576285,576298,576301,576452,576476,577153,577216,577262,577596,577842,578130,578342,578392,578682,578688,578773,578962,579004,579038,579094,579110,579122,579142,579185,579236,579305,579379,579430,579455,579466,579480,579495,579512,579575,579604,579845,579891,579924,580131,580144,580168,580200,580201,580218,580226,580235,580324,580423,580470,580502,580588,580603,580614,580655,580656,580665,580669,580695,580705,580716,580723,580725,580751,580761,580764,580800,580814,580820,580849,580958,580968,580974,580998,581012,581026,581036,581050,581088,581099,581104,581142,581160,581164,581186,581189,581194,581224,581225,581228,581232,581242,581250,581282,581332,581350,581380,581382,581385,581386,581390,581406,581410,581424,581425,581429,581432,581457,581460,581479,581493,581499,581510,581515,581528,581558,581590,581593,581602,581606,581623,581626,581627,581651,581654,581656,581672,581676,581678,581697,581708,428421]
        for appointment_id in orders:
            try:
                file_path_png = "{}/{}_001.png".format(local_insurance_card_file_path, appointment_id)
                filename = "{}_001.pdf".format(appointment_id)
                file_path_pdf = "{}/{}".format(local_insurance_card_file_path, filename)
                blob = await serve_file('ggt-insurance-cards-prod', '{}.png'.format(appointment_id))
                if blob:
                    blob.download_to_filename(file_path_png)
                    Image.open(file_path_png).convert('RGB').save(file_path_pdf)
                    file_buffer.append((filename, file_path_pdf))

            except Exception as err:
                print(err)    
        
        print('uploading insurance files to FTP')
        upload_file_list_to_ftp(file_buffer)

    except Exception as err:
        print(err)


def upload_file_list_to_ftp(file_list):
    try:
        hostname = get_config_val('vendors.healthtrackrx.hostname')
        username = get_config_val('vendors.healthtrackrx.username')
        password = get_config_val('vendors.healthtrackrx.password')
        port = get_config_val('vendors.healthtrackrx.port')

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=hostname,
            username=username,
            password=password,
            port=port
        )

        ftp_client = ssh_client.open_sftp()

        for f in file_list:
            filename = f[0]
            local_file_path = f[1]
            remotepath = "{}/{}".format('', filename)
            ftp_client.put(local_file_path, remotepath)


    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            task_session_id=session_id,
            error=err
        )
    finally:
        ftp_client.close()


def process_sms_notifications():
    rows = get_appointments()
    data = []
    for row in rows:
        phone_number = row['phone_number']
        data.append(
            (phone_number, prepare_sms_text(row))
        )

    batch_enqueue_sms_notifications(data)


def process_email_notifications():
    rows = get_appointments()
    data = []

    for row in rows:
        email = formatted_email_message(row)

        data.append(
            (email['from_email'], email['from_name'],
             email['to_email'], email['subject'], email['html_content'])
        )

    batch_enqueue_email_notifications(data)


def formatted_email_message(row):
    from_email = get_config_val('notifications.from_email')
    from_name = get_config_val('notifications.from_name')
    subject = "{}, Your Appointment has changed".format(row['first_name'])

    template_vars = {
        "first_name": row['first_name']
    }

    template_name = 'GGT-4-APPOINTMENT-RESCHEDULE-EMAIL.html'
    html_content = render_template(template_name, **template_vars)

    email_message = {
        'from_email': from_email,
        'from_name': from_name,
        'to_email': row['email'],
        'subject': subject,
        'html_content': html_content
    }

    return email_message


def batch_enqueue_email_notifications(data):
    try:
        sql = """
            INSERT INTO email_notification_queue
                (from_email, from_name, to_email, subject, html_content)
            VALUES
                (%s, %s, %s, %s, %s);
        """
        exec_batch_execute(sql, data)
        return True

    except Exception as err:
        print("err:", err)
        return False


def batch_enqueue_sms_notifications(data):
    try:
        sql = """
            INSERT INTO sms_notification_queue
                (to_number,message)
            VALUES
                (%s, %s);
        """
        exec_batch_execute(sql, data)

    except Exception as err:
        print("err:", err)


def get_appointments():
    try:
        sql = """
        SELECT 
            p.first_name, p.phone_number, p.email
        FROM
            appointments a
            JOIN patients p ON a.patient_id = p.id 
        WHERE
            location_id IN (152 , 72, 98, 110, 20, 166, 174, 140)
                AND scheduled_dt > '2020-11-23'
                AND status = 'scheduled'
        """
        return read_rows(sql)

    except Exception as err:
        print(err)


def prepare_sms_text(appointment):
    return """Hi {}, we’ve had to close the testing location where you have registered for your COVID-19 test. We apologize for the inconvenience. 

Please visit GoGetTested.com and register for another appointment at a convenient location. Thank you for choosing GoGetTested.

Reply STOP to cancel msgs
    """.format(appointment["first_name"])


def sync_appointments_with_schedule_slots():
    sql = """
        SELECT 
            id, scheduled_dt, location_id
        FROM
            appointments
        WHERE
            scheduled_dt > DATE(NOW())
            AND scheduled_dt < '2020-11-20'
                AND id NOT IN (
                    SELECT 
                        appointment_id
                    FROM
                        schedules
                    WHERE
                        appointment_id IS NOT NULL
                )
    """
    rows = read_rows(sql)
    print('Appointments loaded. Count: {}'.format(len(rows)))

    for row in rows:
        try:
            sql = """
                UPDATE schedules 
                SET 
                    status = 'booked',
                    appointment_id = %s
                WHERE
                    start_dt = %s
                    AND status = 'available' 
                    AND location_id = %s
                LIMIT 1
            """
            vals = (row['id'], row['scheduled_dt'], row['location_id'])
            # if exec_update(sql, vals):
            #    print(row['id'], row['scheduled_dt'])

            print("""UPDATE schedules SET status = 'booked', appointment_id = {} WHERE start_dt = '{}' AND location_id = {} AND status = 'available' LIMIT 1""".format(
                row['id'], row['scheduled_dt'], row['location_id']))

        except Exception as err:
            log_generic(
                type=c.ERROR,
                function=whoami(),
                error=err
            )


def upload_insurance_images_to_gcp():
    limit = 500000
    increment = 1000
    start = random.randint(0, 100000)
    start = 0
    print('starting at: ', start)
    try:
        for i in range(start, limit, increment):
            sql = """
            SELECT 
                q.id, a.id as appointment_id, q.patient_id, insurance_photo
            FROM
                patient_questionnaires q
                    JOIN
                appointments a ON (a.patient_id = q.patient_id)
            LIMIT {},{}
            """.format(i, increment)
            rows = read_rows(sql)

            for row in rows:
                try:
                    qid = row['id']
                    insurance_photo = row['insurance_photo']
                    appointment_id = row['appointment_id']

                    if insurance_photo is None or len(insurance_photo) < 250:
                        pass
                    else:
                        if "," in insurance_photo:
                            base64string = insurance_photo.split(",")[1]

                        dest_file_name = '{}.png'.format(appointment_id)
                        upload_insurance_card_from_base64_string(
                            base64string, 'image/png', dest_file_name)

                        print('uploaded image: {}'.format(dest_file_name))
                        remove_image_from_questionnnaires_table(qid)

                except Exception as err:
                    print(err)

    except Exception as err:
        print(err)


def upload_insurance_images_to_gcp_with_small_table():
    print('starting...')
    try:
        sql = """
        SELECT 
            q.id, a.id as appointment_id, q.patient_id, insurance_photo
        FROM
            patient_questionnaires q
                JOIN
            appointments a ON (a.patient_id = q.patient_id)
        WHERE length(q.insurance_photo)>10
        LIMIT 100
        """
        rows = read_rows(sql)

        for row in rows:
            try:
                qid = row['id']
                insurance_photo = row['insurance_photo']
                appointment_id = row['appointment_id']

                if insurance_photo is None or len(insurance_photo) < 250:
                    pass
                else:
                    if "," in insurance_photo:
                        base64string = insurance_photo.split(",")[1]

                    dest_file_name = '{}.png'.format(appointment_id)
                    upload_insurance_card_from_base64_string(
                        base64string, 'image/png', dest_file_name)

                    print('uploaded image: {}'.format(dest_file_name))
                    remove_image_from_questionnnaires_table(qid)

            except Exception as err:
                print(err)

    except Exception as err:
        print(err)


def remove_image_from_questionnnaires_table(id):
    try:
        sql = """
        UPDATE patient_questionnaires 
        SET 
            insurance_photo = 1
        WHERE
            id = %s
        """
        val = (id,)
        result = exec_update(sql, val)
        pass

    except Exception as err:
        print(err)
