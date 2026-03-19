from flask import Flask, render_template, request, redirect
import gspread
import json
import os
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# ==============================
# CONECTAR AO GOOGLE SHEETS
# ==============================
def conectar_planilha(nome_aba):

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    if "GOOGLE_CREDENTIALS" in os.environ:
        credenciais_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])

        creds = Credentials.from_service_account_info(
            credenciais_dict,
            scopes=scope
        )
    else:
        creds = Credentials.from_service_account_file(
            "credentials.json",
            scopes=scope
        )

    client = gspread.authorize(creds)

    planilha = client.open_by_key(
        "1FnxxnmIe8-to-Fek918vUUBc9asCIbLCJaOcUAjGoz4"
    ).worksheet(nome_aba)

    return planilha

# ==============================
# ROTA PRINCIPAL
# ==============================
@app.route("/")
def index():
    return render_template("index.html")


# ==============================
# SALVAR DADOS
# ==============================
@app.route("/salvar", methods=["POST"])
def salvar():

    cliente = request.form.get("cliente")
    local = request.form.get("local")
    setor = request.form.get("setor")

    # ====================================================
    # ================= MEDIDORES ========================
    # ====================================================
    ws_med = conectar_planilha("Medidores")

    try:
        qtd_medidores = int(request.form.get("qtd_medidor", 0))
    except:
        qtd_medidores = 0

    linhas_medidores = []

    for i in range(1, qtd_medidores + 1):

        tipo = request.form.get(f"tipo_medidor_{i}")

        # -------- CAMPOS PADRÃO --------
        base = [
            cliente,
            local,
            setor,
            request.form.get(f"tag_name_medidor_{i}"),
            request.form.get(f"label_{i}"),
            request.form.get(f"qual_medidor_{i}"),
            tipo
        ]

        # -------- UPENERGY --------
        if tipo == "UPENERGY":
            extra = [
                request.form.get(f"id1_{i}"),
                request.form.get(f"id2_{i}"),
                request.form.get(f"device_address_{i}"),
                request.form.get(f"tc_{i}"),
                request.form.get(f"kc_{i}"),
                request.form.get(f"kt_{i}"),
                request.form.get(f"tensao_{i}"),
                "", "", "", "", "", "", ""  # padding KRON
            ]

        # -------- KRON --------
        elif tipo == "KRON-Multimedidor":
            extra = [
                "", "",  # id1, id2
                request.form.get(f"device_address_{i}"),
                request.form.get(f"tc_{i}"),
                "",  # kc
                "",  # kt
                "",  # tensao
                request.form.get(f"threshold_{i}"),
                request.form.get(f"serial_{i}"),
                request.form.get(f"ti_{i}"),
                request.form.get(f"tl_{i}"),
                request.form.get(f"tp_{i}")
            ]

        # -------- OUTROS --------
        else:
            extra = [""] * 14

        linhas_medidores.append(base + extra)

    if linhas_medidores:
        ws_med.append_rows(linhas_medidores)

    # ====================================================
    # ================= CONCENTRADORES ===================
    # ====================================================
    ws_conc = conectar_planilha("Concentradores")

    try:
        qtd_conc = int(request.form.get("qtd_concentrador", 0))
    except:
        qtd_conc = 0

    linhas_conc = []

    for i in range(1, qtd_conc + 1):

        tipo_eth = request.form.get(f"tipo_eth_{i}")

        linhas_conc.append([
            cliente,
            local,
            setor,
            request.form.get(f"modelo_{i}"),
            request.form.get(f"numero_serie_{i}"),
            request.form.get(f"tag_name_{i}"),
            request.form.get(f"client_cod_{i}"),
            tipo_eth,
            request.form.get(f"faixa_ip_{i}") if tipo_eth == "Via cabo" else "",
            request.form.get(f"usuario_wifi_{i}") if tipo_eth == "Wi-Fi" else "",
            request.form.get(f"senha_wifi_{i}") if tipo_eth == "Wi-Fi" else ""
        ])

    if linhas_conc:
        ws_conc.append_rows(linhas_conc)

    # ====================================================
    # ================= NOBREAKS =========================
    # ====================================================
    ws_nob = conectar_planilha("Nobreaks")

    try:
        qtd_nob = int(request.form.get("qtd_nobreak", 0))
    except:
        qtd_nob = 0

    linhas_nob = []

    for i in range(1, qtd_nob + 1):
        linhas_nob.append([
            cliente,
            local,
            setor,
            request.form.get(f"qual_nobreak_{i}"),
            request.form.get(f"fabricante_nobreak_{i}"),
            request.form.get(f"tag_nobreak_{i}")
        ])

    if linhas_nob:
        ws_nob.append_rows(linhas_nob)

    # ====================================================
    # ================= RADIOS ===========================
    # ====================================================
    ws_rad = conectar_planilha("Radios")

    try:
        qtd_rad = int(request.form.get("qtd_radio", 0))
    except:
        qtd_rad = 0

    linhas_rad = []

    for i in range(1, qtd_rad + 1):
        linhas_rad.append([
            cliente,
            local,
            setor,
            request.form.get(f"qual_radio_{i}"),
            request.form.get(f"fabricante_radio_{i}"),
            request.form.get(f"tag_radio_{i}"),
            request.form.get(f"endereco_radio_{i}"),
            request.form.get(f"canal_radio_{i}")
        ])

    if linhas_rad:
        ws_rad.append_rows(linhas_rad)

    return redirect("/")

# ==============================
# EXECUTAR
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


