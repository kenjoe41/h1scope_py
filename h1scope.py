import re
import os
import argparse
from apicalls import make_api_request, get_programs, get_scope
from queue import Queue
from threading import Thread

# TODO: Consider scope for a single program.

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--username", default=os.environ.get('H1_USERNAME'), help="Hackerone Username")
	parser.add_argument("--apikey", default=os.environ.get('H1_APIKEY'), help="Generate APIKEY from https://hackerone.com/settings/api_token/edit")
	parser.add_argument("--wildcard", action="store_true", help="Get wildcard domains.")
	parser.add_argument("-cw", action="store_true", help="Clean wildcard domains to pipe to recon tools, *.hackeone.com => hackerone.com")
	parser.add_argument("--domains", action="store_true")
	parser.add_argument("--cidr", action="store_true")
	parser.add_argument("--android", action="store_true")
	parser.add_argument("--ios", action="store_true")
	parser.add_argument("--code", action="store_true")
	parser.add_argument("--other", action="store_true") # This covers the executables and others, might need refining if we need only the executables.
	parser.add_argument("--all", action="store_true", help="Get all asset types.")
	parser.add_argument("--private", action="store_true", help="Get only private programs.")
	parser.add_argument("--public", action="store_true", help="Get only public programs.") # Doesn't hurt to add it, what do i lose.
	parser.add_argument("--vdp", action="store_true", help="Get all VDP programs only.")
	parser.add_argument("--paid", action="store_true", help="Get only programs that pay a bounty.")
	# parser.add_argument("-o","--output")
	# parser.add_argument("-of","--output_format", default='text')
	p_args = vars(parser.parse_args())

	if not p_args.username and not p_args.apikey:
		os.exit(parser.print_usage())
	
	programs_queue = Queue()
	programs_thread = Thread(target=get_programs, args=(programs_queue, p_args), daemon=True).start()

	get_scope(programs_queue, p_args)

	# Do i call this on the thread or Queue?
	programs_queue.join()

if __name__ == '__main__':
	
	main()