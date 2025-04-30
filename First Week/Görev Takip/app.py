from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def anasayfa():
    return render_template("anasayfa.html")

@app.route("/giris")
def giris():
    return render_template("giris.html")

@app.route("/kayit")
def kayit():
    return render_template("kayit.html")

@app.route("/hakkımızda")
def hakkımızda():
    return render_template("hakkımızda.html")

@app.route("/iletisim")
def iletisim():
    return render_template("iletisim.html")

@app.route("/giris/panel")
def panel():
    return render_template("panel.html")

@app.route("/giris/panel/gorev_detay")
def gorev_detay():
    return render_template("gorev_detay.html")

@app.route("/giris/panel/gorev_liste")
def gorev_liste():
    return render_template("gorev_liste.html")

@app.route("/giris/panel/gorev_ekle")
def gorev_ekle():
    return render_template("gorev_ekle.html")

@app.route("/giris/panel/kullanıcılar")
def kullanıcılar():
    return render_template("kullanıcılar.html")

@app.route("/giris/panel/rapor")
def rapor():
    return render_template("rapor.html")


if __name__ == "__main__":
    app.run(debug=True)
