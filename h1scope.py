import os, sys
import argparse
from apicalls import make_api_request, get_programs, get_scope, get_program_scope
from queue import Queue
from threading import Thread

VERSION = 1.1

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--username", default=os.environ.get('H1_USERNAME'), help="Hackerone Username")
	parser.add_argument("--apikey", default=os.environ.get('H1_APIKEY'), help="Generate APIKEY from https://hackerone.com/settings/api_token/edit")
	parser.add_argument("--handle", help="Handle for a specific program.")
	parser.add_argument("--wildcard", action="store_true", help="Get wildcard domains.")
	parser.add_argument("-cw", action="store_true", help="Clean wildcard domains to pipe to recon tools, *.hackerone.com => hackerone.com")
	parser.add_argument("--domains", action="store_true")
	parser.add_argument("--cidr", action="store_true")
	parser.add_argument("--android", action="store_true")
	parser.add_argument("--ios", action="store_true")
	parser.add_argument("--code", action="store_true")
	parser.add_argument("--other", action="store_true")
	parser.add_argument("--apk", action="store_true")
	parser.add_argument("--ipa", action="store_true")
	parser.add_argument("--hardware", action="store_true")
	parser.add_argument("--windows", action="store_true")
	parser.add_argument("--all", action="store_true", help="Get all asset types.")
	parser.add_argument("--private", action="store_true", help="Get only private programs.")
	parser.add_argument("--public", action="store_true", help="Get only public programs.") # Doesn't hurt to add it, what do i lose.
	parser.add_argument("--vdp", action="store_true", help="Get all VDP programs only.")
	parser.add_argument("--paid", action="store_true", help="Get only programs that pay a bounty. Remember to choose")
	# parser.add_argument("-o","--output")
	# parser.add_argument("-of","--output_format", default='text')
	p_args = parser.parse_args()

	if not p_args.username and not p_args.apikey:
		print("Missing USERNAME or APIKEY.", file=sys.stderr)
		sys.exit(parser.print_usage())

	if not p_args.wildcard or p_args.domains or p_args.cidr or p_args.android or p_args.ios or p_args.code or p_args.other:
		print("No specified scope, getting all in scope items.", file=sys.stderr)
		p_args.all = True

	if p_args.paid and p_args.vdp:
		print("Seriously, choose either PAID or VDP programs, or don't specify either to get them all. Smart *ss.", file=sys.stderr)
		sys.exit(parser.print_usage())

	if p_args.private and p_args.public:
		print("Seriously? Choose either PRIVATE or PUBLIC programs, or don't specify either to get them all. Smart *ss.", file=sys.stderr)
		sys.exit(parser.print_usage())
	
	if p_args.handle:
	
		get_program_scope(p_args)

	else:
	
		programs_queue = Queue()
		programs_thread = Thread(target=get_programs, args=(programs_queue, p_args), daemon=True).start()

		get_scope(programs_queue, p_args)

		# Do i call this on the thread or Queue?
		programs_queue.join()

if __name__ == '__main__':
	
	main()