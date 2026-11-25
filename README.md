# SINERAFIL
# Sistema Informasaun Jestaun Inventáriu Pesa-Rezerva no Reparasaun — Ofisina Nerafil

Aplikasaun web Django ba jestaun inventáriu pesa-rezerva no reparasaun motór iha Ofisina Nerafil
(tesis S1 Informatika: *Dezeñu no Dezenvolvimentu ba Sistema Informasaun Jestaun Inventáriu Pesa-Rezerva no
Reparasaun iha Ofisina Nerafil Uza Framework Django*). Database no alur sistema tuir **ERD** no **flowchart** husi dosen.

## 🚀 Teknologia
- Python 3 · Django 5.2 · SQLite3
- Bootstrap 4.6.2 · jQuery · Font Awesome 5 · DataTables · Chart.js (**hotu offline** iha `main/static/main/vendor/`)
- django-crispy-forms (bootstrap4) · python-decouple · ReportLab (PDF) · openpyxl (impor Excel)

## 📁 Estrutura Projetu
```bash
Sinerafil/          # Django project configuration (settings, urls, wsgi)
config/             # Decorators (allowed_users), helper form, activity log, utility
custom/             # CATEGORY no SUPPLIER
main/               # Login (Start), layout/sidebar/navbar, static (vendor offline)
users/              # USER (ho role) no ACTIVITY_LOG
inventory/          # PART no STOCK_MOVEMENT (+ import_excel)
customers/          # CUSTOMER no EQUIPMENT
repairs/            # REPAIR no REPAIR_PART (workflow reparasaun)
report/             # Dashboard (grafiku) no Reports PDF
data/               # File Excel orijinál (NOTA DAVID)
```
Konvensaun (hanesan projetu SJAMCI): view *function-based* iha pakote `views/`; form uza *crispy-forms*;
papél uza `@allowed_users(allowed_roles=[...])`; template extend `main/layout.html`.

## ⚙️ Instalasaun
```bash
python -m venv venv && source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                     # opsionál
python manage.py migrate
python manage.py import_excel      # impor 129 pesa-rezerva husi data/NOTA_DAVID_TILES-II.xlsx (opsionál)
python manage.py seed_demo         # utilizadór demo + kliente/reparasaun ezemplu (opsionál)
python manage.py runserver
```
Loke http://127.0.0.1:8000/ (Start = System Login). Password hotu-hotu iha demo: `nerafil123`.
Atu kria admin rasik: `python manage.py createsuperuser` (papél otomátiku `admin`).

| Username | Role (kolun `user.role`) | Direitu asesu |
|---|---|---|
| `admin` | `admin` | Hotu: inventory, kategoria, supplier, kliente, ekipamentu, rejistu/diagnóstiku/hili mekániku, reparasaun, reports, utilizadór, activity log |
| `zin`, `anata`, `abosa` | `technician` | Haree pesa/kliente/ekipamentu; reparasaun *hili ba nia*: edita diagnóstiku, uza pesa, hahú prosesu, konfirma remata |
| `nain` | `owner` | Haree de'it (read-only): dashboard, stock, reparasaun, reports PDF |

## 🗄️ Database = ERD dosen
Tabel no kolun tuir ERD (10 tabel). Kolun **tambahan** (la iha iha ERD, presiza ba alur/fitur) marka ho ★:

| Tabel | Kolun (ERD) | ★ Tambahan |
|---|---|---|
| `user` | id, username, password, role | ★ full_name, ★ is_active |
| `activity_log` | id, user_id (FK), action, created_at | — |
| `customer` | id, name, phone | — |
| `equipment` | id, customer_id (FK), name, serial_number | ★ plate (plaka) |
| `category` | id, name | — |
| `supplier` | id, name, phone | — |
| `part` | id, sku, name, category_id (FK), supplier_id (FK), stock, minimum_stock, purchase_price | ★ selling_price (folin faan, default ba `unit_price`) |
| `repair` | id, repair_number, customer_id, equipment_id, technician_id (FK→user), status, service_cost | ★ diagnosis (etapa *Damage Diagnosis*), ★ created_at |
| `repair_part` | id, repair_id (FK), part_id (FK), quantity, unit_price | — |
| `stock_movement` | id, part_id (FK), movement_type (`in`/`out`), quantity, created_at | ★ note |

Relasaun: customer 1—N equipment · customer 1—N repair · equipment 1—N repair · user 1—N repair (*handles*) ·
user 1—N activity_log (*creates*) · category 1—N part · supplier 1—N part · repair 1—N repair_part ·
part 1—N repair_part · part 1—N stock_movement. Teste `SchemaTests` verifika naran tabel/kolun automátikamente.

`repair.status`: `registered` → `diagnosed` → `assigned` → `in_progress` → `completed`.

## 🔁 Flowchart dosen = alur sistema
| Flowchart | Iha sistema |
|---|---|
| Start → System Login → User Validation | `/` (login). Invalid → fila ba login ho mensajen erru; Valid → Dashboard (rejistu *Login* iha activity log) |
| Dashboard | `/Reports/dashboard/` — kartu, alerta stock mínimu, grafiku, reparasaun foun |
| Inventory Management → Spare Parts Data | menu *Spare Parts Data* (CRUD `part`; kategoria no supplier) |
| → Stock In / Stock Out → Update Stock Quantity | menu *Stock In / Out*: movimentu `in`/`out` atualiza `part.stock` (stock labele negativu) |
| Repair Management → Customer and Equipment Data | menu *Customer Data* no *Equipment Data* |
| → Register New Repair | *Repairs → Reparasaun Foun* (etapa 1, admin) |
| → Damage Diagnosis | etapa 2: kolun `diagnosis` |
| → Assign Technician | etapa 3: `repair.technician` (admin) |
| → Spare Parts Usage → Automatic Stock Update | etapa 4: aumenta pesa → `repair_part` + movimentu `out` automátiku (hasai = stock fila fali) |
| → Repair Process | etapa 5: mekániku hahú prosesu |
| → Confirm Completion | etapa 6: konfirma remata + `service_cost`; reparasaun sai *locked* |
| → Reports → Finish | menu *Reports (PDF)*: stock, movimentu stock, reparasaun/finanseiru; invoice PDF kada reparasaun |

Pájina detallu reparasaun hatudu *stepper* 6 etapa (verde = remata, mean = etapa atuál) no botaun ba etapa tuir mai.
Ordem etapa sei loloos iha server (ex: labele uza pesa molok hili mekániku).

## 🧮 Kálkulu
- `Total reparasaun = service_cost + Σ (quantity × unit_price)`
- `Lukru estimadu = service_cost + Σ ((unit_price − part.purchase_price) × quantity)`
- Dashboard no relatóriu finanseiru uza de'it reparasaun ho status `completed`.

## 🧪 Teste
`python manage.py test` — kobre skema ERD, alur 6 etapa, stock automátiku, papél (admin/technician/owner), login,
activity log, no PDF.

## 📝 Nota
- Folin sosa husi Excel (Rupiah) konverte ba USD ho kursu `KURS_RUPIAH_PER_USD` (default 16000;
  `python manage.py import_excel --kurs 15500`). Supplier = `NOTA DAVID`.
- Naran/enderesu/telefone ofisina iha kop PDF: troka iha `.env` (`SHOP_*`).
- Tabel `user` la iha `last_login` (tuir ERD), no Django admin site la uza.
- Molok produsaun: troka `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, no `python manage.py collectstatic`.
- Fitur Kios (faan sasán/scanner barcode) hasai tanba la iha iha ERD/flowchart; kódigu iha git history (commit `4ee4100`).
