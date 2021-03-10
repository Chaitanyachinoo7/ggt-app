import stripe
import unittest
from unittest.mock import Mock

from ggt.lib.adapters.stripe_adapter import create_checkout_session
from ggt.models.data_models.data_types import PaymentRequestBody, PaymentRequestLineItem, PaymentRequestNavigation


# This class mimics the response from strip session
class StripeSession:
    def __init__(self, session_id):
        self.id = session_id

# This class mimics the response from strip customer creation
class StripeCustomer:
    def __init__(self, customer_id):
        self.id = customer_id

class StripeAdapterTest(unittest.TestCase):

    def test_create_checkout_session(self):
        # This is mock response from strip checkout session create
        stripe_session = StripeSession(2)
        stripe_customer = StripeCustomer("123456")

        # Mock the Strip checkout session create
        stripe.checkout.Session.create = Mock(name='create', return_value=stripe_session)
        stripe.Customer.create = Mock(name='customer_create', return_value=stripe_customer)

        # Create the Payment request
        payment_request_body = PaymentRequestBody()

        payment_request_line_item = PaymentRequestLineItem()
        payment_request_navigation = PaymentRequestNavigation()

        # Define navigations
        payment_request_navigation.cancel_url = "http://cancel.com"
        payment_request_navigation.success_url = "http://success.com"

        # Deine a line item
        payment_request_line_item.unit_price = 20
        payment_request_line_item.quantity = 1
        payment_request_line_item.product_images = ['http://image-url.com']
        payment_request_line_item.product_name = 'payment'

        # Set to payment request body
        payment_request_body.line_items = [payment_request_line_item]
        payment_request_body.navigation = payment_request_navigation

        # Invoke the create session method
        session_id = create_checkout_session(payment_request_body)

        # It should return correct session id
        self.assertEqual(session_id, 2)

        # Stripe checkout session create should be called with correct params
        stripe.checkout.Session.create.assert_called_once_with(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': 2000,
                    'product_data': {
                        'name': 'payment',
                        'images': ['http://image-url.com']
                    }
                },
                'quantity': 1
            }],
            mode='payment',
            success_url='http://success.com',
            cancel_url='http://cancel.com',
            locale='en',
            billing_address_collection='required',
            customer=stripe_customer.id
        )

    def test_failure_with_invalid_payload(self):
        exception = None
        try:
            # Mock stripe
            stripe.checkout.Session.create = Mock(name='create')
            # We are sending a empty payment body
            payment_request = PaymentRequestBody()
            payment_navigation = PaymentRequestNavigation()
            payment_navigation.cancel_url = "http://cancel.com"
            payment_navigation.success_url = "http://success.com"
            payment_request.navigation = payment_navigation

            create_checkout_session(payment_request)
        except Exception as e:
            # Line items was not set hence exception is thrown here
            exception = e

        self.assertIsNotNone(exception)
