from flask import Flask, render_template, request, redirect, url_for, jsonify
from accountlogin import accountLogin
from routefinder import RouteFinder

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account = accountLogin()
        if not account.login(username, password):
            error = 'Invalid login'
        else:
            return redirect(url_for('routefinder') + '?user=' + username)
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account = accountLogin()
        if not account.createUser(username, password):
            error = 'Error creating user'
        else:
            print("Account Created")
            return redirect(url_for('routefinder') + '?user=' + username)
    return render_template('register.html', error=error)


result = None
route_data = None  # structured route dictionary


@app.route('/routefinder', methods=['GET', 'POST'])
def routefinder():
    global result, route_data
    username = request.args.get('user')
    if request.method == 'POST':
        postcode = request.form['postcode']
        activity = request.form['activity']
        radius = int(request.form['radius'])
        username = request.form['username']
        routefinder = RouteFinder(activity, postcode, radius)
        result, route_data = routefinder.solve()  # string + dict
    return render_template('routefinder.html', result=result, username=username)


@app.route('/api/route', methods=['GET'])
def api_route():
    # Returns the last computed structured route data as JSON
    global route_data
    if route_data is None:
        return jsonify({"error": "No route calculated yet"}), 400
    return jsonify(route_data)


if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
