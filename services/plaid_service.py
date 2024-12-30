import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.payment_initiation_payment_create_request import PaymentInitiationPaymentCreateRequest

class PlaidService:
    def __init__(self):
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,
            api_key={
                'clientId': os.environ.get('PLAID_CLIENT_ID'),
                'secret': os.environ.get('PLAID_SECRET'),
            }
        )
        self.client = plaid_api.PlaidApi(plaid.ApiClient(configuration))
        self.charity_account = os.environ.get('CHARITY_ACCOUNT_ID', 'acc_charity_sandbox')

    def create_link_token(self, user_id):
        """Create a link token for Plaid Link initialization"""
        try:
            request = LinkTokenCreateRequest(
                products=[Products('auth')],
                client_name="HabitBuilder",
                country_codes=[CountryCode('US')],
                language='en',
                user=LinkTokenCreateRequestUser(
                    client_user_id=str(user_id)
                )
            )
            response = self.client.link_token_create(request)
            return response.link_token
        except plaid.ApiException as e:
            print(f"Error creating link token: {e}")
            return None

    def exchange_public_token(self, public_token):
        """Exchange public token for access token"""
        try:
            response = self.client.item_public_token_exchange(
                {'public_token': public_token}
            )
            return response.access_token
        except plaid.ApiException as e:
            print(f"Error exchanging public token: {e}")
            return None

    def create_payment(self, access_token: str, account_id: str, amount: float):
        """Create a payment from user account to charity account"""
        try:
            request = PaymentInitiationPaymentCreateRequest(
                access_token=access_token,
                account_id=account_id,
                recipient_id=self.charity_account,
                amount={
                    'currency': 'USD',
                    'value': amount
                },
                description="Habit failure penalty"
            )
            response = self.client.payment_initiation_payment_create(request)
            return response.payment_id
        except plaid.ApiException as e:
            print(f"Error creating payment: {e}")
            return None
