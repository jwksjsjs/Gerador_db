import json
import sqlite3
import subprocess
import sys
import re


def install_dependencies():
    packages = [
        "llama-cpp-python",
        "fastapi",
        "uvicorn"
    ]

    for pkg in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


install_dependencies()
from llama_cpp import Llama

MODEL_PATH = "vicuna-7b.Q4_K_M.gguf"

def extract_json(text):
    """
    Extrai JSON da resposta da LLM
    """
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        return json.loads(match.group())
    else:
        raise ValueError("JSON não encontrado na resposta da IA")


class IaSystem:

    def __init__(self):
        print("Carregando modelo...\n")
        self.llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=4096
        )

    def ask(self, prompt):

        out = self.llm(
            prompt,
            temperature=0.1,
            max_tokens=1200
        )

        return out["choices"][0]["text"].strip()

    def planner(self, description):

        prompt = f"""
Você é um analista de sistemas especialista em modelagem de dados

Sua tarefa e analisar a descrição de um sistema e identificar:

1. Entidades principais
2. Atributos de cada entidade
2. Relações entre entidades
4. Cardinalidade das relações (1-para-1, 1-para-N, N-para-N)

Regras:

- Use nomes simples
- Entidades devem ser substantivos
- Não repita entidades
- Detecte relações implícitas

Formato de saída (JSON):

{{
 "entities":[
   {{
     "name":"entidade",
     "attributes":["atributo1","atributo2"]
   }}
 ],
 "relationships":[
   {{
     "from":"entidade",
     "to":"entidade",
     "type":"one-to-many"
   }}
 ]
}}

Descrição do sistema:

{description}

Retorne APENAS JSON
"""

        response = self.ask(prompt)
        return extract_json(response)

    def schema_generator(self, plan):

        prompt = f"""
Você é um arquiteto de banco de dados relacional.
Baseado no plano abaixo, crie um schema de banco normalizado.
Plano:

{json.dumps(plan, indent=2)}

Regras:

- Cada tabela deve ter chave primária
- Use INTEGER PRIMARY KEY para id
- Use TEXT para strings
- Crie chaves estrangeiras quando necessário
- Para relações N-para-N crie tabela intermediária
- Evite duplicação de dados

Formato de saída:

{{
 "tables":[
   {{
    "name":"tabela",
    "columns":[
      {{"name":"id","type":"INTEGER","pk":true}},
      {{"name":"campo","type":"TEXT"}}
    ],
    "foreign_keys":[
      {{"column":"campo_id","references":"outra_tabela.id"}}
    ]
   }}
 ]
}}

Retorne APENAS JSON
"""
        response = self.ask(prompt)

        return extract_json(response)

    def validate(self, schema):
        tables = {t["name"] for t in schema["tables"]}
        for t in schema["tables"]:
            if "columns" not in t:
                t["columns"] = []
            # garantir PK
            if not any(c.get("pk") for c in t["columns"]):
                t["columns"].insert(
                    0,
                    {"name": "id", "type": "INTEGER", "pk": True}
                )

            # validar foreign keys
            valid_fks = []

            for fk in t.get("foreign_keys", []):

                ref_table = fk["references"].split(".")[0]

                if ref_table in tables:
                    valid_fks.append(fk)

            t["foreign_keys"] = valid_fks

        return schema

    def build_database(self, schema):
        conn = sqlite3.connect("generated.db")
        cur = conn.cursor()
        for table in schema["tables"]:

            cols = []
            for col in table["columns"]:
                line = f'{col["name"]} {col["type"]}'

                if col.get("pk"):
                    line += " PRIMARY KEY"

                cols.append(line)

            for fk in table.get("foreign_keys", []):
                cols.append(
                    f'FOREIGN KEY({fk["column"]}) REFERENCES {fk["references"]}'
                )

            sql = f"""
CREATE TABLE IF NOT EXISTS {table['name']}(
{",".join(cols)}
);
"""

            cur.execute(sql)

        conn.commit()
        conn.close()

    def generate_api(self, schema):
        routes = ""
        for table in schema["tables"]:
            name = table["name"]
            routes += f"""

@app.get("/{name}")
def get_{name}():
    conn = sqlite3.connect("generated.db")
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM {name}").fetchall()
    conn.close()
    return rows
"""
        api_code = f"""
from fastapi import FastAPI
import sqlite3

app = FastAPI()

{routes}
"""
        with open("api.py", "w") as f:
            f.write(api_code)

    def build(self, description):
        print("\\nMontando sistema...\\n")
        plan = self.planner(description)
        print(json.dumps(plan, indent=2))
        schema = self.schema_generator(plan)
        print(json.dumps(schema, indent=2))

        schema = self.validate(schema)
        self.build_database(schema)
        self.generate_api(schema)
        print("\\nSistema criado com sucesso!")
        print("Banco:", "generated.db")
        print("API:", "api.py")
        print("\\nPara iniciar a API execute:")
        print("uvicorn api:app --reload")


# ---------------- MAIN ---------------- #

if __name__ == "__main__":

    desc = input("Descreva o sistema: ")
    ai = IaSystem()
    ai.build(desc)