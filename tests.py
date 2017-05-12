from bitcoin.wallet import CBitcoinSecret
from bitcoin.signmessage import BitcoinMessage, SignMessage
from binascii import unhexlify
from bitcoin import base58
from hashlib import *
import requests
import time
import json
import hashlib

def ripemd160(string):
	h = new('ripemd160')
	h.update(string)
	return h.hexdigest()

def generate_sin(master_key):
    """Generates a type 2 'Secure Identity Number' using the bip32 master public key"""
    prefix = 0x0F
    sin_type = 0x02
    # Convert master key to hex if necessary
    try:
        master_key = unhexlify(master_key)
    except:
        pass

    # Step 1 (SHA-256 of public key)
    step_1 = sha256(master_key.encode('utf-8')).hexdigest()
    # Step 2 (RIPEMD-160 of Step 1)
    step_2 = ripemd160(unhexlify(step_1))
    # Step 3 (Prefix + SIN_Version + Step 2)
    step_3 = '{0:02X}{1:02X}{2}'.format(prefix, sin_type, step_2)
    # Step 4 (Double SHA-256 of Step 3)
    step_4_1 = unhexlify(step_3)
    step_4_2 = sha256(step_4_1).hexdigest()
    step_4_3 = unhexlify(step_4_2)
    step_4 = sha256(step_4_3).hexdigest()
    # Step 5 (Checksum), first 8 characters
    step_5 = step_4[0:8]
    # Step 6 (Step 5 + Step 3)
    step_6 = step_3 + step_5
    # Base58-encode to receive final SIN
    sin = base58.encode(unhexlify(step_6))

    return sin


# CONSTS


BASE_URL = 'http://127.0.0.1:5000/'
USERS_URL = BASE_URL + 'users/'
JOBS_URL = BASE_URL + 'jobs/'

TX_FEE = 0.002


# USERS


test_user_1_mnemonic = 'robot excuse run dwarf depth candy emerge puzzle gospel churn kick tool'
test_user_1 = {
    'contact': {
        'login': 'rein-test-user',
        'email': 'test1@reinproject.org'
    },
    'bitcoin': {
        'master_address': '18mSWcpYB9X9nobaxc4kCHZXPNZaVVLYbR',
        'delegate': {
            'address': '17sxtd9FBmLcoRQATFwKz3uwuch8M5hHWy',
            'pubkey': '03ffd318e367ae0a8ea1eff6f6b9e324414fb51794c578f8c8ab1e217d4d6b0a0e',
            'privkey': 'L2TBvNdZ2q79qW4knjveCtSk2ZLsooR5pFc712hvXwrT4Ffm6E2N'
        }
    },
    'mediator': {
        'status': False,
        'fee': 0.0,
        'key': None
    },
    'validity': {
        'sin': generate_sin('18mSWcpYB9X9nobaxc4kCHZXPNZaVVLYbR')
    }
}
test_user_1['validity']['id'] = hashlib.sha256(json.dumps(test_user_1).encode('utf-8')).hexdigest()
test_user_1['validity']['signature'] = SignMessage(test_user_1['bitcoin']['delegate']['privkey'], test_user_1).decode('ascii')
test_user_1['validity']['signature_address'] = test_user_1['bitcoin']['delegate']['address']

test_user_2_mnemonic = 'hen skate guitar tube kick clutch decline silent way length stereo neglect'
test_user_2 = {
    'contact': {
        'login': 'rein-test-user2',
        'email': 'test2@reinproject.org'
    },
    'bitcoin': {
        'master_address': '1MGbFjsPAJTZAhf136shUrXinHJZJo1DKT',
        'delegate': {
            'address': '1HTWQLfE9mYPy1Knf7wgbWZLEJ9SDoNMX1',
            'pubkey': '027761c803512c83941f2c3ea43319b1d3806ad2f64156afd2fc3c63322d298396',
            'privkey': 'L3cckpG5S4fk54UMUBNW2SG3LynjFHBRdRj66AyCdFdupTTkDhTb'
        }
    },
    'mediator': {
        'status': False,
        'fee': 0.0,
        'key': None
    },
    'validity': {
        'sin': generate_sin('1MGbFjsPAJTZAhf136shUrXinHJZJo1DKT')
    }
}
test_user_2['validity']['id'] = hashlib.sha256(json.dumps(test_user_2).encode('utf-8')).hexdigest()
test_user_2['validity']['signature'] = SignMessage(test_user_2['bitcoin']['delegate']['privkey'], test_user_2).decode('ascii')
test_user_2['validity']['signature_address'] = test_user_2['bitcoin']['delegate']['address']

