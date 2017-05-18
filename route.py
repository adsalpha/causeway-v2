from flask import Flask, request
from pymongo import MongoClient
from template import Template
from copy import deepcopy
from checks import *
import uuid
import time
import json
import config

app = Flask(__name__)
app.template_folder = 'json'

client = MongoClient('127.0.0.1', 27017)
db = client.get_database(config.db_name)
jobs_collection = db.get_collection(config.jobs_collection)
users_collection = db.get_collection(config.users_collection)
requests_collection = db.get_collection(config.users_collection)


# SERVICE


@app.route('/')
def info():
    """
    Information about the server and its status.
    """
    template = Template(config.server_info)
    template.populate(url = config.server_url,
                      name = config.server_name,
                      pricing_type = config.pricing_type,
                      free_data = config.free_data,
                      description = config.description)
    return json.dumps(template)


@app.route('/nonce')
def request_id():
    """
    A unique ID which identifies a Causeway request.
    The IP address the request came from is also logged for security reasons.
    """
    nonce = str(uuid.uuid4())
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    requests_collection.insert({'nonce': nonce, 'ip': ip})
    return json.dumps({'nonce': nonce})


# JOBS


@app.route('/jobs/add', methods = ['POST'])
def create_job():
    """
    Add a job.
    """
    (job, errors) = check_request(request, config.incoming_job)

    # Job-specific checks

    if not check_incoming_job_crypto(deepcopy(job)):
        errors.append(config.incoming_document_crypto_error)
    if check_duplicate_job(job['job']['id']):
        errors.append(config.duplicate_job_error)

    if not errors:
        job['status'] = 'posted'
        jobs_collection.insert(job)
        return success()
    else:
        return error(errors)


@app.route('/jobs')
def jobs():
    """
    Active jobs registered with this server.
    Returns an error if no jobs are available.
    """
    jobs_to_return = []
    for job in jobs_collection.find({}, {'_id': False}):
        if job['time']['expires_at'] >= time.time():
            jobs_to_return.append(job)
    return query_result(jobs_to_return, 'jobs')


@app.route('/jobs/<string:job_id>')
def job_by_id(job_id):
    """
    A job with the specified ID.
    Returns an error if not found.
    """
    job = jobs_collection.find({'id': job_id}, {'_id': False})
    return query_result(job, 'job')


# TODO - Include or delete this
# @app.route('/jobs/<string:job_id>/worker')
# def job_worker(job_id):
#     """
#     The user whom a job was awarded to.
#     If job was not awarded to anybody, returns an error.
#     """
#     return redirect(url_for('user_by_id'))


# BIDS


@app.route('/jobs/<string:job_id>/bids/add', methods=['POST'])
def add_bid_to_job(job_id):
    """
    Bid for a job.
    """
    (bid, errors) = check_request(request, config.incoming_bid)
    if bid:
        bid.pop('job')
        raw_result = jobs_collection.update_one({'id': job_id}, {'$addToSet': {'bids': bid}})
        return update_result(raw_result, document_type = 'bid')
    else:
        return error(errors)


@app.route('/jobs/<string:job_id>/bids')
def job_bids(job_id):
    """
    All bids for a job.
    Returns an error if no bids are available.
    """
    bids_to_return = []
    for bid in jobs_collection.find({'id': job_id}, {'_id': False, 'bids': True}):
        bids_to_return.append(bid)
    return query_result(bids_to_return, 'bids')


@app.route('/jobs/<string:job_id>/bids/<string:user_id>')
def job_bid_by_id(job_id, user_id):
    """
    A specific bid submitted to a job.
    Returns an error if bid does not exist.
    """
    bid = jobs_collection.find(
        {'job': {'id': job_id}, 'bids': {'$elemMatch': {'worker': {'name': user_id}}}},
        {'_id': False, 'bids.$': True}
    )
    return query_result(bid, 'bid')


# OFFERS


@app.route('/jobs/<string:job_id>/creator/accept-bid', methods = ['POST'])
def create_offer_for_job(job_id):
    """
    Award a job to a bidder. The URL should contain the 'id' parameter.
    Returns an error if the URL is invalid or the ID is invalid.
    """
    (offer, errors) = check_request(request, config.incoming_offer)
    if offer:
        offer.pop('job')
        raw_result = jobs_collection.update_one({'id': job_id}, {'$set': {'offer': offer}})
        return update_result(raw_result, document_type='offer')
    else:
        return error(errors)


@app.route('/jobs/<string:job_id>/offer/<string:bid_id>', methods = ['GET', 'POST'])
def offer(job_id, bid_id):
    if bid_id is None:
        jobs_collection.find({'id': job_id}, {'_id': False, 'offer': True})


# DELIVERIES


@app.route('/jobs/<string:job_id>/deliver', methods = ['POST'])
def add_delivery(job_id):
    """
    Submit a delivery.
    """
    (delivery, errors) = check_request(request, config.incoming_delivery)
    if delivery:
        delivery.pop('job')
        raw_result = jobs_collection.update_one({'job': {'id': job_id}}, {'$addToSet': {'deliveries': delivery}})
        return update_result(raw_result, document_type='delivery')
    else:
        return error(errors)


