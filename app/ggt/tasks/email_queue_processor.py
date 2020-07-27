def task_process_email_queue():
    test_email()


def test_email():
    from ggt.lib.email import send_email, render_template

    template_vars = {
        "first_name": "Suresh",
        "test_number": "f4gv34-001",
        "test_location_line1": "Gregory Swanson",
        "test_location_line2": "26 Caesar Canyon Suite 723,",
        "test_location_line3": "West Newell, 62418",
        "test_date": "August 01, 2020",
        "test_time": "11:15AM to 11:30AM",
        "appointment_link": "https://start.gogettested.com/appointment/400800"
    }

    # generate HTML from template
    template_name = 'GGT-1-APPOINTMENT-CONFIRMATION-EMAIL.html'
    html_content = render_template(template_name, **template_vars)

    from_email = "support@gogettested.com"
    from_name = "Go Get Tested"
    to_email = "suresh@wellpay.com"
    subject = "COVID-19 Testing Appointment Confirmation"

    send_email(from_email, from_name, to_email, subject, html_content)
