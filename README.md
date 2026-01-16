# arXiv → Discord
Este repositório contém um **runner em Python** que busca artigos no **arXiv** a partir de um arquivo YAML de tópicos/querys e publica diariamente no **Discord** via **Webhook**.

## 1) Setup
1. Baixe/clone este repositório com todo o código-fonte (inclusive os arquivos da pasta .github/workflows).
2. Suba o código em um **novo repositório** (GitHub) em que você é dono.

<img width="568" height="139" alt="image" src="https://github.com/user-attachments/assets/46935c34-9eec-4524-8109-789223a56d3d" />

## 2) Bind das variáveis
Em cada tópico no arquivo YML (topics/hep.yml), contém a query de busca a ser executada (arvix_url) e existe uma variável de ambiente que contém a URL (`webhook_env`) para onde enviar a mensagem no Discord.
<img width="1271" height="152" alt="image" src="https://github.com/user-attachments/assets/24e0199b-5f7f-4332-b37e-39dadf2e2941" />

### **No Discord: para obter o valor desta variável (URL) do post:**

### **Selecione um Canal de destino e acesse as configurações deste canal em Settings:**
<img width="380" height="51" alt="image" src="https://github.com/user-attachments/assets/3215b6d8-578c-4012-a7c7-ff61bf22e1e6" />

### **Em Settings, clique em Integrations:**
<img width="272" height="187" alt="image" src="https://github.com/user-attachments/assets/d5d6e938-0fde-405b-9727-ebed44bc9108" />

### **Crie um webhook em New Webhook e copie a URL em Copy Webhook URL:**
<img width="747" height="94" alt="image" src="https://github.com/user-attachments/assets/e60bfbbe-6c7e-41fd-871a-0564a805063b" />
<img width="703" height="355" alt="image" src="https://github.com/user-attachments/assets/de0dd352-429c-4bf3-8845-a60d8ea9f87d" />

### **Nas configurações do GitHub Repository (Settings) para criar uma secret com a URL destino do post.**

### **Selecione Settings**
<img width="1098" height="130" alt="image" src="https://github.com/user-attachments/assets/0b3b4f4d-30ec-4cd5-97fa-d0102cf11e5d" />

### **Selecione Secrets and Variables e depois Actions**
<img width="364" height="150" alt="image" src="https://github.com/user-attachments/assets/87fedf6b-c0b0-4b9d-ae57-f19ea0895da6" />

### **Crie uma Repository Secrets**
<img width="941" height="231" alt="image" src="https://github.com/user-attachments/assets/12a48ae3-b40c-4d36-9f12-948a001f2e37" />

### **Agora no runner (.github/workflows/check_new_papers.yml) informe o nome dessa secret**
<img width="815" height="320" alt="image" src="https://github.com/user-attachments/assets/2520d651-5ef1-4f25-bba0-2391621221a7" />

### **E informe para o topico o valor da variável que recebeu a secret (URL)**
**topics/topic.yml:** <img width="1190" height="150" alt="image" src="https://github.com/user-attachments/assets/a6425669-3963-4016-8ddf-7e741c9d51ae" />

## 3) Query
<img width="479" height="349" alt="image" src="https://github.com/user-attachments/assets/6537fb75-c33d-49ed-9b26-e6c9a4293f3f" />

## 4) Tópico
Para incluir um novo tópico, criar um novo step no workflow com a mesma estrutura do anterior, informando as secrets utilizadas e passando o novo tópico como parâmetro para o runner.py.

<img width="893" height="343" alt="image" src="https://github.com/user-attachments/assets/ce736f07-f719-43f3-a61d-97ad48fa376e" />

