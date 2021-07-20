from flask import Flask, render_template, url_for, flash, redirect, Response
import cv2
import time
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'


##Everything needed for authentication#######
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/home")
def home():
    return render_template('home.html')

##Everything needed for live stream##########

camera= cv2.VideoCapture(0)#for live streaming from my camera

def generate_frames():
    while True:
            
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        #success is a boolean variable which tells us whether we're able to read the camera or not
        

@app.route("/livefeed")
def livefeed():
    return render_template('livefeed.html', title='Live Feed')

@app.route('/camvideo')
def camvideo():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

##Everything needed or Static Feed##########


def gen():
    """Video streaming generator function."""
    cap = cv2.VideoCapture('staticvideo.mp4')

    # Read until video is completed
    while(cap.isOpened()):
      # Capture frame-by-frame
        ret, img = cap.read()
        if ret == True:
            img = cv2.resize(img, (0,0), fx=0.5, fy=0.5) 
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
        else: 
            break

@app.route("/staticfeed")
def staticfeed():
    return render_template('staticfeed.html', title='Static Feed')

@app.route('/staticvideo')
def staticvideo():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)