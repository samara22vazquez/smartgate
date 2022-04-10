from flask import Flask, flash, redirect, render_template, request, session, abort
import os
import config
import sqlite3 as sql
import hashlib
import time
import os
import shutil

app= Flask(__name__)
    
conn=sql.connect('webapp.db')
print ("Opened database successfully")
cur=conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (Username TEXT, Password TEXT)')
cur.execute('DROP TABLE IF EXISTS times')
cur.execute('CREATE TABLE IF NOT EXISTS times (Start TEXT, Stop TEXT, Mode TEXT)')
conn.close()

####################
global gate_id
gate_id = "cortana123"
####################
                           
@app.route('/register')
def register_temp():        
        return render_template('register.html')                           

@app.route("/done", methods=['GET', 'POST'])
def register_storage():
 if request.method == 'POST':
    try:
        Username = request.form['username']
        Password = request.form['password']
        Confirm  = request.form['confirm']
        ID_check = request.form['ID_check']
        global gate_id

        if ID_check.lower() == gate_id:
        
            if Confirm == Password:

                Secure_password= hashlib.md5(str(Password).encode())
                h= Secure_password.hexdigest()
                        
                with sql.connect('webapp.db') as con:
                   print ("Opened database successfully")   
                   cur = con.cursor()
                   x = cur.execute('SELECT username FROM users WHERE username=?', (Username, ) )
                   x = cur.fetchone()
                              
                   if x is not None:
                     msg = "Username already taken, please select another one." 
                     return render_template('registration.html', a = msg )
                               
                   else:
                      cur.execute("INSERT INTO users (Username, Password) VALUES  (?, ?) ", (Username, h ) )
               
                      print ("Opened database successfully")
                      con.commit()
                      msg = "Thanks for registering!"
                      session['logged_in']= True
                      session['username'] = Username

            else:
                 msg= "Passwords must match!"   
                 return render_template('registration.html', a = msg )

        else:
            msg = "Invalid Gate ID!"
            return render_template('registration.html', a = msg )
                 
    except Exception as e:
            con.rollback()
            print(e)
            msg="Registration failed!"
    finally:    
            return render_template("registration.html", a = msg)   
            con.close()         
                     
@app.route('/delete', methods = ['GET', 'POST'])
def delete_users():
  if not session.get('logged_in'):
        return render_template('login.html')
  else:
    
    Username = request.form['user']
    print (Username)
    con = sql.connect("webapp.db")
    con.row_factory = sql.Row
    try:
        if str(session['username']) == str(Username):
            cur = con.cursor()
            x =cur.execute("DELETE  FROM users WHERE username=?", (Username,))
            con.commit()
            session['logged_in']= False
           
        else:
            cur = con.cursor()
            x =cur.execute("DELETE  FROM users WHERE username=?", (Username,))
            con.commit()
            session['logged_in']= True
    
    except Exception as e:
        con.rollback()
        print (str(e))
        flash("wtf u doin")

    finally:
        return render_template('login.html')
        con.close()

@app.route('/user_display')
def user_display():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        con = sql.connect('webapp.db')
        con.row_factory = sql.Row

        cur = con.cursor()
        cur.execute('SELECT username FROM users')

        rows = cur.fetchall()

        return render_template('users.html', rows = rows)

    
@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        current_status = config.read_config('status')
        current_mode = config.read_config('mode')
        return render_template('menu.html', a = current_status.capitalize().replace(' ', '_'), b = current_mode.capitalize())

@app.route('/menu')
def home():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    current_status = config.read_config('status')
    current_mode = config.read_config('mode')
    return render_template('menu.html', a = current_status.capitalize().replace(' ', '_'), b = current_mode.capitalize())

@app.route('/login', methods=['POST'])
def do_admin_login():
 try:       
  if  request.method=='POST':  
   user=request.form['username']
   password=request.form['password']
   with sql.connect('webapp.db') as con:
       cur=con.cursor()
       Secure_password= hashlib.md5(str(password).encode())
       h= Secure_password.hexdigest()
         
       a = cur.execute('SELECT * FROM users WHERE username=?', (user,))
       a = cur.fetchone()[1]
       if  h==a:
         session['logged_in'] = True
         session['username'] = user

       else:
         flash('wrong password!')
 except:
         return "wrong username"
 finally:       
  return index()

@app.route("/logout")
def logout():
    session['logged_in']=False
    return index()

@app.route('/settings')
def time_settings():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        
        return render_template('set.html')

@app.route('/settings/delete')
def delete_time() :
    if not session.get('logged_in'):
        return render_template('login.html')
    else:    
        try:
            config.delete_preset_modes()
            with sql.connect('webapp.db') as con: 
                cur = con.cursor()
                cur.execute('DELETE FROM times')
                con.commit()
                a= "Time settings have been reset!"
        except Exception as e:
                print(e)
                con.rollback()
                a="Could not delete table!"
        finally:    
                return render_template('delete.html', msg=a)
    
