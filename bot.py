from bs4 import BeautifulSoup
import time
import random
import sqlite3

TOKEN_TELEGRAM = "SEU_TOKEN_AQUI"
SEU_ID_TELEGRAM = "8704677929"

conn = sqlite3.connect("produtos.db")
cursor = conn.cursor()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {"chat_id": SEU_ID_TELEGRAM, "text": mensagem}

    try:
        response = requests.post(url, data=payload)
        print(response.text)
    except Exception as e:
        print(f"Erro Telegram: {e}")

def pegar_preco_amazon(url):
    for _ in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            # tenta vários seletores
            seletores = [
                ("span", {"class": "a-offscreen"}),
                ("span", {"class": "a-price-whole"})
            ]

            for tag, attr in seletores:
                preco = soup.find(tag, attr)
                if preco:
                    valor = preco.text
                    valor = valor.replace("R$", "").replace(".", "").replace(",", ".")
                    return float(valor)

        except:
            pass

        print("🔁 Tentando novamente Amazon...")
        time.sleep(random.randint(2, 4))

    return None

def pegar_preco_mercadolivre(url):
    for _ in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            preco = soup.find("span", {"class": "andes-money-amount__fraction"})

            if preco:
                valor = preco.text.replace(".", "")
                return float(valor)

        except:
            pass

        print("🔁 Tentando novamente ML...")
        time.sleep(random.randint(2, 4))

    return None

def pegar_preco(url):
    if "amazon" in url or "a.co" in url:
        return pegar_preco_amazon(url)

    elif "mercadolivre" in url:
        return pegar_preco_mercadolivre(url)

    else:
        print("❌ Loja não suportada")
        return None

def verificar_precos():
    cursor.execute("SELECT id, url, preco_alvo, ultimo_preco FROM produtos")
    produtos = cursor.fetchall()

    for id, url, preco_alvo, ultimo_preco in produtos:

        print(f"🔍 Verificando: {url}")

        preco = pegar_preco(url)

        if preco is None:
            print("❌ Falhou, tenta no próximo ciclo")
            continue

        print(f"💰 Preço atual: R$ {preco:.2f}")

        if preco <= preco_alvo and preco != ultimo_preco:
            msg = f"🔥 OPORTUNIDADE!\nPreço: R$ {preco}\n{url}"
            enviar_telegram(msg)

            cursor.execute(
                "UPDATE produtos SET ultimo_preco=? WHERE id=?",
                (preco, id)
            )
            conn.commit()

            print("✅ Alerta enviado!")

while True:
    verificar_precos()
    time.sleep(random.randint(60, 120))  # mais intervalo = menos bloqueio
