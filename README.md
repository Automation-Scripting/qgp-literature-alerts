
# arXiv → Discord

This repository contains a **Python runner** that fetches articles from **arXiv** based on a YAML file of topics/queries and publishes them daily to **Discord** via **Webhook**.

---

## Index

1.[Setup](#1-setup)
2.[Variable binding](#2-variable-binding)
3.[Query](#3-query)
4.[Topic](#4-topic)
5.[Report](#5-report)

---

## 1) Setup

1. Download/clone this repository with the full source code (including the files inside the `.github/workflows` folder).
2. Push the code to a **new repository** (GitHub) that you own.

---

## 2) Variable binding

Each topic in the YML file (e.g. `topics/hep.yml`) contains:

- The query to be executed: `arxiv_url`
- The environment variable name that holds the Discord webhook URL: `webhook_env`

This variable determines **where** the message will be sent on Discord.

---

### On Discord: how to obtain the value of this variable (post URL)

1. Select the destination channel.
2. Open **Settings**.
3. Go to **Integrations**.
4. Click **New Webhook**.
5. Copy the value from **Copy Webhook URL**.

This URL is the value that must be stored as a GitHub secret.

---

### On GitHub: create a secret with the destination post URL

1. Go to your repository **Settings**.
2. Open **Secrets and variables** → **Actions**.
3. Click **New repository secret**.
4. Set the **name** of the secret to match the value used in `webhook_env`.
5. Set the **value** of the secret to the Discord webhook URL.

---

### Bind the secret in the workflow

In the workflow file:

.github/workflows/check_new_papers.yml

Make sure the secret is exposed as an environment variable.

---

### Bind the variable to the topic

In your topic file (e.g. `topics/topic.yml`), set:

- `webhook_env` = name of the environment variable that contains the secret

---

## 3) Query

Each topic defines its own arXiv query using the `arxiv_url` field.

This is a **direct query** to the arXiv Atom API and is consumed **as-is** by the runner.

No transformation or validation is performed by the system.

---

## 4) Topic

To add a new topic:

1. Create a new step in the workflow.
2. Use the same structure as the existing steps.
3. Declare the required secrets.
4. Pass the new topic as a parameter to `runner.py`.

---

## 5) Report

A detailed execution report can be found under:

**GitHub → Actions → arXiv → Discord workflow**

Each run prints:
- Fetched articles
- Filtered articles
- Posted messages
- Errors (if any)

---

> **Rule of thumb:**  
> If the query is wrong, the system is wrong.  
> If the variable binding is wrong, nothing will be posted.

# arXiv → Discord
This repository contains a **Python runner** that fetches articles from **arXiv** based on a YAML file of topics/queries and publishes them daily to **Discord** via **Webhook**.

---
## Index

- [Setup](#1-setup)
- [Variable binding](#2-variable-binding)
- [Query](#3-query)
- [Topic](#4-topic)
- [Report](#5-report)
  
## 1) Setup
1. Download/clone this repository with the full source code (including the files inside the `.github/workflows` folder).
2. Push the code to a **new repository** (GitHub) that you own.

<img width="568" height="139" alt="image" src="https://github.com/user-attachments/assets/46935c34-9eec-4524-8109-789223a56d3d" />

## 2) Variable binding

Each topic in the YML file (e.g. `topics/hep.yml`) contains:

- The query to be executed: `arxiv_url`
- The environment variable name that holds the Discord webhook URL: `webhook_env`

This variable determines **where** the message will be sent on Discord.

<img width="1271" height="152" alt="image" src="https://github.com/user-attachments/assets/24e0199b-5f7f-4332-b37e-39dadf2e2941" />

---

### On Discord: how to obtain the value of this variable (post URL)

1. Select the destination channel.
2. Open **Settings**.
3. Go to **Integrations**.
4. Click **New Webhook**.
5. Copy the value from **Copy Webhook URL**.

This URL is the value that must be stored as a GitHub secret.

### **1:**
<img width="380" height="51" alt="image" src="https://github.com/user-attachments/assets/3215b6d8-578c-4012-a7c7-ff61bf22e1e6" />

### **2:**
<img width="272" height="187" alt="image" src="https://github.com/user-attachments/assets/d5d6e938-0fde-405b-9727-ebed44bc9108" />

### **3:**
<img width="747" height="94" alt="image" src="https://github.com/user-attachments/assets/e60bfbbe-6c7e-41fd-871a-0564a805063b" />

### **4:**
<img width="703" height="355" alt="image" src="https://github.com/user-attachments/assets/de0dd352-429c-4bf3-8845-a60d8ea9f87d" />

---

### On GitHub: create a secret with the destination post URL

1. Go to your repository **Settings**.
2. Open **Secrets and variables** → **Actions**.
3. Click **New repository secret**.
4. Set the **name** of the secret to match the value used in `webhook_env`.
5. Set the **value** of the secret to the Discord webhook URL.

### **1:**
<img width="1098" height="130" alt="image" src="https://github.com/user-attachments/assets/0b3b4f4d-30ec-4cd5-97fa-d0102cf11e5d" />

### **2:**
<img width="364" height="150" alt="image" src="https://github.com/user-attachments/assets/87fedf6b-c0b0-4b9d-ae57-f19ea0895da6" />

### **3:**
<img width="941" height="231" alt="image" src="https://github.com/user-attachments/assets/12a48ae3-b40c-4d36-9f12-948a001f2e37" />


### Bind the secret in the workflow

In the workflow file:

.github/workflows/check_new_papers.yml

Make sure the secret is exposed as an environment variable.

---
### -> **4 (.github/workflows/check_new_papers.yml): **
<img width="815" height="320" alt="image" src="https://github.com/user-attachments/assets/2520d651-5ef1-4f25-bba0-2391621221a7" />

### **E informe para o topico o valor da variável que recebeu a secret (URL)**
**topics/topic.yml:** <img width="1190" height="150" alt="image" src="https://github.com/user-attachments/assets/a6425669-3963-4016-8ddf-7e741c9d51ae" />

## 3) Query
<img width="479" height="349" alt="image" src="https://github.com/user-attachments/assets/6537fb75-c33d-49ed-9b26-e6c9a4293f3f" />

## 4) Tópico
Para incluir um novo tópico, criar um novo step no workflow com a mesma estrutura do anterior, informando as secrets utilizadas e passando o novo tópico como parâmetro para o runner.py.

<img width="893" height="343" alt="image" src="https://github.com/user-attachments/assets/ce736f07-f719-43f3-a61d-97ad48fa376e" />

## 5) Relatório

### Um relatório detalhado com a busca pode ser acessado em Action, depois em "arXiv -> Discord workflow".

<img width="1020" height="672" alt="image" src="https://github.com/user-attachments/assets/f3fcd50a-695e-4200-b6a0-ece44a385d01" />

<img width="1004" height="541" alt="image" src="https://github.com/user-attachments/assets/2f4bba2e-fc4a-4158-aed5-f639d76e815b" />

