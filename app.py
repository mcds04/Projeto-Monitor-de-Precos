from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Monitor de Preços</title>
<style>
body {
    font-family: Arial;
    background: #0f172a;
    color: white;
    text-align: center;
}
.container {
    max-width: 400px;
    margin: auto;
}
input, button {
    width: 100%;
    padding: 10px;
    margin: 5px 0;
    border-radius: 8px;
    border: none;
}
button {
    background: #22c55e;
    color: white;
    font-weight: bold;
}
.card {
    background: #1e293b;
    padding: 10px;
    margin-top: 10px;
    border-radius: 10px;
}
a { color: #38bdf8; text-decoration: none; }
</style>
</head>

<body>
<div class="container">
<h2>📦 Monitor de Preços</h2>

<form method="POST">
<input type="text" name="url" placeholder="Link do produto" required>
<input type="number" step="0.01" name="preco" placeholder="Preço alvo" required>
<button type="submit">Adicionar</button>
</form>

<h3>📋 Produtos</h3>

{% for p in produtos %}
<div class="card">
<a href="{{p[1]}}" target="_blank">Abrir Produto</a><br><br>
Preço alvo: R$ {{p[2]}}<br><br>
<a href="/?delete={{p[0]}}">❌ Remover</a>
</div>
{% endfor %}

</div>
</body>
</html>
"""

def conectar():
    return sqlite3.connect("produtos.db")

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        preco_alvo REAL,
        ultimo_preco REAL
    )
    """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    conn = conectar()
    cursor = conn.cursor()

    # adicionar produto
    if request.method == "POST":
        url = request.form["url"]
        preco = float(request.form["preco"])

        cursor.execute("SELECT * FROM produtos WHERE url=?", (url,))
        existe = cursor.fetchone()

        if not existe:
            cursor.execute(
                "INSERT INTO produtos (url, preco_alvo, ultimo_preco) VALUES (?, ?, ?)",
                (url, preco, 0)
            )
            conn.commit()

    # remover produto
    if "delete" in request.args:
        id = request.args.get("delete")
        cursor.execute("DELETE FROM produtos WHERE id=?", (id,))
        conn.commit()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()

    return render_template_string(HTML, produtos=produtos)

criar_tabela()

print("🔥 PAINEL RODANDO...")

app.run(host="0.0.0.0", port=5000)
