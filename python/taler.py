import requests
import threading

class MoneyPool:
	def __init__(self):
		self.lock = threading.Lock()
		self.amount = 0
		self.callbacks = []
	
	def update(self, diff):
		with self.lock:
			self.amount += diff
		for cb in self.callbacks:
			print("callback", cb)
			try:
				cb(self.amount)
			except Exception as e:
				print("CALLBACK FAILED, ", e)
	
	def get(self):
		with self.lock:
			return self.amount

class BankConfig:
	def __init__(self, base_url, username, token, currency):
		self.base_url = base_url
		self.username = username
		self.token = token
		self.currency = currency

cfg = BankConfig("https://bank.demo.taler.net", "windfisch", "36GWCV1MRCYT9YQZ87JP1ZZF5SR9KA6CCYW1Q0KE07D4Y646FK3G", "KUDOS")

class WithdrawalOperation:
	def __init__(self, bank_config, amount):
		self.bank_config = bank_config
		self.lock = threading.Lock()
		self.amount = amount

		headers = {
			'Accept': 'application/json',
			'Authorization': 'Bearer secret-token:' + bank_config.token,
			'Content-Type': 'application/json',
		}

		json_data = {
			'amount': '%s:%s' % (bank_config.currency, amount),
		}

		response = requests.post('%s/accounts/%s/withdrawals' % (bank_config.base_url, bank_config.username), headers=headers, json=json_data)

		if response.status_code != 200: raise RuntimeError("Fail")
		self.withdrawal_id = response.json()['withdrawal_id']
		self.withdraw_uri = response.json()['taler_withdraw_uri']

		self.cancelled = False
		self.confirmed = False

	def cancel(self):
		with self.lock:
			self.cancelled = True

			headers = {
				'Accept': 'application/json',
				'Authorization': 'Bearer secret-token:%s' % self.bank_config.token,
				'Content-Type': 'application/json',
			}

			response = requests.post(
				'%s/accounts/%s/withdrawals/%s/abort' % (self.bank_config.base_url, self.bank_config.username, self.withdrawal_id),
				headers=headers,
			)

			if response.status_code >= 200 and response.status_code <= 299:
				return True

		return False

	def wait_and_confirm(self):
		status = self._wait_until_changed_from('pending')

		if status is None or status["status"] == "aborted":
			return 0

		if status["status"] != 'selected': raise RuntimeError("Unknown withdrawal state transition: Expected pending->selected, got %s" % status["status"])

		headers = {
			'Accept': 'application/json',
			'Authorization': 'Bearer secret-token:%s' % self.bank_config.token,
			'Content-Type': 'application/json',
		}

		with self.lock:
			if not self.cancelled:
				response = requests.post(
					'%s/accounts/%s/withdrawals/%s/confirm' % (self.bank_config.base_url, self.bank_config.username, self.withdrawal_id),
					headers=headers,
				)

				if (response.status_code >= 200 and response.status_code <= 299):
					self.confirmed = True
					return self.amount

		return 0

	def _wait_until_changed_from(self, state):
		while not self.cancelled:
			headers = {
				'Accept': 'application/json',
			}

			params = {
				'long_poll_ms': '15000',
				'old_state': state,
			}

			response = requests.get(
				'%s/withdrawals/%s' % (self.bank_config.base_url, self.withdrawal_id),
				params=params,
				headers=headers,
			)

			r = response.json()

			print("wait got ")
			print(r)

			if r['status'] != state:
				return r

class TalerManager:
	def __init__(self, bank_config, callback):
		self.bank_config = bank_config
		self.op = None
		self.thread = None
		self.confirmed = 0
		self.callback = callback

	def _thread_func(self):
		print("thread starting")
		amount = self.op.wait_and_confirm()
		print("wait and confirm returned %s" % amount)
		if amount > 0:
			self.confirmed += amount
			print("thread exiting")
			self.callback(self.confirmed)
	
	def cancel(self):
		if self.op is None and self.thread is None:
			return

		if self.op.cancel() == True:
			pass
		else:
			raise RuntimeError("Failed to cancel old transaction")

		if self.thread is not None:
			print("joining thread")
			self.thread.join()
			print("done")
			self.thread = None

	def set_amount(self, amount):
		print("cancelling")
		self.cancel()

		print("creating op")
		self.op = WithdrawalOperation(self.bank_config, amount)
		print("starting thread")
		self.thread = threading.Thread(target=TalerManager._thread_func, args=(self,))
		self.thread.start()
		print("yo")

		return self.op.withdraw_uri

