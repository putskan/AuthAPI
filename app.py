from flask import Flask, render_template, url_for, request, redirect, Response
from datetime import datetime, timezone
import json
import math
import os

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
USERS_DATA_PATH = os.path.join(WORKING_DIR, "users.json")

app = Flask(__name__)

@app.route('/auth')
def auth():
	"""
	handle authentication api
	usage: curl "http://127.0.0.1:4096/auth?u=username&p=password"
	"""
	username = request.args.get('u')
	password = request.args.get('p')
	if not username or not password:
		return r"usage: /auth?u={username}&p={password}"

	filtered_users = [user_dict for user_dict in users_data if user_dict['u'].lower() == username.lower() and user_dict['p'] == password]
	if not filtered_users:
		error_msg = "Username or password are incorrect."
		return Response(json.dumps({"status": "failed", "error_msg": error_msg}), status=400)

	else:
		# compare user allowed time to current time
		begin_time_str, end_time_str = filtered_users[0]['begin_time'], filtered_users[0]['end_time']
		begin_time = datetime.strptime(begin_time_str, "%Y-%m-%d %H:%M:%S %z")
		end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S %z")
		now = datetime.now(timezone.utc)

		if now < begin_time:
			days_left = (begin_time - now).days
			hours_left = math.floor((begin_time - now).seconds / 60 / 60 % 24)
			mins_left = math.ceil((begin_time - now).seconds / 60 % 60)
			error_msg = 'oops! you are a bit early. please try again in {0} days, {1} hours and {2} minutes'.format(days_left, hours_left, mins_left)
			return Response(json.dumps({"status": "failed", "error_msg": error_msg}), status=400)

		elif now > end_time:
			error_msg = 'Session Expired.'
			return Response(json.dumps({"status": "failed", "error_msg": error_msg}), status=400)

		return {"status": "success", "user_type": filtered_users[0]['user_type']}


with open(USERS_DATA_PATH, 'rb') as f:
	users_data = json.loads(f.read())


if __name__ == '__main__':
	"""
	handle website
	"""
	app.run(host='0.0.0.0', port=4096, debug=True)

