AI Database Builder

A ideia foi montar um programa que recebe um prompt descrevendo um sistema (tipo "sistema de clínica veterinária", "sistema de loja", etc) e usar um modelo de linguagem rodando localmente para transformar essa descrição em tabelas, relações e um banco SQLite funcional.
Além disso, o programa também gera uma API simples automaticamente, permitindo acessar os dados sem precisar escrever código extra.
O projeto foi desenvolvido meio como experimento / trabalho prático, para testar até onde um modelo de linguagem rodando localmente consegue ajudar na criação de estruturas de software.
Durante o desenvolvimento também houve ajuda de ferramentas de IA para estruturar algumas partes do código e do pipeline, mas muita coisa precisou ser ajustada manualmente para funcionar de forma mais previsível.

Ideia geral

O programa basicamente:
1. recebe uma descrição de um sistema
2. usa uma LLM local para identificar entidades e relações
3. transforma isso em schema de banco de dados
4. cria um SQLite automaticamente
5. gera uma API simples baseada nas tabelas

Ou seja, em vez de escrever manualmente todas as tabelas, você descreve o sistema e o programa tenta montar a estrutura inicial.

Não substitui um projeto de banco feito manualmente, principalmente sistemas complecos, mas cria uma base.
Exemplo de uso

Você pode dar uma descrição como:

Sistema para pet shop.

Clientes possuem animais.
Veterinários realizam consultas.
Cada consulta possui data, diagnóstico e tratamento.

O programa tenta extrair algo parecido com:

- clientes
- animais
- veterinarios
- consultas

E criar relações entre eles
Depois disso ele gera:

generated.db
api.py

O projeto usa algumas ferramentas simples:

- llama-cpp-python para rodar localmente
- Deepseek como modelo de linguagem
- SQLite para banco de dados
- FastAPI para gerar uma API simples

Para evitar dependências muito pesadas, rodando em máquinas mais fracas
Uma preocupação foi tentar deixar tudo o mais leve.

Por isso:

- foi usado SQLite (não precisa servidor)
- o código é simples
- modelos quantizados podem rodar em CPU
- poucas dependências

Mesmo assim, rodar uma LLM local sempre depende da memória da máquina. Modelos menores funcionam melhor.

O projeto foi mantido simples:

ai_db_system.py
generated.db
api.py

ai_db_system.py
Script principal. Ele roda a llm, gera o schema e cria o banco.

generated.db
Banco SQLite gerado automaticamente.

api.py
Api simples criada com base nas tabelas detectadas.

Instalação

Instale as dependências:
pip install llama-cpp-python fastapi uvicorn
Depois coloque um modelo GGUF no projeto e configure o caminho no código.

Exemplo:
MODEL_PATH = "models/deepseek-coder-1.3b-instruct.Q4_K_M.gguf"
Executando
Basta rodar:
python ai_db_system.py

O programa vai pedir a descrição do sistema.
Depois que terminar ele cria o banco automaticamente.

Rodando a API
Para subir a API:
uvicorn api:app --reload
A API fica disponível em:
http://localhost:8000

Limitações

Como tudo depende de um modelo de linguagem podem acontecr:

- nomes de tabelas estranhos
- relações incompletas
- campos faltando
- JSON mal formatado

Por isso a saída deve ser analisada antes de usada.


Possíveis melhorias

- gerar CRUD automaticamente
- revisar schema antes de criar o banco
- gerar interface administrativa
- melhorar validação das relações
- suportar outros bancos além de SQLite


>>>>Esse projeto é mais um experimento para testar geração de estrutura de software com LLM local.
>>>>Ele não substitui modelagem manual de banco, mas já consegue criar uma base inicial razoável a partir de uma descrição simples.

>>>>>A ideia principal foi explorar como modelos de podem ajudar no processo de desenvolvimento, mesmo rodando localmente e sem infraestrutura pesada.
