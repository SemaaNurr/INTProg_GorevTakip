from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask import session
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from functools import wraps
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import json
import hashlib

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kullanicilar.db"
app.config["SECRET_KEY"] = "gizli_anahtar"
db = SQLAlchemy(app)

class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Gorev(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    aciklama = db.Column(db.Text, nullable=False)
    durum = db.Column(db.String(50), nullable=False)
    sorumlu = db.Column(db.String(80), nullable=False)
    bitis_tarihi = db.Column(db.String(20), nullable=False)
    oncelik = db.Column(db.String(20), nullable=True)
    baslangic_tarihi = db.Column(db.String(20), nullable=True)
    etiketler = db.Column(db.String(255), nullable=True)


with app.app_context():
    db.create_all()

# Giriş gerektiren sayfalar için decorator

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("kullanici_adi"):
            flash("Bu sayfayı görüntülemek için giriş yapmalısınız.", "warning")
            return redirect(url_for("anasayfa"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def anasayfa():
    return render_template("anasayfa.html")

@app.route("/giris", methods=["GET", "POST"])
def giris():
    # Otomatik yönlendirmeyi kaldırdık, böylece giriş sayfası her zaman açılır
    if request.method == "POST":
        kullanici_adi = request.form.get("kullanici_adi")
        sifre = request.form.get("sifre")
        kullanici = Kullanici.query.filter_by(username=kullanici_adi).first()
        if kullanici and kullanici.password == sifrele_sha256(sifre):
            session["kullanici_adi"] = kullanici.username
            flash("Başarıyla giriş yaptınız.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Kullanıcı adı veya şifre hatalı.", "danger")
    return render_template("giris.html")

@app.route("/kayit", methods=["GET", "POST"])
def kayit():
    if session.get("kullanici_adi"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            flash("Şifreler uyuşmuyor!", "danger")
            return render_template("kayit.html")
        if Kullanici.query.filter_by(username=username).first():
            flash("Bu kullanıcı adı zaten alınmış!", "danger")
            return render_template("kayit.html")
        if Kullanici.query.filter_by(email=email).first():
            flash("Bu e-posta zaten kayıtlı!", "danger")
            return render_template("kayit.html")
        sifreli_password = sifrele_sha256(password)
        yeni_kullanici = Kullanici(username=username, email=email, password=sifreli_password)
        db.session.add(yeni_kullanici)
        db.session.commit()
        flash("Kayıt başarılı! Giriş yapabilirsiniz.", "success")
        return redirect(url_for("giris"))
    return render_template("kayit.html")

@app.route("/hakkımızda")
def hakkımızda():
    return render_template("hakkımızda.html")

@app.route("/iletisim")
def iletisim():
    return render_template("iletisim.html")

@app.route("/giris/panel")
@login_required
def panel():
    return render_template("panel.html")

@app.route("/giris/panel/gorev_detay/<int:gorev_id>")
@login_required
def gorev_detay(gorev_id):
    gorev = Gorev.query.get_or_404(gorev_id)
    return render_template("gorev_detay.html", gorev=gorev)

@app.route("/giris/panel/gorev_liste")
@login_required
def gorev_liste():
    sayfa = request.args.get("sayfa", 1, type=int)
    sayfa_basi = 5  # Her sayfada kaç görev gözüksün?
    gorevler = Gorev.query.paginate(page=sayfa, per_page=sayfa_basi)
    return render_template("gorev_liste.html", gorevler=gorevler)

@app.route("/giris/panel/gorev_ekle", methods=["GET", "POST"])
@login_required
def gorev_ekle():
    kullanicilar = Kullanici.query.all()
    if request.method == "POST":
        ad = request.form.get("ad")
        aciklama = request.form.get("aciklama")
        durum = request.form.get("durum") or "Beklemede"
        sorumlu = request.form.get("sorumlu")
        bitis_tarihi = request.form.get("bitis_tarihi")
        oncelik = request.form.get("oncelik")
        baslangic_tarihi = request.form.get("baslangic_tarihi")
        etiketler = request.form.get("etiketler")
        yeni_gorev = Gorev(
            ad=ad,
            aciklama=aciklama,
            durum=durum,
            sorumlu=sorumlu,
            bitis_tarihi=bitis_tarihi,
            oncelik=oncelik,
            baslangic_tarihi=baslangic_tarihi,
            etiketler=etiketler
        )
        db.session.add(yeni_gorev)
        db.session.commit()
        flash("Görev başarıyla eklendi!", "success")
        return redirect(url_for("gorev_liste"))
    return render_template("gorev_ekle.html", kullanicilar=kullanicilar)

@app.route("/giris/panel/kullanıcılar")
@login_required
def kullanıcılar():
    kullanicilar = Kullanici.query.all()
    return render_template("kullanıcılar.html", kullanicilar=kullanicilar)

@app.route("/giris/panel/rapor")
@login_required
def rapor():
    gorevler = Gorev.query.all()
    kullanicilar = Kullanici.query.all()
    # Filtreler
    rapor_turu = request.args.get('rapor_turu')
    tarih_araligi = request.args.get('tarih_araligi')
    ekip_uyesi = request.args.get('ekip_uyesi')
    proje = request.args.get('proje')
    # Ekip üyesine göre filtrele
    if ekip_uyesi:
        gorevler = [g for g in gorevler if g.sorumlu == ekip_uyesi]
    # Proje alanı modelde yok, etiketlerde arama yapılabilir
    if proje:
        gorevler = [g for g in gorevler if g.etiketler and proje.lower() in g.etiketler.lower()]
    # Tarih aralığı (ör: 2024-06-01 - 2024-06-30)
    if tarih_araligi and '-' in tarih_araligi:
        try:
            start, end = [t.strip() for t in tarih_araligi.split('-')]
            gorevler = [g for g in gorevler if g.baslangic_tarihi and g.bitis_tarihi and start <= g.baslangic_tarihi <= end]
        except:
            pass
    # Rapor türü (örnek: sadece tamamlananları göster)
    if rapor_turu == 'gorev':
        pass  # Tüm görevler
    elif rapor_turu == 'performans':
        gorevler = [g for g in gorevler if g.durum == 'Tamamlandı']
    elif rapor_turu == 'ekip':
        pass  # Şimdilik tüm görevler, istenirse ekip bazlı eklenebilir
    toplam = len(gorevler)
    tamamlanan = len([g for g in gorevler if g.durum == 'Tamamlandı'])
    devam_eden = len([g for g in gorevler if g.durum == 'Devam Ediyor'])
    geciken = len([g for g in gorevler if g.durum == 'Gecikti'])
    tamam_oran = round((tamamlanan / toplam) * 100, 1) if toplam else 0
    devam_oran = round((devam_eden / toplam) * 100, 1) if toplam else 0
    gecik_oran = round((geciken / toplam) * 100, 1) if toplam else 0
    return render_template(
        "rapor.html",
        toplam=toplam,
        tamamlanan=tamamlanan,
        devam_eden=devam_eden,
        geciken=geciken,
        tamam_oran=tamam_oran,
        devam_oran=devam_oran,
        gecik_oran=gecik_oran,
        gorevler=gorevler,
        kullanicilar=kullanicilar
    )

@app.route("/giris/panel/rapor/pdf")
def rapor_pdf():
    font_path = os.path.join(os.path.dirname(__file__), "static", "DejaVuSans.ttf")
    pdfmetrics.registerFont(TTFont('DejaVu', font_path))

    gorevler = Gorev.query.all()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("DejaVu", 12)
    y = 750
    p.drawString(30, y, "Görev Raporu")
    y -= 30
    p.drawString(30, y, "Ad | Sorumlu | Başlangıç | Bitiş | Durum")
    y -= 20
    for gorev in gorevler:
        p.drawString(30, y, f"{gorev.ad} | {gorev.sorumlu} | {gorev.baslangic_tarihi or '-'} | {gorev.bitis_tarihi or '-'} | {gorev.durum}")
        y -= 20
        if y < 50:
            p.showPage()
            p.setFont("DejaVu", 12)
            y = 750
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="gorev_raporu.pdf", mimetype='application/pdf')

@app.route('/giris/panel/rapor/excel')
def rapor_excel():
    gorevler = Gorev.query.all()
    data = [{
        'Görev Adı': g.ad,
        'Sorumlu': g.sorumlu,
        'Başlangıç': g.baslangic_tarihi,
        'Bitiş': g.bitis_tarihi,
        'Durum': g.durum
    } for g in gorevler]
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Görevler')
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="gorev_raporu.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route("/giris/panel/gorev_sil/<int:gorev_id>", methods=["POST"])
@login_required
def gorev_sil(gorev_id):
    gorev = Gorev.query.get_or_404(gorev_id)
    db.session.delete(gorev)
    db.session.commit()
    flash("Görev başarıyla silindi!", "success")
    return redirect(url_for("gorev_liste"))

@app.route("/giris/panel/gorev_duzenle/<int:gorev_id>", methods=["GET", "POST"])
@login_required
def gorev_duzenle(gorev_id):
    gorev = Gorev.query.get_or_404(gorev_id)
    kullanicilar = Kullanici.query.all()
    if request.method == "POST":
        gorev.ad = request.form.get("ad")
        gorev.aciklama = request.form.get("aciklama")
        gorev.durum = request.form.get("durum") or "Beklemede"
        gorev.sorumlu = request.form.get("sorumlu")
        gorev.bitis_tarihi = request.form.get("bitis_tarihi")
        gorev.oncelik = request.form.get("oncelik")
        gorev.baslangic_tarihi = request.form.get("baslangic_tarihi")
        gorev.etiketler = request.form.get("etiketler")
        db.session.commit()
        flash("Görev başarıyla güncellendi!", "success")
        return redirect(url_for("gorev_liste"))
    return render_template("gorev_duzenle.html", gorev=gorev, kullanicilar=kullanicilar)


@app.route("/cikis")
def cikis():
    session.clear()
    flash("Başarıyla çıkış yaptınız.", "success")
    return redirect(url_for("giris"))

@app.route("/dashboard")
@login_required
def dashboard():
    gorevler = Gorev.query.all()
    toplam = len(gorevler)
    tamamlanan = len([g for g in gorevler if g.durum == 'Tamamlandı'])
    devam_eden = len([g for g in gorevler if g.durum == 'Devam Ediyor'])
    geciken = len([g for g in gorevler if g.durum == 'Gecikti'])
    return render_template(
        "dashboard.html",
        gorevler=gorevler,
        toplam=toplam,
        tamamlanan=tamamlanan,
        devam_eden=devam_eden,
        geciken=geciken
    )

def export_gorevler_to_json():
    with app.app_context():
        gorevler = Gorev.query.all()
        data = []
        for gorev in gorevler:
            data.append({
                'id': gorev.id,
                'ad': gorev.ad,
                'aciklama': gorev.aciklama,
                'durum': gorev.durum,
                'sorumlu': gorev.sorumlu,
                'bitis_tarihi': gorev.bitis_tarihi,
                'oncelik': gorev.oncelik,
                'baslangic_tarihi': gorev.baslangic_tarihi,
                'etiketler': gorev.etiketler
            })

        with open('gorevler.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print("Görevler başarıyla gorevler.json dosyasına kaydedildi!")

def export_kullanicilar_to_json():
    with app.app_context():
        kullanicilar = Kullanici.query.all()
        data = []
        for kullanici in kullanicilar:
            data.append({
                'id': kullanici.id,
                'username': kullanici.username,
                'email': kullanici.email,
                 'password': kullanici.password  # Şifreyi şifrelenmiş olarak saklıyoruz
                # Eğer başka alanlar varsa ekleyebilirsin
            })

        with open('kullanicilar.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print("Kullanıcılar başarıyla kullanicilar.json dosyasına kaydedildi!")

def sifrele_sha256(sifre):
    return hashlib.sha256(sifre.encode()).hexdigest()

#if __name__ == "__main__":
    #export_gorevler_to_json()
    #export_kullanicilar_to_json()
    #app.run(debug=True)

import os
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
