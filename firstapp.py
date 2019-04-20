from flask import Flask,render_template,url_for,flash,redirect
from forms import RegistrationForm, LoginForm, RegisterAlbum,RegisterArtist,AddSongs
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
import cx_Oracle
from wtforms.validators import ValidationError

app = Flask(__name__)

app.config['SECRET_KEY'] = '2e3d9442882549964af284ca7d59f157'

engine = create_engine('oracle://dhairya:dhai7735@localhost/orcl')

bcrypt = Bcrypt(app)


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/admin", methods=['GET'])
def admin():
    posts = []
    songs = engine.execute("select * from Songs")
    for song in songs:
        albumid  = song[2]
        image = engine.execute("select Image from Album where AlbumID = :albumid",{'albumid':albumid})
        for row in image:
            songimage = row
        SongImage = songimage[0]
        post = {'SongName':song[1],'Image':SongImage,'SongUrl':song[5], 'SongId':song[0]}
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
        # def validate_email(self,email):
        #     email = email.data
        #     result = engine.execute('select * from UserInfo where email = :email',{'email':email})
        #     for row in result:
        #         raise ValidationError('That email is already taken. Please choose another email!')
        # if user:
        #     raise ValidationError('That email is already taken. Please choose another email!')
        engine.execute("insert into UserInfo(FirstName, LastName, email,password) values (:firstname,:lastname,:email,:hashed_pw)",{'firstname':form.firstname.data,'lastname':form.lastname.data,
                        'email':form.email.data,'hashed_pw':hashed_pw})
        # engine.commit()
        # engine.session.commit()
        flash(f'Account created for {form.firstname.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit() :
        password_entered = form.password.data
        email_entered = form.email.data
        password_reg = engine.execute("select password from UserInfo where email = :email_entered",{'email_entered':email_entered})
        for row in password_reg:
            reg = row
        if bcrypt.check_password_hash(reg[0] , form.password.data) :
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
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
        # return redirect(url_for('addsong'))
    else :
        flash('Not Registered', 'danger')
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
        # return redirect(url_for('addsong'))
    else :
        flash('Not Registered', 'danger')
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
        arid = engine.execute("select ArtistID from Artist where ArtistName = :artistname",{'artistname':artistname})
        for row in arid:
            artistid= row
        artistId = artistid[0]
        maxid = engine.execute("select max(SongID) from Songs")
        for row in maxid:
            Max = row
        songid = int(Max[0])
        songid = songid + 1
        engine.execute("insert into Songs(SongID,SongName,AlbumID,Language,Duration,SongURL) values(:songid,:songname,:albumId,:language,:duration,:songurl)",{'songid':songid,'songname':songname,
                                                            'albumId':albumId,'language':language,'duration':duration,'songurl':songurl})
        engine.execute("insert into Composition(SongID,ArtistID) values(:songid,:artistId)",{'songid':songid,'artistId':artistId})
        return redirect(url_for('admin'))
    return render_template('adminAddsong.html', title='admin', form=form)


@app.route("/delete/<songid>", methods=['POST', 'GET'])
def delete(songid):
    engine.execute("delete from Composition where SongID=:songid",{'songid':songid})
    engine.execute("delete from Songs where SongID=:songid",{'songid':songid})
    flash('Song Deleted')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)