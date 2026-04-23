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
                request.form.get(f"tensao_{i}"), 
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
            # ETH
            request.form.get(f"mac_eth_{i}"),
            request.form.get(f"ip_eth_{i}"),
            request.form.get(f"gateway_eth_{i}"),

            # WAN
            request.form.get(f"mac_wan_{i}"),
            request.form.get(f"ip_wan_{i}"),
            request.form.get(f"gateway_wan_{i}")
        ])

    if linhas_conc:
        ws_conc.append_rows(linhas_conc)
    # ====================================================
    # ================= CONVERSORES =======================
    # ====================================================
    ws_conv = conectar_planilha("Conversores")

    try:
        qtd_conv = int(request.form.get("qtd_conversor", 0))
    except:
        qtd_conv = 0

    linhas_conv = []

    for i in range(1, qtd_conv + 1):
        linhas_conv.append([
            cliente,
            local,
            setor,
            request.form.get(f"tag_conversor_{i}"),
            request.form.get(f"ip_conversor_{i}"),
            request.form.get(f"tipo_conversor_{i}"),
            request.form.get(f"mac_conversor_{i}"),
            request.form.get(f"baudrate_{i}"),
            request.form.get(f"endereco_id_{i}"),
            request.form.get(f"paridade_{i}")
        ])

    if linhas_conv:
        ws_conv.append_rows(linhas_conv)

    # ====================================================
    # ============= EQUIPAMENTOS DE REDE =================
    # ====================================================
    ws_eq = conectar_planilha("Equipamentos de Rede")

    try:
        qtd_eq = int(request.form.get("qtd_equipamento_rede", 0))
    except:
        qtd_eq = 0

    linhas_eq = []

    for i in range(1, qtd_eq + 1):
        linhas_eq.append([
            cliente,
            local,
            setor,
            request.form.get(f"tipo_equipamento_{i}"),
            request.form.get(f"fabricante_equipamento_{i}"),
            request.form.get(f"tag_equipamento_{i}")
        ])

    if linhas_eq:
        ws_eq.append_rows(linhas_eq)

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
            request.form.get(f"id_radio_{i}"),
            request.form.get(f"endereco_radio_{i}"),
            request.form.get(f"canal_radio_{i}"),
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
