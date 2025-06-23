# 📊 Finanças em Movimento

[![MIT License](https://img.shields.io/github/license/seuusuario/financas-em-movimento.svg)](https://github.com/seuusuario/financas-em-movimento/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow.svg)](https://github.com/seuusuario/financas-em-movimento/projects)
[![Made with FastAPI](https://img.shields.io/badge/made%20with-FastAPI-00b386.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-336791.svg)](https://www.postgresql.org/)

---

**Finanças em Movimento** é um sistema moderno e completo de gestão financeira, administrativa e escoteira, projetado especialmente para associações, grupos escoteiros, clubes e organizações sociais. Com uma interface intuitiva e recursos poderosos, ele facilita o controle de mensalidades, contas, atividades, almoxarifado, certificados e muito mais.

## 🚀 Recursos Principais

- ✅ **Dashboard Financeiro Completo**
- 📅 **Calendário de Atividades**
- 🧾 **Gestão de Mensalidades**
- 💼 **Contas a Pagar e Receber**
- 📦 **Almoxarifado com Estoque**
- 🎓 **Certificados Customizáveis**
- 🧭 **Atividades Administrativas com Balanço**
- 🔐 **Acesso Seguro e Multiempresa**
- 📱 **Design Responsivo para Mobile**

## 🛠️ Tecnologias Utilizadas

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/)
- **Banco de Dados**: [PostgreSQL](https://www.postgresql.org/)
- **Frontend**: [Jinja2](https://jinja.palletsprojects.com/), [Tailwind CSS](https://tailwindcss.com/), [Alpine.js](https://alpinejs.dev/)
- **Outros**: FPDF, FullCalendar, JWT

## 🏗️ Estrutura do Projeto

```
app/
├── routers/           # Rotas da aplicação (módulos)
├── models/            # Modelos SQLAlchemy
├── templates/         # Templates Jinja2 com Tailwind
├── static/            # CSS, JS e imagens
├── services/          # Funções auxiliares
└── main.py            # Entrypoint do sistema
```

## ⚙️ Instalação

### Pré-requisitos

- Python 3.11+
- PostgreSQL 13+
- Git

### Passos

```bash
git clone https://github.com/seuusuario/financas-em-movimento.git
cd financas-em-movimento

python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows

pip install -r requirements.txt

cp .env.example .env  # Configure com suas credenciais
alembic upgrade head  # Aplica as migrações

uvicorn app.main:app --reload
```

## 📸 Capturas de Tela

*Adicione aqui links ou imagens reais hospedadas no GitHub ou em um CDN*

## 📌 Roadmap

- [x] Fluxo de caixa com gráficos
- [x] Geração de boletos com pyboleto
- [x] Certificados com controle automático
- [ ] Permissões avançadas por usuário
- [ ] Integração com Google Calendar
- [ ] Modo escuro automático
- [ ] Aplicativo mobile (WebView)

## 🤝 Contribuindo

1. Faça um fork
2. Crie sua branch: `git checkout -b feature/minha-funcionalidade`
3. Commit: `git commit -m 'feat: minha funcionalidade'`
4. Push: `git push origin feature/minha-funcionalidade`
5. Crie um Pull Request

## 📄 Licença

Este projeto está sob a [Licença MIT](LICENSE).

---

**Finanças em Movimento** – Transformando a gestão de associações com tecnologia, simplicidade e controle.
