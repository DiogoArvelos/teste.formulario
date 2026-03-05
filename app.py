from flask import Flask, render_template, request, redirect
import gspread
from google.oauth2.service_account import Credentials
import os
import json

app = Flask(__name__)

# ==========================================
# CONECTAR AO GOOGLE SHEETS
# ==========================================

def conectar_planilha(nome_aba):
    cred_json = os.environ.get("GOOGLE_CREDENTIALS")
    cred_dict = json.loads(cred_json)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(
        cred_dict, scopes=scopes
    )

    client = gspread.authorize(credentials)

    planilha = client.open("Sistema Medidores").worksheet(nome_aba)

    return planilha


# ==========================================
# ROTA PRINCIPAL
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")


# ==========================================
# SALVAR DADOS
# ==========================================

@app.route("/salvar", methods=["POST"])
def salvar():

    cliente = request.form.get("cliente")
    local = request.form.get("local")
    setor = request.form.get("setor")

    # ====================================================
    # ================= MEDIDORES ========================
    # ====================================================

    ws_med = conectar_planilha("Medidores")
    qtd_medidores = int(request.form.get("qtd_medidor") or 0)

    for i in range(1, qtd_medidores + 1):

        qual_medidor = request.form.get(f"qual_medidor_{i}")
        tipo_medidor = request.form.get(f"tipo_medidor_{i}")

        ws_med.append_row([
            cliente,
            local,
            setor,
            request.form.get(f"tag_name_medidor_{i}"),
            request.form.get(f"label_{i}"),
            qual_medidor,
            tipo_medidor,
            request.form.get(f"id1_{i}"),
            request.form.get(f"id2_{i}"),
            request.form.get(f"device_address_{i}"),
            request.form.get(f"tc_{i}"),
            request.form.get(f"kc_{i}"),
            request.form.get(f"kt_{i}"),
            request.form.get(f"tensao_{i}")
        ])

    # ====================================================
    # ================= CONCENTRADORES ===================
    # ====================================================

    ws_conc = conectar_planilha("Concentradores")
    qtd_conc = int(request.form.get("qtd_concentrador") or 0)

    for i in range(1, qtd_conc + 1):

        tipo_eth = request.form.get(f"tipo_eth_{i}")

        ws_conc.append_row([
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

    # ====================================================
    # ================= NOBREAKS =========================
    # ====================================================

    ws_nob = conectar_planilha("Nobreaks")
    qtd_nob = int(request.form.get("qtd_nobreak") or 0)

    for i in range(1, qtd_nob + 1):

        ws_nob.append_row([
            cliente,
            local,
            setor,
            request.form.get(f"qual_nobreak_{i}"),
            request.form.get(f"fabricante_nobreak_{i}"),
            request.form.get(f"tag_nobreak_{i}")
        ])

    # ====================================================
    # ================= RADIOS ===========================
    # ====================================================

    ws_rad = conectar_planilha("Radios")
    qtd_rad = int(request.form.get("qtd_radio") or 0)

    for i in range(1, qtd_rad + 1):

        ws_rad.append_row([
            cliente,
            local,
            setor,
            request.form.get(f"qual_radio_{i}"),
            request.form.get(f"fabricante_radio_{i}"),
            request.form.get(f"tag_radio_{i}"),
            request.form.get(f"endereco_radio_{i}"),
            request.form.get(f"canal_radio_{i}")
        ])

    return redirect("/")


# ==========================================
# EXECUTAR
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