test_user_3_mnemonic = 'quarter toward soldier vessel typical top upper giant cotton target ritual group'
test_user_3 = {
    'contact': {
        'login': 'rein-test-user3',
        'email': 'test3@reinproject.org'
    },
    'bitcoin': {
        'master_address': '1LQP3sfbScgG3fqnkMhELe5Zvpvay8bnMg',
        'delegate': {
            'address': '12mgLVMrYqUvnTwgi6e3NizWhL6x4bnPsZ',
            'pubkey': '039a5be13776d6ba394571e7e19845b771f1d542ecca20200d4cf034166659cf0e',
            'privkey': 'L4RE61ru142PpTBkCjr4KK94Y7NtvqnBmJ5Fo2i68e2w79oaBqSY'
        }
    },
    'mediator': {
        'status': True,
        'fee': 1.0,
    },
    'validity': {
        'sin': generate_sin('1MGbFjsPAJTZAhf136shUrXinHJZJo1DKT')
    }
}
test_user_3['validity']['id'] = hashlib.sha256(json.dumps(test_user_3).encode('utf-8')).hexdigest()
test_user_3['validity']['signature'] = SignMessage(test_user_1['bitcoin']['delegate']['privkey'], test_user_3).decode('ascii')
test_user_3['validity']['signature_address'] = test_user_1['bitcoin']['delegate']['address']




# JOB


job = {
    'name': 'Test how the new Causeway works',
    'description': 'Write tests for http://github.com/ReinProject/causeway',
    'tags': ['tests', 'rein'],
    'time': {
        'block_hash': '000000000000000001a8dcc0d6f373fec948f9c07820927705f8c01123e59e15',
        'created_at': time.time(),
        'expires_at': time.time() + 100000,
    },
    'creator': {
        'login': test_user_1['contact']['login'],
        'contact': test_user_1['contact']['email'],
        'url': USERS_URL + test_user_1['contact']['login']
    },
    'mediator': {
        'login': test_user_3['contact']['login'],
        'contact': test_user_3['contact']['login'],
        'url': USERS_URL + test_user_3['contact']['login'],
        'fee': test_user_3['mediator']['fee']
    }
}

btc_job = BitcoinMessage(json.dumps(job))
job['validity'] = {}
job['validity']['signature'] = SignMessage(test_user_1['bitcoin']['delegate']['privkey'], btc_job).decode('ascii')
job['validity']['signature_address'] = test_user_1['bitcoin']['delegate']['address']
job['job']['id'] = hashlib.sha256(json.dumps(job).encode('utf-8')).hexdigest()

job_rq = {'key': 'remote-key',
          'value': json.dumps(job),
          'nonce': json.loads(requests.get('http://127.0.0.1:5000/nonce').content)['nonce'],
          'owner': test_user_1['bitcoin']['master_address'],
          'testnet': 'false'}

btc_job_rq = BitcoinMessage(json.dumps(job_rq))
job_rq['signature'] = SignMessage(test_user_1['bitcoin']['delegate']['privkey'], btc_job_rq).decode('ascii')
job_rq['signature_address'] = test_user_1['bitcoin']['delegate']['address']

job_res = requests.post(JOBS_URL + 'add', data = job_rq)
print(job_res.content)


# BID


bid = {
    'job': {
        'id': job['job']['id'],
        'url': JOBS_URL + job['job']['id']
    },
    'time': {
        'created_at': time.time()
    },
    'worker': {
        'login': test_user_2['contact']['login'],
        'contact': test_user_2['contact']['email'],
        'amount': 0.2,
        'url': USERS_URL + test_user_2['contact']['login']
    },
}

btc_bid = BitcoinMessage(json.dumps(bid))
bid['validity'] = {}
bid['validity']['signature'] = SignMessage(test_user_2['bitcoin']['delegate']['privkey'], btc_bid).decode('ascii')
bid['validity']['signature_address'] = test_user_2['bitcoin']['delegate']['address']

bid_rq = {'key': 'remote-key',
          'value': json.dumps(bid),
          'nonce': json.loads(requests.get('http://127.0.0.1:5000/nonce').content)['nonce'],
          'owner': test_user_2['bitcoin']['master_address'],
          'testnet': 'false'}

btc_bid_rq = BitcoinMessage(json.dumps(bid_rq))
bid_rq['signature'] = SignMessage(test_user_2['bitcoin']['delegate']['privkey'], btc_bid_rq).decode('ascii')
bid_rq['signature_address'] = test_user_2['bitcoin']['delegate']['address']

bid_res = requests.post(JOBS_URL + job['job']['id'] + '/bids/add', data = bid_rq)
print(bid_res.content)


# OFFER