@app.route('/timeset', methods=['GET', 'POST'])
def timeset():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    if request.method == 'POST':
        try:            
            start_time = request.form['start']
            stop_time  = request.form['stop']
            timed_mode = request.form['mode']

            with sql.connect("webapp.db") as con:

                cur = con.cursor()
                cur.execute("INSERT INTO times (Start,Stop, Mode) VALUES (?,?,?) ",(start_time, stop_time, timed_mode) )
                con.commit()
                done = "Time recorded"
                print (timed_mode, start_time, stop_time)

                strp_start_time = time.strptime(start_time, '%Y-%m-%dT%H:%M')
                strp_stop_time = time.strptime(stop_time, '%Y-%m-%dT%H:%M')
                print (strp_start_time, strp_stop_time)

                
                new_time_object = config.preset_mode(timed_mode, strp_start_time, strp_stop_time)
                config.write_preset_mode(new_time_object)
                print('Time data successfully written to config!')
                
        except Exception as e:
                con.rollback()
                print (str(e))
                done = "Could not record time!"
        finally:                
                return render_template("time_defined.html", msg = done)
                con.close()

@app.route('/configuration')
def configuration_display():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        con = sql.connect("webapp.db")
        con.row_factory = sql.Row
   
        cur = con.cursor()
        cur.execute("select * from times")
   
        rows = cur.fetchall();

        return render_template('configuration.html',rows = rows)

@app.route('/mode')
def mode():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    current_mode = config.read_config('mode')
    return render_template('mode.html', a = current_mode.capitalize())
        
@app.route('/mode/active')
def setmodeactive():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    config.write_config('mode','active')
    new_mode = config.read_config('mode')
    return render_template('modeset.html', a = new_mode.capitalize())

@app.route('/mode/secure')
def setmodesecure():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    config.write_config('mode','secure')
    new_mode = config.read_config('mode')
    return render_template('modeset.html', a = new_mode.capitalize())

@app.route('/mode/off')
def setmodeoff():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    config.write_config('mode','off')
    new_mode = config.read_config('mode')
    return render_template('modeset.html', a = new_mode.capitalize())

@app.route('/mode/aggro')
def setmodeaggro():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    config.write_config('mode','aggressive')
    new_mode = config.read_config('mode')
    return render_template('modeset.html', a = new_mode.capitalize())

@app.route('/status')
def status():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    current_status = config.read_config('status')
    return render_template('status.html', a = current_status)

@app.route('/angle')
def angle():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    current_angle_left = config.read_config('open_angle_left')
    current_angle_right = config.read_config('open_angle_right')
    return render_template('angle.html', a = current_angle_left, b = current_angle_right)

@app.route('/angle/set', methods=['POST','GET'])
def setangle():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    new_angle_left = request.form['left_angle']
    new_angle_right = request.form['right_angle']
    config.write_config('open_angle_left', int(new_angle_left))
    config.write_config('open_angle_right', int(new_angle_right))
    current_angle_left = config.read_config('open_angle_left')
    current_angle_right = config.read_config('open_angle_right')
    return render_template('setangle.html', a = current_angle_left, b = current_angle_right)

@app.route('/opentime')
def opentime():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    current_open_time = config.read_config('stay_open_time')
    return render_template('opentime.html', a = current_open_time)

@app.route('/opentime/set', methods=['POST','GET'])
def setopentime():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    new_open_time = request.form['open_time']
    config.write_config('stay_open_time', new_open_time)
    current_open_time = config.read_config('stay_open_time')
    return render_template('setopentime.html', a = current_open_time)

@app.route('/intruders/<int:image_ref>')
def intruders(image_ref):
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    if os.path.isfile("/home/pi/d4/d4cortana/src/static/1.jpg"):
        if image_ref > 1:
            c = image_ref - 1
        else:
            c = image_ref
    
        path_ref = "/home/pi/d4/d4cortana/src/static/" + str(image_ref + 1) + ".jpg"
        print (path_ref)
    
        if os.path.isfile(path_ref):
            b = image_ref + 1
        else:
            b = image_ref
    
        return render_template('intruders.html', a = image_ref, b = b, c = c)
    
    else:
        return render_template('registration.html', a = "No intruder images!")

@app.route('/intruderdelete')
def delete_intruders():
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    shutil.rmtree("/home/pi/d4/d4cortana/src/static/")
    os.makedirs("/home/pi/d4/d4cortana/src/static/")
    return render_template('registration.html', a = "All images deleted!")

#def webapp():
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=4000)

