from flask import Flask,render_template,url_for,flash,redirect
from forms import RegistrationForm, LoginForm, RegisterAlbum,RegisterArtist,AddSongs,UpdateForm
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
import cx_Oracle
from wtforms.validators import ValidationError

app = Flask(__name__)

app.config['SECRET_KEY'] = '2e3d9442882549964af284ca7d59f157'

engine = create_engine('oracle://dhairya:dhai7735@localhost/orcl')

bcrypt = Bcrypt(app)

email_entered = "Email"

@app.route("/")
def home():
    email_entered = "Email"
    print(email_entered)
    return render_template('home.html')

@app.route("/userhome")
def userhome():
    if email_entered == 'Email':
        return redirect(url_for('home'))
    posts = []
    albumpost = []
    artistpost = []
    songs = engine.execute("select * from Songs")
    for song in songs:
        songID = song[0]
        albumid  = song[2]
        image = engine.execute("select Image from Album where AlbumID = :albumid",{'albumid':albumid})
        for row in image:
            songimage = row
        SongImage = songimage[0]
        post = {'SongID':songID, 'SongName':song[1],'Image':SongImage,'SongUrl':song[5],'Duration':song[4],'Language':song[3]}
        posts.append(post)

    albums = engine.execute("select * from Album")
    for album in albums:
        albumID = album[0]
        x = engine.execute("select count(*) from Songs where AlbumID = :albumID",{'albumID':albumID})
        for row in x:
            noOfSongs = row[0]
        post = {'AlbumName':album[1], 'Image':album[2], 'NumSongs': noOfSongs, 'AlbumID': album[0],'Year':album[3]}
        albumpost.append(post)

    artists = engine.execute("select * from Artist")
    for artist in artists:
        artistID = artist[0]
        x = engine.execute("select count(*) from Composition where ArtistID = :artistID",{'artistID':artistID})
        for row in x:
            noOfSongs= row[0]
        post = {'ArtistID':artist[0], 'ArtistName':artist[1], 'Image':artist[3], 'NumofSongs': noOfSongs,'Gender':artist[2]}
        artistpost.append(post)
    return render_template('userhome.html', posts=posts,albumpost=albumpost, artistpost=artistpost)

@app.route("/userhistory")
def userhistory():
    if email_entered == 'Email':
        return redirect(url_for('home'))
    SongsHistory=engine.execute("select * from Songs S join History H on S.SongID = H.SongID where H.Email = :email_entered order by H.DateAndTime desc",{'email_entered':email_entered})
    historyposts = []
    for song in SongsHistory:
        songName = song[1]
        albumid = song[2]
        image = engine.execute("select Image from Album where AlbumID = :albumid",{'albumid':albumid})
        for row in image:
            songimage = row
        SongImage = songimage[0]
        dateandtime = song[8]
        post = {'SongName':songName, 'SongImage':SongImage, 'DateAndTime':dateandtime,'Duration':song[4],'Language':song[3],'SongUrl':song[5]}
        historyposts.append(post)
    return render_template('userhistory.html',historyposts=historyposts)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/admin", methods=['GET'])