offer = {
    'job': {
        'id': job['job']['id'],
        'url': JOBS_URL + job['job']['id']
    },
    'time': {
        'created_at': time.time()
    },
    'worker': {
        'login': test_user_2['contact']['login'],
        'escrow_address': '32vbvkxJT9Fp2RxieBpyUqmiTfN8eDXUvM',
        'escrow_pubkey': test_user_2['bitcoin']['delegate']['address'],
        'redeem_script': '522103ffd318e367ae0a8ea1eff6f6b9e324414fb51794c578f8c8ab1e217d4d6b0a0e21027761c803512c83941f2c3ea43319b1d3806ad2f64156afd2fc3c63322d29839621039a5be13776d6ba394571e7e19845b771f1d542ecca20200d4cf034166659cf0e53ae',
        'tx_fee': TX_FEE,
        'url': USERS_URL + test_user_2['contact']['login']
    },
    'creator': {
        'escrow_pubkey': test_user_1['bitcoin']['delegate']['address']
    },
    'mediator': {
        'escrow_address': '35ndpYmqoFXFCL3uvXBaD14mJvT5dS18Bn',
        'redeem_script': '522103ffd318e367ae0a8ea1eff6f6b9e324414fb51794c578f8c8ab1e217d4d6b0a0e21027761c803512c83941f2c3ea43319b1d3806ad2f64156afd2fc3c63322d29839652ae',
        'fee': test_user_3['mediator']['fee'] * bid['worker']['amount'],
        'tx_fee': TX_FEE
    }
}

btc_offer = BitcoinMessage(json.dumps(offer))
offer['validity'] = {}
offer['validity']['signature'] = SignMessage(test_user_1['bitcoin']['delegate']['privkey'], btc_offer).decode('ascii')
offer['validity']['signature_address'] = test_user_1['bitcoin']['delegate']['address']

offer_rq = {'key': 'remote-key',
            'value': json.dumps(offer),
            'nonce': json.loads(requests.get('http://127.0.0.1:5000/nonce').content)['nonce'],
            'owner': test_user_1['bitcoin']['master_address'],
            'testnet': 'false'}

btc_offer_rq = BitcoinMessage(json.dumps(bid_rq))
offer_rq['signature'] = SignMessage(test_user_1['bitcoin']['delegate']['address'], btc_offer_rq).decode('ascii')
offer_rq['signature_address'] = test_user_1['bitcoin']['delegate']['address']

offer_res = requests.post(JOBS_URL + job['job']['id'] + '/creator/accept-bid', data = offer_rq)
print(offer_res.content)


# DELIVERY


delivery = {
    'job': {
        'id': job['job']['id'],
        'url': JOBS_URL + job['job']['id']
    },
    'time': {
        'created_at': time.time()
    },
    'deliverables': {
        'description': 'A sample delivery.',
        'url': 'https://example.com'
    },
}

btc_delivery = BitcoinMessage(json.dumps(delivery))
delivery['validity'] = {}
delivery['validity']['signature'] = SignMessage(test_user_1['bitcoin']['delegate']['privkey'], btc_delivery).decode('ascii')
delivery['validity']['signature_address'] = test_user_1['bitcoin']['delegate']['address']

delivery_rq = {'key': 'remote-key',
            'value': json.dumps(delivery),
            'nonce': json.loads(requests.get('http://127.0.0.1:5000/nonce').content)['nonce'],
            'owner': test_user_2['bitcoin']['master_address'],
            'testnet': 'false'}

btc_delivery_rq = BitcoinMessage(json.dumps(delivery_rq))
delivery['signature'] = SignMessage(test_user_2['bitcoin']['delegate']['address'], btc_delivery_rq).decode('ascii')
delivery['signature_address'] = test_user_2['bitcoin']['delegate']['address']

delivery_res = requests.post(JOBS_URL + job['job']['id'] + '/deliver', data = delivery_rq)
print(delivery_res.content)


# DISPUTE


dispute = {
    'job': {
        'id': job['job']['id'],
        'url': JOBS_URL + job['job']['id']
    },
    'details': {
        'type': 'creator',
        'description': 'A sample dispute.'
    },
}

btc_dispute = BitcoinMessage(json.dumps(dispute))
dispute['validity'] = {}
dispute['validity']['signature'] = SignMessage(test_user_1['bitcoin']['delegate']['privkey'], btc_dispute).decode('ascii')
dispute['validity']['signature_address'] = test_user_1['bitcoin']['delegate']['address']

dispute_rq = {'key': 'remote-key',
            'value': json.dumps(dispute),
            'nonce': json.loads(requests.get('http://127.0.0.1:5000/nonce').content)['nonce'],
            'owner': test_user_1['bitcoin']['master_address'],
            'testnet': 'false'}

btc_dispute_rq = BitcoinMessage(json.dumps(dispute_rq))
dispute['signature'] = SignMessage(test_user_1['bitcoin']['delegate']['address'], btc_dispute_rq).decode('ascii')
dispute['signature_address'] = test_user_1['bitcoin']['delegate']['address']

dispute_res = requests.post(JOBS_URL + job['job']['id'] + '/deliver', data = dispute_rq)
print(dispute_res.content)


# DISPUTE RESOLUTION



