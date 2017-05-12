import json
import config
from bitcoin.signmessage import BitcoinMessage, VerifyMessage
from hashlib import sha256
from route import users_collection, jobs_collection, requests_collection


def user_exists(name):
    """
    Checks if user is registered with Rein.
    """
    if users_collection.find({'name': name}) == 1:
        return True
    else:
        return False


def error(message):
    error = {'result': 'error', 'message': message}
    return json.dumps(error)


def success(message = None):
    if message:
        success = {'result': 'success', 'message': message}
    else:
        success = {'result': 'success'}
    return json.dumps(success)


def check_request_nonce_and_ip(nonce, ip):
    if requests_collection.find_one({'nonce': nonce, 'ip': ip}):
        return True
    else:
        return False


def check_incoming_document_structure(request_doc, doc_model):
    for dic in doc_model:
        for key in dic:
            for field in dic[key]:
                if field not in request_doc[key]:
                    return False
    return True


def check_incoming_job_crypto(job):
    job_id = job['job'].pop('id')
    if job_id == sha256(json.dumps(job).encode('utf-8')).hexdigest():
        validity = job.pop('validity')
        if VerifyMessage(validity['signature_address'], BitcoinMessage(json.dumps(job)), validity['signature']):
            return True
    else:
        return False


def check_duplicate_job(job_id):
    if jobs_collection.find({'job.id': job_id}):
        return True
    else:
        return False


def check_request(request, doc_type):
    nonce = request.form['nonce']
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    document = json.loads(request.form['value'])

    errors = []
    if not check_request_nonce_and_ip(nonce, ip):
        errors.append(config.invalid_request_error)
    if not check_incoming_document_structure(document, doc_type):
        errors.append(config.incoming_document_integrity_error)

    if errors:
        return (None, errors)
    else:
        return (document, None)


def update_result(raw_result, document_type):
    if raw_result.modified_count != 1:
        return error(config.document_add_error(document_type))
    else:
        return success()


def query_result(raw_result, document_type):
    if raw_result:
        return json.dumps(raw_result)
    else:
        return error(document_type.capitalize() + ' not available.')