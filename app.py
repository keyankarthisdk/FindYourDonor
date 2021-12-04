from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import TextField
from datetime import date , datetime
import sqlite3


app = Flask(__name__)
app.secret_key = "don't tell"

@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('home.html')


@app.route('/admin_view')
def admin_view():
    con = sqlite3.connect('db.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from donor_details")
    users = cur.fetchall();
    return render_template('admin_view.html',users=users)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    state=-1
    #conn = sqlite3.connect('main.sqlite')
    if request.method == 'POST':
      conn = sqlite3.connect('db.db')
      cur = conn.cursor()
      result = request.form
      #print(result)
      gg=result.to_dict(flat=True)
      cur.execute('''INSERT into donor_details (name,age,address,c_n,whatsapp,telegram,email,pincode,username, password,bg) VALUES ( ?,?,?,?,?,?,?,?,?,?,?)''', (result['name'],result['age'],result['address'],result['c_n'],result['whatsapp'],result['telegram'],result['email'],result['pin'],result['username'],result['password'],result['bg'] ))
      conn.commit()
      conn.close()    
      return redirect(url_for('login'))

    return render_template('signup.html')
    # return "hi"


@app.route('/login',methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('/login.html')
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            a = 'yes'
            session['username'] = username
            #session['logged_in'] = True
            session['admin'] = True
            return redirect(url_for('admin_view'))
        #print((password,email))
        con = sqlite3.connect('db.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select username,password from donor_details where username=?",(username,))
        rows = cur.fetchall();
        for row in rows:
            print(row['username'],row['password'])
            a = row['username']
            session['username'] = a
            session['logged_in'] = True
            print(a)
            u = {'username': a}
            p = row['password']
            print(p)

            if username == a and password == p:
                return redirect(url_for('index'))
            else:
                flash("Incorrect Password")
                return render_template('/login.html')
        return render_template('/login.html')
    else:
        return render_template('/')

@app.route('/update_donation',methods=["POST","GET"])
def update_donation():
    #print("Hi donation")
    if request.method=='POST':
        l_d=request.form.get("l_date",False)
        #l_d=datetime.fromisoformat(l_d).date()
        print(l_d)
        con = sqlite3.connect('db.db')
        cur=con.cursor()
        #print("Inside donations")
        print("username: ",session.get('username'))
        cur.execute('''UPDATE donor_details SET last_date=? WHERE username=?''',(l_d,session.get('username')))
        con.commit()
        con.close()
        #flash("Updated successfully!")
        print("Updated successfully")
        return redirect(url_for('index'))
    if request.method=='GET':
        print("done donation")
        return render_template('update_donation.html')

@app.route('/index',methods=["POST","GET"])
def index():
    return render_template('index.html')


@app.route('/deleteuser/<email>',methods=('GET', 'POST'))
def deleteuser(email):
    if request.method == 'GET':
        conn = sqlite3.connect('db.db')
        cur = conn.cursor()
        cur.execute('delete from donor_details where email=?',(email,))
        flash('deleted user:'+email)
        conn.commit()
        conn.close()
        return redirect(url_for('admin_view'))


def _dis1(spin,dpin):
    spin=int(spin)
    print("Printing types",type(spin),type(dpin))
    #print(dpin)
    #dpin=int(dpin)

    if(spin>=dpin):
        return spin-dpin
    else:
        return dpin-spin



@app.route('/find',methods= ['POST', 'GET'])
def find():
    #<td> {{ _distance(spin,r["pincode"])}}</td>
    #result=request.form
    print("Session :",session.get('username'))
    if request.method=='POST':
        b_g = request.form.get('bg',False)#request.form.get("something", False)
        s_p=request.form.get('spin',False)#['spin']
        print(b_g,s_p)
        con = sqlite3.connect('db.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from donor_details ")
        rows=cur.fetchall()
        today=date.today()
        #print(type(rows))
        print("Updating Status")
        flash("Updating status")
        for i in range(len(rows)):
            if(rows[i]['last_date'] is not None):
                l_d=rows[i]['last_date']
                l_d=datetime.fromisoformat(l_d).date()
                months=(today-l_d).days/30
                #print(rows[i]['name'],months)
                if(months>18):#1 for Active , 4for Active but InValid(within 6 months), 2 for Semi active, 3 for Inactive
                    status=4
                elif(months<=18 and months > 9):
                    status=2
                elif(months<=9 and months>6):
                    status=1
                elif(months<=6):
                    print("inside 4")
                    status=3

            else:
                #print("yet to be updated for",rows[i]['name'])
                status="Yet to be updated"
            status=status
            print("Printing status ",rows[i]['name'],status)
            print(type(status))
            a=cur.execute(''' UPDATE donor_details SET status=? WHERE username=? ''',(status,rows[i]['name']))
            print("Execute status: ",a)
            con.commit()
            #print((today-rows[i]['last_date']).days)
            #print(rows[i]['last_date'])
        if(b_g=='any'):
            print("inside any")
            cur.execute(''' SELECT * from donor_details ''')
            search=cur.fetchall()
            cur.execute('''CREATE table if not exists temp_table as select * from donor_details ''')
            cur.execute('''ALTER table temp_table ADD di numeric''')
            for i in range(len(search)):
                dis=_dis1(s_p,search[i]['pincode'])
                print(s_p,search[i]['pincode'],dis,search[i]['name'])
                cur.execute(''' UPDATE temp_table set di=? where username=? ''',(dis,search[i]['name']))
            #rows = cur.fetchall()
            con.commit()
            cur.execute('''SELECT * from temp_table ORDER BY status , di ASC''')
        else:
            print("Also else")
            cur.execute(''' SELECT * from donor_details where bg=? ''',(b_g,))
            search = cur.fetchall();
            #cur.execute('''CREATE TABLE temp_table like donor_details ''')
            cur.execute('''CREATE table if not exists temp_table as select * from donor_details where bg=? ''',(b_g,))
            #cur.execute(''' INSERT INTO temp_table SELECT * FROM donor_details where bg=? ''',(b_g,))
            #cur.execute('''CREATE table temp_table as (select * from donor_details where bg=?) ''',(b_g,))
            #cur.execute('''ALTER TABLE temp_table drop column di''')
            cur.execute('''ALTER table temp_table ADD di numeric''')
            for i in range(len(search)):
                dis=_dis1(s_p,search[i]['pincode'])
                print(s_p,search[i]['pincode'],dis,search[i]['name'])
                cur.execute(''' UPDATE temp_table set di=? where username=? ''',(dis,search[i]['name']))
            #rows = cur.fetchall()
            con.commit()
            cur.execute('''SELECT * from temp_table where bg=? ORDER BY status , di ASC''',(b_g,))

        
        search1=cur.fetchall();
        cur.execute(''' DROP table temp_table''')
        con.commit()
        con.close()
        #print("Row is :",search)
        return render_template('find_result.html',search=search1,b_g=b_g, spin=s_p,i=0)
    if request.method=='GET':
        return render_template('find.html')





if __name__ == "__main__":
    app.run(debug=True,port=5001)