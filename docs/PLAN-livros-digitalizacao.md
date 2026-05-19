# PLAN-livros-digitalizacao.md - Plano de Digitalização de Livros Verbum Dei

Este documento define o plano detalhado e as tarefas para a extração, tradução e integração completa dos 6 livros digitais (PDFs) no aplicativo de leitura.

---

## 📋 Visão Geral
* **Objetivo:** Adicionar toda a coleção de PDFs (6 livros) dentro do aplicativo de leitura em português brasileiro (pt-BR), organizados por capítulos de forma fluida e de alta performance.
* **Tipo do Projeto:** WEB (Vanilla HTML/CSS/JS Single-Page Reader Application)

---

## 🎯 Critérios de Sucesso
1. **Coleção Completa (6 Livros):** Todos os 6 arquivos PDF contidos na pasta `Conteúdo/` devem estar acessíveis no leitor, divididos em capítulos coerentes.
2. **Tradução e Qualidade:** 100% do conteúdo traduzido e revisado em português brasileiro, sem termos residuais em espanhol.
3. **Estética Kingdom & Performance:** O leitor deve renderizar o conteúdo em menos de 100ms, com tipografia majestosa, suporte total a modo noturno, redimensionamento de letras e menus colapsáveis (accordions) para listas longas.
4. **Persistência de Progresso:** O progresso de leitura (porcentagem e capítulo atual) de cada um dos 6 livros deve ser mantido de forma independente no `localStorage`.

---

## 🛠️ Stack Tecnológica
* **Frontend:** Vanilla HTML5, CSS3 moderno (Kingdom Theme), Vanilla ES6 JavaScript.
* **Banco de Dados local:** Arquivo estático `data.js` expondo a constante `BOOKS_DATABASE` (JSON compatível).
* **Pipeline de Digitalização:** Python 3.10+, bibliotecas `pdfminer.six` e processador personalizado de mapeamento de fontes.

---

## 📁 Estrutura de Arquivos Planejada
```
projects/verbum-dei-reader/
├── Conteúdo/
│   ├── 170 BOSQUEJOS DE JOSUE.pdf
│   ├── 30 DIAS DE ORACIÓN - VERSICULO DEL PENTATEUCO.pdf
│   ├── Codigo Divino.pdf
│   ├── GENESIS-EXPLICADO-VERSICULO-POR-VERSICULO.pdf
│   ├── EXODO-EXPLICADO-VERSICULO-POR-VERSICULO.pdf
│   └── LEVITICO-EXPLICADO-VERSICULO-POR-VERSICULO.pdf
├── docs/
│   └── PLAN-livros-digitalizacao.md           [NOVO] (Este arquivo)
├── test_stream.py
├── parse_books.py                             [NOVO] (Script de automação)
├── data.js                                    [MODIFICADO]
├── style.css                                  [MODIFICADO]
├── app.js                                     [MODIFICADO]
└── index.html
```

---

## 📝 Divisão de Tarefas (Task Breakdown)

### Fase 1: Análise e Scripting (P0 - Fundação)
- `[ ]` **TASK-1: Desenvolvimento do Parser Multi-PDF em Python**
  - **Agente:** `backend-specialist`
  - **Skills:** `python-patterns`, `clean-code`
  - **INPUT:** PDF files in `Conteúdo/` and font-decoding logic from `test_stream.py`.
  - **OUTPUT:** Functional `parse_books.py` script that can extract text from all 6 PDFs.
  - **VERIFY:** Run `python parse_books.py --dry-run` to print the chapter/outline count for each book.

- `[ ]` **TASK-2: Pipeline de Tradução Contextual e Conversão Teológica**
  - **Agente:** `backend-specialist`
  - **Skills:** `python-patterns`, `clean-code`
  - **INPUT:** Extracted raw text.
  - **OUTPUT:** Integration of a translation pipeline in `parse_books.py` using localized term mapping and translation models to generate clean, native pt-BR text.
  - **VERIFY:** Verify a sample output file `sample_translation.txt` to confirm no Spanish remains.

### Fase 2: Geração e Integração de Dados (P1 - Core)
- `[ ]` **TASK-3: Geração Automatizada de data.js**
  - **Agente:** `database-architect`
  - **Skills:** `database-design`
  - **INPUT:** Transcribed and translated content.
  - **OUTPUT:** Execution of `parse_books.py` to overwrite `data.js` with the 6 fully-populated books in correct JSON format.
  - **VERIFY:** Run `node -c projects/verbum-dei-reader/data.js` to ensure zero syntax errors in the database file.

### Fase 3: Aprimoramento e UX (P2 - UI/UX)
- `[ ]` **TASK-4: Implementação de Accordions e Estilos Especiais no CSS**
  - **Agente:** `frontend-specialist`
  - **Skills:** `frontend-design`, `ui-ux-pro-max`
  - **INPUT:** `style.css`.
  - **OUTPUT:** Add custom CSS styles for `.accordion-item`, `.accordion-header`, and `.accordion-content` with smooth micro-animations, custom scrollbars, and styled quotes.
  - **VERIFY:** Inspect CSS selectors for WCAG AA colors and ensure no purple/violet colors are introduced.

- `[ ]` **TASK-5: Lógica Interativa no app.js e Acessibilidade**
  - **Agente:** `frontend-specialist`
  - **Skills:** `nextjs-react-expert` (for pure DOM optimization)
  - **INPUT:** `app.js`.
  - **OUTPUT:** Update page rendering to support collapsible accordion sections for long chapters, and bind event handlers to expand/collapse items.
  - **VERIFY:** Ensure that clicking on a section expands it smoothly and toggles accessibility attributes (`aria-expanded`).

---

## 🏁 PHASE X: VERIFICAÇÃO FINAL
- [ ] Executar auditoria de UX: `python .agent/skills/frontend-design/scripts/ux_audit.py projects/verbum-dei-reader`
- [ ] Executar auditoria de Lint e Sintaxe: `node -c projects/verbum-dei-reader/data.js`
- [ ] Testar persistência de progresso local no `localStorage` do navegador para os 6 livros individualmente.
- [ ] Manual Check: Garantir que não existam trechos em espanhol e que todas as capas provisórias majestosas (lombo de livro) renderizem elegantemente.