@app.route('/jobs/<string:job_id>/deliveries')
def job_deliveries(job_id):
    """
    What a user submitted for a job delivery.
    Returns an error if no delivery has yet been submitted.
    """
    deliveries = jobs_collection.find(
        {'job': {'id': job_id}},
        {'_id': False, 'deliveries': True}
    )
    return query_result(deliveries, 'bid')



@app.route('/jobs/<string:job_id>/creator/accept-delivery', methods = ['POST'])
def accept_delivery(job_id):
    """
    Accept a delivery.
    """
    (delivery_accepted, errors) = check_request(request, config.incoming_accept_delivery)
    if delivery_accepted:
        raw_result = jobs_collection.update_one({'job': {'id': job_id}}, {'$set': {'delivery_accepted': True}})
        return update_result(raw_result, document_type='delivery acceptance')
    else:
        return error(errors)


# DISPUTES


@app.route('/jobs/<string:job_id>/file-dispute', methods = ['POST'])
def add_dispute(job_id):
    """
    File a dispute.
    """
    (dispute, errors) = check_request(request, config.incoming_dispute)
    if dispute:
        dispute.pop('job')
        # TODO - Can multiple disputes be filed?
        raw_result = jobs_collection.update_one(
            {'job': {'id': job_id}},
            {'$set': {'dispute': dispute}}
        )
        return update_result(raw_result, document_type='dispute')
    else:
        return error(errors)


@app.route('/jobs/<string:job_id>/dispute')
def job_disputes(job_id):
    """
    Disputes that were filed for a job.
    Returns an error if no dispute was filed.
    """
    disputes = jobs_collection.find(
        {'job': {'id': job_id}},
        {'_id': False, 'disputes': True}
    )
    return query_result(disputes, 'bid')


@app.route('/jobs/<string:job_id>/resolve-dispute')
def finish_dispute(job_id):
    """
    Cancel or finish a dispute.
    """
    (resolution, errors) = check_request(request, config.incoming_dispute_resolution)
    if resolution:
        resolution.pop('job')
        raw_result = jobs_collection.update_one(
            {'job': {'id': job_id}},
            {'$set': {'dispute': {'resolution': resolution['resolution']}}}
        )
        raw_result2 = jobs_collection.update_one(
            {'job': {'id': job_id}},
            {'$set': {'dispute': {'resolution': {'validity': resolution['validity']}}}}
        )
        return update_result(raw_result, document_type='dispute')
    else:
        return error(errors)


# USERS


@app.route('/users/add', methods = ['POST'])
def add_user():
    """
    Add a user.
    """
    (user, errors) = check_request(request, config.incoming_user)
    if user:
        users_collection.insert(user)
        return success()
    else:
        return error(errors)


@app.route('/users')
def users():
    """
    All users registered with a server.
    """
    users_to_return = []
    for user in users_collection.find({}, {'_id': False}):
        users_to_return.append(user)
    return query_result(users_to_return, 'users')

@app.route('/users/exists/<string:delegate_address>')
def does_user_exist(delegate_address):
    """
    Checks whether a user is registered with a server.
    """
    users = users_collection.find({'bitcoin.delegate_address': delegate_address})
    return str(users.count() > 0)

@app.route('/users/<string:user_id>')
def user_by_id(user_id):
    """
    Information on a specific user.
    """
    user = jobs_collection.find({'contact': {'id': user_id}}, {'_id': False})
    return query_result(user, 'user')


@app.route('/users/<string:user_id>/jobs/awarded')
def user_awarded_jobs(user_id):
    """
    Jobs awarded to a user.
    """
    jobs_to_return = []
    for job in jobs_collection.find({}, {'_id': False}):
        if job['worker']['id'] == user_id:
            jobs_to_return.append(job)
    return query_result(jobs_to_return, 'jobs')


@app.route('/users/<string:user_id>/jobs/delivered')
def user_delivered_jobs(user_id):
    """
    Jobs for which a user submitted a delivery.
    """
    jobs_to_return = []
    for job in jobs_collection.find({}, {'_id': False}):
        if job['worker']['id'] == user_id and 'deliveries' in job:
            jobs_to_return.append(job)
    return query_result(jobs_to_return, 'jobs')


@app.route('/users/<string:user_id>/jobs/finished')
def user_finished_jobs(user_id):
    """
    Jobs accomplished by a user.
    """
    jobs_to_return = []
    for job in jobs_collection.find({}, {'_id': False}):
        if job['worker']['id'] == user_id and \
                ('delivery_accepted' in job or
                     ('dispute' in job and 'resolution' in job['dispute'])):
            jobs_to_return.append(job)
    return query_result(jobs_to_return, 'jobs')


if __name__ == '__main__':
    app.run()