def admin():
    print(email_entered)
    posts = []
    songs = engine.execute("select * from Songs")
    for song in songs:
        albumid  = song[2]
        image = engine.execute("select Image from Album where AlbumID = :albumid",{'albumid':albumid})
        for row in image:
            songimage = row
        SongImage = songimage[0]
        post = {'SongName':song[1],'Image':SongImage,'SongUrl':song[5], 'SongId':song[0],'Duration':song[4],'Language':song[3]}
        posts.append(post)

    return render_template('adminDisplaySong.html',posts=posts)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        password = form.password.data
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        count = engine.execute("select count(*) from UserInfo where email = :email",{'email':email})
        for cnt in count:
            noofemails = cnt[0]
        if noofemails == 1:
            flash('This email is already taken! Please choose another one.','danger')
            # return redirect(url_for('register'))
        else:
            engine.execute("insert into UserInfo(FirstName, LastName, email,password) values (:firstname,:lastname,:email,:hashed_pw)",{'firstname':form.firstname.data,'lastname':form.lastname.data,
                            'email':form.email.data,'hashed_pw':hashed_pw})
            flash(f'Account created for {form.firstname.data}!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    global email_entered
    form = LoginForm()
    if form.validate_on_submit() :
        password_entered = form.password.data
        email_entered = form.email.data
        print(email_entered)
        count = engine.execute("select count(*) from UserInfo where email = :email_entered",{'email_entered':email_entered})
        for cnt in count:
            noofemails = cnt
        print(noofemails[0])
        password_reg = engine.execute("select password from UserInfo where email = :email_entered",{'email_entered':email_entered})
        username = engine.execute("select FirstName from UserInfo where email = :email_entered",{'email_entered':email_entered})
        for row in password_reg:
            reg = row
        for row in username:
            user = row[0]
        # print(user)
        if noofemails[0] == 1:
            if bcrypt.check_password_hash(reg[0] , form.password.data) :
                flash('You have been logged in!', 'success')
                if email_entered == 'iit2017080@iiita.ac.in':
                    return redirect(url_for('admin'))
                else:
                    return redirect(url_for('userhome', user=user))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        else:
            flash('Incorrect email or password', 'danger')
    return render_template('login.html', title='Login', form=form)


# @app.route("/login", methods=['GET', 'POST'])
# def addSong():
#     form = AddSong()
#     if form.validate_on_submit() :


@app.route("/registeralbum", methods=['GET', 'POST'])
def registeralbum():
    form = RegisterAlbum()
    if form.validate_on_submit() :
        albumname = form.AlbumName.data
        yearofrelease = form.YearOfRelease.data
        imageurl = form.Image.data
        maxid = engine.execute("select max(AlbumID) from Album")
        for row in maxid:
            Max = row
        albumid = int(Max[0])
        albumid = albumid + 1
        engine.execute("insert into Album(AlbumID, AlbumName, Image, YearofRelease) values (:albumid,:albumname,:imageurl,:yearofrelease)",{'albumid':albumid,'albumname':albumname,
                         'imageurl':imageurl,'yearofrelease':yearofrelease})
        flash('Registered Successfully!', 'success')
        return redirect(url_for('addsong'))
    return render_template('registerAlbum.html', title='Register', form=form)


@app.route("/registerartist", methods=['GET', 'POST'])
def registerartist():
    form = RegisterArtist()
    if form.validate_on_submit() :
        artistname = form.ArtistName.data
        gender = form.Gender.data
        imageurl = form.Image.data
        maxid = engine.execute("select max(ArtistID) from Artist")
        for row in maxid:
            Max = row
        artistid = int(Max[0])
        artistid = artistid + 1
        engine.execute("insert into Artist(ArtistID, ArtistName,Gender, Image) values (:artistid,:artistname,:gender,:imageurl)",{'artistid':artistid,'artistname':artistname,
                         'imageurl':imageurl,'gender':gender})
        flash('Registered Successfully!', 'success')
        return redirect(url_for('addsong'))

    return render_template('registerArtist.html', title='Register', form=form)



@app.route("/addsong", methods=['GET', 'POST'])
def addsong():
    form = AddSongs()
    album_options = []
    albumnames = engine.execute("select AlbumName from Album")
    for row in albumnames:
        alb = row
        album_options.append(tuple((alb[0],alb[0])))
    form.AlbumName.choices = album_options
    artist_options = []
    artistnames = engine.execute("select ArtistName from Artist")
    for row1 in artistnames:
        alb1= row1
        artist_options.append(tuple((alb1[0],alb1[0])))
    form.ArtistName.choices = artist_options
    if form.validate_on_submit() :
        songname = form.SongName.data
        language = form.Language.data
        duration = form.Duration.data
        albumname = form.AlbumName.data
        artistname = form.ArtistName.data
        print(artistname)
        songurl = form.SongURL.data
        # albumimage = engine.execute("select Image from Album where AlbumName = :albumname",{'albumname':albumname})
        # for row in albumimage:
        #     image = row
        # postSong = {'SongName':songname,'Image':image[0],'SongUrl':songurl}
        # posts.append(postSong)
        aid = engine.execute("select AlbumID from Album where AlbumName = :albumname",{'albumname':albumname})
        for row in aid:
            albumid= row
        albumId = albumid[0]
        # arid = engine.execute("select ArtistID from Artist where ArtistName = :artistname",{'artistname':artistname})
        # for row in arid:
        #     artistid= row
        # artistId = artistid[0]
        maxid = engine.execute("select max(SongID) from Songs")
        for row in maxid:
            Max = row[0]
        songid = Max + 1
        engine.execute("insert into Songs(SongID,SongName,AlbumID,Language,Duration,SongURL,Frequency) values(:songid,:songname,:albumId,:language,:duration,:songurl,0)",{'songid':songid,'songname':songname,
                                                            'albumId':albumId,'language':language,'duration':duration,'songurl':songurl})
        for i in artistname:
            arid = engine.execute("select ArtistID from Artist where ArtistName= :artistname",{'artistname':i})
            for row in arid:
                artistId = row[0]
            engine.execute("insert into Composition(SongID,ArtistID) values(:songid,:artistId)",{'songid':songid,'artistId':artistId})
        return redirect(url_for('admin'))
    return render_template('adminAddsong.html', title='admin', form=form)

@app.route("/insert/<songid>", methods=['POST', 'GET'])
def insert(songid):
    x = engine.execute("select count(*) from History where SongID = :songid and Email = :email_entered",{'songid':songid, 'email_entered':email_entered})
    for row in x:
        noOfSongs = row[0]
    if noOfSongs == 0:
        engine.execute("insert into History(Email,SongID,DateAndTime) values(:email_entered,:songid,TO_CHAR(sysdate, 'yyyy/mm/dd hh24:mi:ss'))",{'email_entered':email_entered,'songid':songid})
        engine.execute("update Songs set Frequency = (select Frequency from Songs where SongID = :songid) + 1 where SongID = :songid",{'songid':songid})
    else:
        engine.execute("update History set DateAndTime = TO_CHAR(sysdate, 'yyyy/mm/dd hh24:mi:ss') where SongID = :songid",{'songid':songid})
    return ''

@app.route("/songInfo/<albumid>", methods=['POST', 'GET'])
def songInfo(albumid):
    print(email_entered)
    if email_entered == 'Email':
        return redirect(url_for('home'))
    posts = []
    songs = engine.execute("select * from Songs where AlbumID = :albumid",{'albumid':albumid})
    for song in songs:
        songID = song[0]
        image = engine.execute("select Image from Album where AlbumID = :albumid",{'albumid':albumid})
        for row in image:
            songimage = row
        SongImage = songimage[0]
        post = {'SongID':songID, 'SongName':song[1],'Image':SongImage,'SongUrl':song[5]}
        posts.append(post)
    return render_template('songInfo.html',posts=posts)

@app.route("/songInfoOfArtist/<artistid>", methods=['POST', 'GET'])
def songInfoOfArtist(artistid):
    posts = []
    songs = engine.execute("select * from Songs where SongID in (select distinct SongID from Composition where ArtistID = :artistid)",{'artistid':artistid})
    for song in songs:
        songID = song[0]
        albumid = song[2]
        image = engine.execute("select Image from Album where AlbumID = :albumid",{'albumid':albumid})
        for row in image:
            songimage = row
        SongImage = songimage[0]
        post = {'SongID':songID, 'SongName':song[1],'Image':SongImage,'SongUrl':song[5],'Duration':song[4],'Language':song[3]}
        posts.append(post)
    return render_template('songInfo.html',posts=posts)

@app.route("/songInfo", methods=['POST', 'GET'])
def popularSongs():
    posts = []
    songs = engine.execute("select * from Songs order by Frequency desc")
    for song in songs:
        songID = song[0]
        albumid = song[2]
        image = engine.execute("select Image from Album where AlbumID = :albumid",{'albumid':albumid})
        for row in image:
            songimage = row
        SongImage = songimage[0]
        post = {'SongID':songID, 'SongName':song[1],'Image':SongImage,'SongUrl':song[5]}
        posts.append(post)
    return render_template('songInfo.html',posts=posts)

@app.route("/delete/<songid>", methods=['POST', 'GET'])
def delete(songid):
    engine.execute("delete from Composition where SongID=:songid",{'songid':songid})
    engine.execute("delete from Songs where SongID=:songid",{'songid':songid})
    flash('Song Deleted')
    return redirect(url_for('admin'))
    # return render_template('adminDisplaySong.html')

@app.route("/adminProfile", methods=['GET', 'POST'])
def adminProfile():
    if email_entered == 'Email':
        flash('Please Login First','danger')
        return redirect(url_for('admin'))
    firstname = engine.execute("select FirstName from UserInfo where email = :email_entered",{'email_entered':email_entered})
    for row in firstname:
        fn = row[0]
    lastname = engine.execute("select LastName from UserInfo where email = :email_entered",{'email_entered':email_entered})
    for row in lastname:
        ln = row[0]
    return render_template('adminProfile.html', email_entered=email_entered,fn=fn,ln=ln)

@app.route("/userList", methods=['GET', 'POST'])
def userList():
    users = engine.execute("select * from UserInfo")
    userlist = []
    i=1
    for row in users:
        userlist.append({'index':i,'FirstName':row[0],'LastName':row[1],'Email':row[2]})
        i = i+1
    return render_template('userList.html', title='users', userlist=userlist)


@app.route("/deleteUser/<id>", methods=['GET', 'POST'])
def deleteUser(id):
    engine.execute("delete from UserInfo where email= :id",{'id':id})
    print(id)
    flash('User Deleted')
    return redirect(url_for('userList'))


@app.route("/updateinfo", methods=['GET', 'POST'])
def updateinfo():
    first = engine.execute("select FirstName from UserInfo where email = :email_entered",{'email_entered':email_entered}) 
    last = engine.execute("select LastName from UserInfo where email = :email_entered",{'email_entered':email_entered})
    for row in first:
        firstname = row[0]
    for row in last:
        lastname = row[0]
    form = UpdateForm()
    # form.firstname.data = firstname
    # form.lastname.data = lastname
    if form.validate_on_submit() :
        fn = form.firstname.data
        ln = form.lastname.data
        password = form.newpassword.data
        oldpassword = form.oldpassword.data
        password_reg = engine.execute("select password from UserInfo where email = :email_entered",{'email_entered':email_entered})
        
        for row in password_reg:
            reg = row[0]

        if bcrypt.check_password_hash(reg, oldpassword) :
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            if fn != firstname:
                engine.execute("update UserInfo set FirstName=:fn where email=:email_entered",{'email_entered':email_entered,'fn':fn})
            if ln != lastname:
                engine.execute("update UserInfo set LastName=:ln where email=:email_entered",{'email_entered':email_entered,'ln':ln})
            engine.execute("update UserInfo set password=:hashed_pw where email=:email_entered",{'email_entered':email_entered,'hashed_pw':hashed_pw})
            return redirect(url_for('adminProfile'))
        else:
            flash('Old password not valid!','danger')
            return ''
    return render_template('adminupdateProfile.html', form=form)


@app.route("/userProfile", methods=['GET', 'POST'])
def userProfile():
    firstname = engine.execute("select FirstName from UserInfo where email = :email_entered",{'email_entered':email_entered})
    for row in firstname:
        fn = row[0]
    lastname = engine.execute("select LastName from UserInfo where email = :email_entered",{'email_entered':email_entered})
    for row in lastname:
        ln = row[0]
    return render_template('userProfile.html', email_entered=email_entered,fn=fn,ln=ln)


@app.route("/updateUser", methods=['GET', 'POST'])
def updateUser():
    first = engine.execute("select FirstName from UserInfo where email = :email_entered",{'email_entered':email_entered}) 
    last = engine.execute("select LastName from UserInfo where email = :email_entered",{'email_entered':email_entered})
    for row in first:
        firstname = row[0]
    for row in last:
        lastname = row[0]
    form = UpdateForm()
    # form.firstname.data = firstname
    # form.lastname.data = lastname
    if form.validate_on_submit() :
        fn = form.firstname.data
        print(fn)
        ln = form.lastname.data
        print(ln)
        password = form.newpassword.data
        oldpassword = form.oldpassword.data
        password_reg = engine.execute("select password from UserInfo where email = :email_entered",{'email_entered':email_entered})
        
        for row in password_reg:
            reg = row[0]

        if bcrypt.check_password_hash(reg, oldpassword) :
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            if fn != firstname:
                engine.execute("update UserInfo set FirstName=:fn where email=:email_entered",{'email_entered':email_entered,'fn':fn})
            if ln != lastname:
                engine.execute("update UserInfo set LastName=:ln where email=:email_entered",{'email_entered':email_entered,'ln':ln})
            engine.execute("update UserInfo set password=:hashed_pw where email=:email_entered",{'email_entered':email_entered,'hashed_pw':hashed_pw})
            return redirect(url_for('userProfile'))
        else:
            flash('Old password not valid!','danger')
            return redirect(url_for('updateUser'))
    return render_template('userUpdateProfile.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)