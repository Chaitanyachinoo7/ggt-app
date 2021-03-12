import stripe
from ggt.lib.utils import (
    get_config_val,
)

stripe_secret_key = get_config_val('payment.stripe.secret_key')
stripe.api_key = stripe_secret_key


# From the request body generate the stripe request body
def generate_stripe_checkout_request_body(payment_details):
    stripe_checkout_request = {
        'payment_method_types': payment_details.payment_methods,
        'mode': payment_details.mode,
        'success_url': payment_details.navigation.success_url,
        'cancel_url': payment_details.navigation.cancel_url,
        'line_items': [],
        'locale': payment_details.locale
    }
    for item in payment_details.line_items:
        line_item = {
            'price_data': {
                'currency': payment_details.currency,
                'unit_amount': int(item.unit_price * 100),  # Convert to cents
                'product_data': {
                    'name': item.product_name,
                    'images': item.product_images
                }
            },
            'quantity': item.quantity
        }
        stripe_checkout_request['line_items'].append(line_item)
    return stripe_checkout_request


# Util function to minify the Stripe session response
def minify_stripe_session_response(stripe_response):
    return {
        'id': stripe_response.id,
        'payment_status': stripe_response.payment_status,
        'customer_email': stripe_response.customer_email
    }


# Transform en to en-US if the locale is us
def transform_customer_locale(locale):
    return locale if locale != 'en' else 'en-US'


# This function will create a customer for checkout session
def create_checkout_customer(payment_details):
    stripe_customer_response = stripe.Customer.create(
        description=payment_details.id,
        # Send the locale so that emails are sent according to preferred locale
        preferred_locales=[transform_customer_locale(payment_details.locale)]
    )
    # Return the customer id only
    return stripe_customer_response.id


def create_checkout_session(payment_details):
    customer_id = create_checkout_customer(payment_details)
    stripe_checkout_request = generate_stripe_checkout_request_body(payment_details)
    stripe_response = stripe.checkout.Session.create(
        payment_method_types=stripe_checkout_request['payment_method_types'],
        line_items=stripe_checkout_request['line_items'],
        mode=stripe_checkout_request['mode'],
        success_url=stripe_checkout_request['success_url'],
        cancel_url=stripe_checkout_request['cancel_url'],
        locale=stripe_checkout_request['locale'],
        billing_address_collection='required',  # Always include billing address
        customer=customer_id
    )
    # Only required item is the session id
    # Replace this by a util if more than one field is required
    return stripe_response.id


def retrieve_checkout_session(session_id):
    return minify_stripe_session_response(stripe.checkout.Session.retrieve(session_id))
