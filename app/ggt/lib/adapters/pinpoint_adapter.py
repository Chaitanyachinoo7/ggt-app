import boto3
from botocore.exceptions import ClientError
from ggt.lib.utils import (
    get_config_val,
    log_generic
)

def send_pinpoint_message(sender_number="+18013867767", sender_id="MySenderID", recipient_number="+18018602474", message="Test"):

    # The AWS Region that you want to use to send the message. For a list of
    # AWS Regions where the Amazon Pinpoint API is available, see
    # https://docs.aws.amazon.com/pinpoint/latest/apireference/
    region = "us-east-1"

    # The phone number or short code to send the message from. The phone number
    # or short code that you specify has to be associated with your Amazon Pinpoint
    # account. For best results, specify long codes in E.164 format.
    originationNumber = sender_number

    # The recipient's phone number.  For best results, you should specify the
    # phone number in E.164 format.
    destinationNumber = recipient_number

    # The content of the SMS message.
    #message = message

    # The Amazon Pinpoint project/application ID to use when you send this message.
    # Make sure that the SMS channel is enabled for the project or application
    # that you choose.
    applicationId = "a8ac26c313a6407385ca0846d72b0d28"

    # The type of SMS message that you want to send. If you plan to send
    # time-sensitive content, specify TRANSACTIONAL. If you plan to send
    # marketing-related content, specify PROMOTIONAL.
    messageType = "TRANSACTIONAL"

    # The registered keyword associated with the originating short code.
    registeredKeyword = "myKeyword"

    # The sender ID to use when sending the message. Support for sender ID
    # varies by country or region. For more information, see
    # https://docs.aws.amazon.com/pinpoint/latest/userguide/channels-sms-countries.html
    senderId = sender_id

    # Create a new client and specify a region.
    client = boto3.client(
        'pinpoint',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=region)
    try:
        response = client.send_messages(
            ApplicationId=applicationId,
            MessageRequest={
                'Addresses': {
                    destinationNumber: {
                        'ChannelType': 'SMS'
                    }
                },
                'MessageConfiguration': {
                    'SMSMessage': {
                        'Body': message,
                        'Keyword': registeredKeyword,
                        'MessageType': messageType,
                        'OriginationNumber': originationNumber,
                        'SenderId': senderId
                    }
                }
            }
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Message sent! Message ID: "
                + response['MessageResponse']['Result'][destinationNumber]['MessageId'])

