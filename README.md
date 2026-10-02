# SINERAFIL
# Sistema Informasaun Jestaun Inventáriu Pesa-Rezerva no Reparasaun — Ofisina Nerafil

SINERAFIL mak aplikasaun web Django ba jestaun inventáriu pesa-rezerva no servisu reparasaun motór iha Ofisina Nerafil
(tesis S1 Informatika: *Dezeñu no Dezenvolvimentu ba Sistema Informasaun Jestaun Inventáriu Pesa-Rezerva no Reparasaun iha Ofisina Nerafil Uza Framework Django*).

## 🚀 Teknologia

- Python 3 · Django 5.2 · SQLite3
- Bootstrap 4.6.2 · jQuery · Font Awesome 5 · DataTables · Chart.js (**hotu offline** iha `main/static/main/vendor/`)
- django-crispy-forms (bootstrap4) · python-decouple · ReportLab (PDF) · openpyxl (impor Excel)
- Git & GitHub

## 📁 Estrutura Projetu

```bash
Sinerafil/          # Django project configuration (settings, urls, wsgi)
config/             # Utility, decorators (allowed_users), auth utils, helper form
custom/             # BaseModel (audit + soft delete) no Kategoria pesa
main/               # Landing, login/logout, home, layout/sidebar/navbar, static (vendor offline)
users/              # Funcionariu (Emp), konta (EmpUser), AuditLogin, jestaun utilizadór
pesa/               # Pesa-rezerva, movimentu stock (tama/sai), import_excel
cliente/            # Kliente no Motór
servisu/            # Servisu reparasaun, pesa ne'ebé uza, despeza
report/             # Dashboard (grafiku) no relatóriu PDF
data/               # File Excel orijinál (NOTA DAVID)
manage.py
```

Konvensaun (hanesan projetu SJAMCI): model herda `BaseModel`; view sai *function-based* iha pakote `views/`
(`views_*.py` + `__init__.py`); form uza *crispy-forms* ho `FormHelper` Layout; papél uza Django **Group** ho
`@allowed_users(allowed_roles=[...])`; template extend `main/layout.html`.

## ⚙️ Instalasaun

```bash
python -m venv venv && source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                     # opsionál: troka valór
python manage.py migrate
python manage.py import_excel      # impor 129 pesa-rezerva husi data/NOTA_DAVID_TILES-II.xlsx
python manage.py seed_demo         # utilizadór demo + kliente/servisu ezemplu (opsionál)
python manage.py runserver
```

Loke http://127.0.0.1:8000/ . Password hotu-hotu iha demo: `nerafil123`

| Username | Grupu | Direitu asesu |
|---|---|---|
| `admin` | admin | Hotu: pesa, stock tama/sai, kliente, motór, servisu, despeza, relatóriu, utilizadór |
| `zin`, `anata`, `abosa` | mekaniku | Haree pesa; kria/edita servisu *rasik nian* ne'ebé seidauk remata no uza pesa; kliente & motór |
| `nain` | nain | Haree de'it (read-only): dashboard finanseiru, stock, servisu, despeza no relatóriu PDF |

Atu kria konta admin rasik: `python manage.py createsuperuser` (superuser sempre trata hanesan admin).

## ✅ Funsaun prinsipál

- **Pesa-rezerva (CRUD)** ho kategoria, folin sosa/faan (USD), stock no stock mínimu.
- **Sasán tama / sai**: kada movimentu atualiza stock; stock labele negativu.
- **Alerta stock mínimu**: badge iha sidebar, banner iha dashboard no home, filtru "Stock mínimu de'it".
- **Kliente no motór**; **Servisu** ho nú. nota automátiku (`SRV-AAAAMM-0001`); pesa uza → stock redús
  automátiku (hasai pesa ka hamoos servisu → stock fila fali).
- **Dashboard** ho grafiku (rendimentu/lukru 6 fulan, status servisu, pesa uza barak liu).
- **PDF** (ReportLab): relatóriu stock, tama/sai, finanseiru no nota servisu.

## 🧮 Kálkulu servisu

- `Total = total pesa + ongkos servisu − diskaun`
- `Ongkos mekániku = ongkos × persen mekániku` (default husi dadus funcionariu mekániku, 10%)
- `Lukru ofisina = lukru pesa (folin faan − folin sosa) + ongkos bersih − diskaun`

## 🧪 Teste

`python manage.py test` — kobre stock, kálkulu, permisaun papél, form no PDF.

## 📝 Nota

- Folin sosa husi Excel (Rupiah) konverte ba USD ho kursu `KURS_RUPIAH_PER_USD` (default 16000;
  `python manage.py import_excel --kurs 15500`).
- Naran/enderesu/telefone ofisina iha kop PDF no landing: troka iha `.env` (`SHOP_*`).
- Molok produsaun: troka `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` no `python manage.py collectstatic`.
