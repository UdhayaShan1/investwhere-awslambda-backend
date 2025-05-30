import json
import logging
import firebase_admin
from firebase_admin import auth, credentials

logger = logging.getLogger()
logger.setLevel(logging.INFO)

if not firebase_admin._apps:
    firebase_admin.initialize_app(credentials.Certificate('serviceAccountKey.json'))

def lambda_handler(event, context):
    logger.info("Lambda authorizer invoked.")
    try:
        logger.debug(f"Received event: {json.dumps(event)}")
    except Exception as e:
        logger.warning(f"Failed to log event: {e}")

    auth_header = event['headers'].get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        logger.warning("Missing or invalid Authorization header.")
        raise Exception('Unauthorized')

    token = auth_header.split(' ')[1]

    try:
        decoded_token = auth.verify_id_token(token)
        logger.info(f"Token successfully verified for UID: {decoded_token['uid']}")

        return {
            'principalId': decoded_token['uid'],
            'policyDocument': {
                'Version': '2012-10-17',
                'Statement': [{
                    'Action': 'execute-api:Invoke',
                    'Effect': 'Allow',
                    'Resource': event['methodArn']
                }]
            },
            'context': {
                'user': json.dumps(decoded_token)
            }
        }

    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise Exception('Unauthorized')
