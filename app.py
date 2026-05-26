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
    # Colunas: Cliente | Local | Setor | Tag Name | Label | Qual Medidor | Tipo de Medidor
    #        | ID1 | ID2 | Device Address | TC | Relação KC | Relação KT | Tensão F/N
    #        | Threshold | Serial | TI | TL | TP
    #        | Port | Protocol | Baud Rate | Rx Timeout | Serial Port | MAC | IP
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
            cliente,                                   # Cliente
            local,                                     # Local
            setor,                                     # Setor
            request.form.get(f"tag_name_medidor_{i}"), # Tag Name
            request.form.get(f"label_{i}"),            # Label
            request.form.get(f"qual_medidor_{i}"),     # Qual Medidor
            tipo                                       # Tipo de Medidor
        ]

        # -------- UPENERGY --------
        if tipo == "UPENERGY":
            extra = [
                request.form.get(f"id1_{i}"),          # ID1
                request.form.get(f"id2_{i}"),          # ID2
                request.form.get(f"device_address_{i}"),# Device Address
                request.form.get(f"tc_{i}"),           # TC
                request.form.get(f"kc_{i}"),           # Relação KC
                request.form.get(f"kt_{i}"),           # Relação KT
                request.form.get(f"tensao_{i}"),       # Tensão F/N
                "", "", "", "", "",                    # Threshold, Serial, TI, TL, TP
                "", "", "", "", "", "",                # Port, Protocol, Baud Rate, Rx Timeout, Serial Port, MAC
                ""                                     # IP
            ]

        # -------- ION --------
        elif tipo == "ION":
            extra = [
                "", "",                                    # ID1, ID2
                request.form.get(f"device_address_{i}"),  # Device Address
                "", "", "", "",                            # TC, Relação KC, Relação KT, Tensão F/N
                "", "", "", "", "",                        # Threshold, Serial, TI, TL, TP
                request.form.get(f"port_ion_{i}"),         # Port
                request.form.get(f"protocol_ion_{i}"),     # Protocol
                request.form.get(f"baudrate_ion_{i}"),     # Baud Rate
                request.form.get(f"rxtimeout_ion_{i}"),    # Rx Timeout
                request.form.get(f"serialport_ion_{i}"),   # Serial Port
                "", ""                                     # MAC, IP
            ]

        # -------- KRON --------
        elif tipo == "KRON-Multimedidor":
            extra = [
                "", "",                                    # ID1, ID2
                request.form.get(f"device_address_{i}"),  # Device Address
                request.form.get(f"tc_{i}"),               # TC
                request.form.get(f"kc_{i}"),               # Relação KC
                "",                                        # Relação KT
                request.form.get(f"tensao_{i}"),           # Tensão F/N
                request.form.get(f"threshold_{i}"),        # Threshold
                request.form.get(f"serial_{i}"),           # Serial
                request.form.get(f"ti_{i}"),               # TI
                request.form.get(f"tl_{i}"),               # TL
                request.form.get(f"tp_{i}"),               # TP
                "", "", "", "", "", "",                    # Port, Protocol, Baud Rate, Rx Timeout, Serial Port, MAC
                ""                                         # IP
            ]

        # -------- CCK-Multimedidor --------
        elif tipo == "CCK-Multimedidor":
            extra = [
                "", "",                                    # ID1, ID2
                request.form.get(f"device_address_{i}"),  # Device Address
                request.form.get(f"tc_{i}"),               # TC
                request.form.get(f"kc_{i}"),               # Relação KC
                "",                                        # Relação KT
                request.form.get(f"tensao_{i}"),           # Tensão F/N
                request.form.get(f"threshold_{i}"),        # Threshold
                request.form.get(f"serial_{i}"),           # Serial
                request.form.get(f"ti_{i}"),               # TI
                request.form.get(f"tl_{i}"),               # TL
                request.form.get(f"tp_{i}"),               # TP
                "", "", "", "", "", "",                    # Port, Protocol, Baud Rate, Rx Timeout, Serial Port, MAC
                ""                                         # IP
            ]

        # -------- IMS --------
        elif tipo == "IMS-ABNT":
            extra = [
                "", "",                                        # ID1, ID2
                request.form.get(f"endereco_id_ims_{i}"),     # Device Address
                "", "", "", "",                                # TC, Relação KC, Relação KT, Tensão F/N
                "", "", "", "", "",                            # Threshold, Serial, TI, TL, TP
                "",                                            # Port
                "",                                            # Protocol
                request.form.get(f"baudrate_ims_{i}"),        # Baud Rate
                "",                                            # Rx Timeout
                "",                                            # Serial Port
                request.form.get(f"mac_ims_{i}"),             # MAC
                request.form.get(f"ip_ims_{i}")               # IP
            ]

        # -------- OUTROS --------
        else:
            extra = [""] * 19

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
    # Colunas: Cliente | Local | Setor | Qual Radio | Fabricante | Tag | ID | Canal
    # ====================================================
    ws_rad = conectar_planilha("Radios")

    try:
        qtd_rad = int(request.form.get("qtd_radio", 0))
    except:
        qtd_rad = 0

    linhas_rad = []

    for i in range(1, qtd_rad + 1):
        linhas_rad.append([
            cliente,                                      # Cliente
            local,                                        # Local
            setor,                                        # Setor
            request.form.get(f"qual_radio_{i}"),          # Qual Radio
            request.form.get(f"fabricante_radio_{i}"),    # Fabricante
            request.form.get(f"tag_radio_{i}"),           # Tag
            request.form.get(f"id_radio_{i}"),            # ID
            request.form.get(f"canal_radio_{i}")          # Canal
        ])

    if linhas_rad:
        ws_rad.append_rows(linhas_rad)

    # ====================================================
    # ================= GERADORES ========================
    # ====================================================
    ws_ger = conectar_planilha("Geradores")

    try:
        qtd_ger = int(request.form.get("qtd_gerador", 0))
    except:
        qtd_ger = 0

    linhas_ger = []

    for i in range(1, qtd_ger + 1):
        linhas_ger.append([
            cliente,
            local,
            setor,
            request.form.get(f"fabricante_gerador_{i}"),
            request.form.get(f"tag_gerador_{i}"),
            request.form.get(f"gateway_gerador_{i}"),
            request.form.get(f"ip_gerador_{i}"),
            request.form.get(f"baudrate_gerador_{i}"),
            request.form.get(f"id_gerador_{i}"),
            request.form.get(f"paridade_gerador_{i}")            
        ])

    if linhas_ger:
        ws_ger.append_rows(linhas_ger)

    return redirect("/")

# ==============================
# EXECUTAR
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
