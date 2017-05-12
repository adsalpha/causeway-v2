# Server description


server_url = 'SERVER_URL'
server_name = 'SERVER_NAME'
description = 'Rein Causeway v2'
pricing_type = 'per_document'
free_data = 500


# Database


db_name = 'rein_causeway'
jobs_collection = 'jobs'
users_collection = 'users'
requests_collection = 'requests'

# Templates


template_dir = 'json'
server_info = 'server_info'
job = 'job'
bid = 'bid'
offer = 'offer'
delivery = 'delivery'
dispute = 'dispute'
resolution = 'resolution'


# Incoming document structure


incoming_payload = ['key', 'value', 'nonce', 'signature', 'signature_address', 'owner', 'testnet']
incoming_user = [{'contact': ['login', 'email']},
                 {'bitcoin': ['master_address', 'delegate_address']},
                 {'mediator': ['status', 'fee', 'key']},
                 {'validity': ['sin', 'signature', 'signature_address']}]
incoming_job = [{'job': ['id', 'name', 'description', 'tags']},
                {'time': ['block_hash', 'created_at', 'expires_at']},
                {'creator': ['login', 'contact', 'url']},
                {'mediator': ['login', 'contact', 'fee', 'url']},
                {'validity': ['signature', 'signature_address']}]
incoming_bid = [{'job': ['id', 'url']},
                {'time': ['created_at']},
                {'worker': ['login', 'contact', 'amount', 'url']},
                {'validity': ['signature', 'signature_address']}]
incoming_offer = [{'job': ['id', 'url']},
                  {'time': ['created_at']},
                  {'worker': ['escrow_address', 'escrow_pubkey' 'redeem_script', 'tx_fee', 'login', 'bid_url']},
                  {'creator': ['escrow_pubkey']},
                  {'mediator': ['escrow_address', 'redeem_script', 'tx_fee', 'fee']},
                  {'validity': ['signature', 'signature_address']}]
incoming_delivery = [{'job': ['id', 'url']},
                     {'deliverables': ['description', 'url']},
                     {'validity': ['signature', 'signature_address']}]
incoming_accept_delivery = [{'job': ['id', 'url']},
                            {'worker_payment': ['inputs', 'address', 'amount', 'sig', 'txid', 'client_sig']},
                            {'mediator_payment': ['inputs', 'address', 'amount, ''client_sig']},
                            {'validity': ['signature', 'signature_address']}]
incoming_dispute = [{'job': ['id', 'url']},
                    {'details': ['type', 'description']},
                    {'validity': ['signature', 'signature_address']}]
incoming_dispute_resolution = [{'job': ['id', 'url']},
                               {'resolution': ['winner', 'description']},
                               {'validity': ['signature', 'signature_address']}]
incoming_accept_resolution = [{'job': ['id', 'url']},
                              {'worker_payment': ['inputs', 'address', 'amount', 'sig', 'txid', 'client_sig']},
                              {'mediator_payment': ['inputs', 'address', 'amount, ''client_sig']},
                              {'validity': ['signature', 'signature_address']}]


# Errors


def document_add_error(doc_type):
    return 'Cannot add ' + doc_type + '. Check if the job exists.'
incoming_document_integrity_error = 'Incoming document does not meet the current requirements. Try updating Rein.'
incoming_document_crypto_error = 'Incoming document has been changed without authorization.'
invalid_request_error = 'Invalid nonce or IP. Please request a new nonce via /nonce.'
duplicate_job_error = 'A job with this ID already exists.'