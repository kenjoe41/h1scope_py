import requests
import os, re

def make_api_request(link, H1_USERNAME, H1_APIKEY):
	try:
		headers = {
		  'Accept': 'application/json'
		}

		r = requests.get(
		  link,
		  auth=(H1_USERNAME, H1_APIKEY),
		  headers = headers
		)
		return r
	except:
		return ''

# TODO: Have a thread getting Programs while another thread gets the scopes. Might be Golang talking to me.
# TODO: Look into python concurrent lib.
# TODO: Add connection retry logic, maybe nested while loop, break out on max retry or on successful connections.
# Let's hope these queues work just fine and ain't overhead and s**t
def get_programs(programs_queue, p_args):

	try:

		link = 'https://api.hackerone.com/v1/hackers/programs'

		while True:

			r = make_api_request(link, p_args.username, p_args.apikey)
			if not r:
				# We hit an Exception during the request, maybe track them, exit and log errors on too many of them.
				continue

			if r.ok:
				rdata = r.json()

				for program in rdata['data']:
					# If clause spaghetti coming up, i am gonna screw something up definitely. Maybe consider different Queues instead.

					# Parse, VDP when we want bounty.
					if p_args.paid and not program['attributes'].get('offers_bounties'):
						continue
					# For some God Almighty reason, someone wants only VDP.
					elif p_args.vdp and program['attributes'].get('offers_bounties'):
						continue
					
					# Parse out Private or Public programs.
					program_mode = program['attributes'].get('state')
					if p_args.private and program_mode == 'public_mode':
						continue
					elif p_args.public and program_mode != 'public_mode':
						continue

					# We should be all done at this level, what did i miss?
					programs_queue.put(program)

				
				link = rdata['links'].get('next')
				if not link:
					# Last page, exit While loop.
					break
			else:
				# Add logic to handle atleast the rate limit, something to consider if concurrent threading comes in play maybe.
				continue 

		return
	except KeyboardInterrupt:
		os._exit()
def cleandomain(dmn):
	# Can't guarantee some domains won't be screwed up, like these clip*sub.domain.com or domain.*

	pattern = r"[\w]+[\w\-_~\.]+\.[a-zA-Z]+|$"
	domain = re.findall(pattern, dmn)[0]

	# Some wildcard domains somehow start with 'www.', let's remove to better bruteforce.
	if domain and domain.startswith('www.'):
		domain = domain.replace('www.', '')
		
	return domain

def get_program_scope(p_args):
			link = f'https://api.hackerone.com/v1/hackers/programs/{p_args.handle}'
			r = make_api_request(link, p_args.username, p_args.apikey)
			if not r:
				return
			
			if r.ok:
				rdata = r.json()
				scope = rdata['relationships']['structured_scopes']['data']
				for asset in scope:
					# Not wasting lines of code to give you Outof Scope items, go copy them yourself, even VDPs have OS items.
					if not asset['attributes']['eligible_for_submission']:
						continue

					identifier = asset['attributes']['asset_identifier']

					# Time for another IF clause spaghetti.
					if asset['attributes']['asset_type'] == 'URL':

						if (p_args.wildcard or p_args.all) and identifier.startswith('*'): # domains.contains() might flag domain.com/* which ain't wildcard domains.
							# TODO: Consider domains that end in wildcard, hackerone.*
							if p_args.cw:
								print(cleandomain(identifier).strip())
							else:
								print(identifier)
							continue
						elif p_args.domains or p_args.all and not identifier.startswith('*'):
							print(identifier)

					elif p_args.cidr or p_args.all and asset['attributes']['asset_type'] == 'CIDR':
							print(identifier)

					elif p_args.code or p_args.all and asset['attributes']['asset_type'] == 'SOURCE_CODE':
							print(identifier)

					elif p_args.android or p_args.all and asset['attributes']['asset_type'] == 'GOOGLE_PLAY_APP_ID':
							print(identifier)

					elif p_args.apk or p_args.all and asset['attributes']['asset_type'] == 'OTHER_APK':
							print(identifier)

					elif p_args.ios or p_args.all and asset['attributes']['asset_type'] == 'APPLE_STORE_APP_ID':
							print(identifier)

					elif p_args.ipa or p_args.all and asset['attributes']['asset_type'] == 'OTHER_IPA':
							print(identifier)

					elif p_args.other or p_args.all and asset['attributes']['asset_type'] == 'OTHER':
							print(identifier)

					elif p_args.hardware or p_args.all and asset['attributes']['asset_type'] == 'HARDWARE':
							print(identifier)

					elif p_args.windows or p_args.all and asset['attributes']['asset_type'] == 'WINDOWS_APP_STORE_APP_ID':
							print(identifier)
							
			else:
				# Aaah, something went wrong, either connection issues or Rate limit. Let's worry later about this.
				pass


# Am i using Queues right? couldn't popping items off a list have worked just find? But thats a Queue in the end anyways.
def get_scope(programs_queue, p_args):
	try:
		# Infinity here we come, i swear this is for the Queue. Someone teach me about queues and a better way.
		while True:
		
			program = programs_queue.get()

			handle = program['attributes'].get('handle')
			get_program_scope(handle)

			programs_queue.task_done()	
	except KeyboardInterrupt:
		# thread.interrupt_main()
		# Whatever, probably still doesn't work. But since it will be in a script mostly, little use for this. Just Ctrl + Z abd ugly kill it.
		os._exit()