import BOOKS_DATABASE from './data.js';

/**
 * VERBUM DEI - Sistema de Controle do E-Reader (Lógica SPA)
 * Controla navegação, renderização dinâmica de livros, progresso no localStorage e transições de tela.
 */

// 1. Estado da Aplicação (Single Source of Truth)
const state = {
  currentBook: null,
  currentChapterIndex: 0,
  currentPageIndex: 0,
  fontSizeClass: "font-size-md", // sm, md, lg, xl, xxl
  theme: "light", // light, dark
  progressData: {} // Estrutura: { "livro-id": { chapterIndex: X, pageIndex: Y, percent: Z } }
};

// 2. Inicialização ao Carregar a Página
function init() {
  initLocalStorage();
  renderLibrary();
  setupEventListeners();
  applyFontSize();
  applyTheme();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}

// 3. Gerenciamento de Persistência (localStorage)
function initLocalStorage() {
  const savedProgress = localStorage.getItem("verbum_dei_reader_progress");
  if (savedProgress) {
    try {
      state.progressData = JSON.parse(savedProgress);
    } catch (e) {
      console.error("Erro ao analisar progresso salvo, reiniciando dados:", e);
      state.progressData = {};
    }
  }
  
  const savedFontSize = localStorage.getItem("verbum_dei_reader_font_size");
  if (savedFontSize) {
    state.fontSizeClass = savedFontSize;
  }
  
  const savedTheme = localStorage.getItem("verbum_dei_reader_theme");
  if (savedTheme) {
    state.theme = savedTheme;
  } else {
    state.theme = "light"; // Creme de leitura confortável é o padrão
  }
}

// 3.1. Gerenciamento e Aplicação de Temas (Acessibilidade)
function applyTheme() {
  // Aplicar tema no elemento body
  document.body.classList.remove("theme-light", "theme-dark");
  document.body.classList.add(state.theme === "light" ? "theme-light" : "theme-dark");
  
  // Atualizar elementos e textos de controle de tema
  const libThemeBtn = document.getElementById("theme-toggle-library");
  const readerToggle = document.getElementById("btn-theme-toggle");
  
  if (state.theme === "light") {
    if (libThemeBtn) {
      libThemeBtn.innerHTML = `<span>🌙</span> Modo Noturno`;
    }
    if (readerToggle) {
      readerToggle.innerHTML = `<span>🌙</span> Modo Noturno`;
      readerToggle.setAttribute("aria-label", "Mudar para Modo Noturno");
    }
  } else {
    if (libThemeBtn) {
      libThemeBtn.innerHTML = `<span>☀️</span> Modo Claro`;
    }
    if (readerToggle) {
      readerToggle.innerHTML = `<span>☀️</span> Modo Claro`;
      readerToggle.setAttribute("aria-label", "Mudar para Modo Claro");
    }
  }
}

function toggleTheme() {
  state.theme = state.theme === "light" ? "dark" : "light";
  localStorage.setItem("verbum_dei_reader_theme", state.theme);
  applyTheme();
}

function saveProgressToStorage(bookId, chapterIndex, pageIndex) {
  // Calcular progresso plano
  const percent = calculateBookProgressPercentage(bookId, chapterIndex, pageIndex);
  
  state.progressData[bookId] = {
    chapterIndex,
    pageIndex,
    percent
  };
  
  localStorage.setItem("verbum_dei_reader_progress", JSON.stringify(state.progressData));
  
  // Atualiza visualmente o card correspondente na biblioteca em tempo de execução
  updateLibraryCardProgress(bookId, percent);
}

// 4. Cálculo do Progresso (Mapeamento Linear de Páginas)
function calculateBookProgressPercentage(bookId, chapterIndex, pageIndex) {
  const book = BOOKS_DATABASE.find(b => b.id === bookId);
  if (!book) return 0;
  
  let totalPages = 0;
  let pagesRead = 0;
  
  for (let c = 0; c < book.chapters.length; c++) {
    const chap = book.chapters[c];
    if (c < chapterIndex) {
      pagesRead += chap.pages.length;
    } else if (c === chapterIndex) {
      pagesRead += pageIndex; // Inclui até a página atual anterior
    }
    totalPages += chap.pages.length;
  }
  
  // Se o usuário chegou à última página do último capítulo, marcar como 100%
  const isLastChapter = chapterIndex === book.chapters.length - 1;
  const isLastPage = pageIndex === book.chapters[chapterIndex].pages.length - 1;
  if (isLastChapter && isLastPage) {
    return 100;
  }
  
  // Caso contrário, calcula proporcionalmente
  const progressPercent = Math.round((pagesRead / totalPages) * 100);
  // Garantir limite inferior de 5% se já começou, para dar feedback visual na barra
  return Math.max(progressPercent === 0 && (chapterIndex > 0 || pageIndex > 0) ? 5 : progressPercent, 0);
}

// 5. Renderizar Cartões de Livros na Biblioteca
function renderLibrary() {
  const grid = document.getElementById("books-grid");
  grid.innerHTML = ""; // Limpa grid existente
  
  BOOKS_DATABASE.forEach(book => {
    // Obter progresso salvo
    const saved = state.progressData[book.id];
    const percent = saved ? saved.percent : 0;
    const progressText = percent > 0 ? `${percent}% lido` : "Não iniciado";
    const buttonText = percent > 0 ? "Continuar Leitura" : "Iniciar Leitura";
    
    // Gerar HTML de capas provisórias refinadas com paleta e estilos premium se a imagem sumir
    const coverUrl = book.cover;
    
    // Criar cartão do livro com estrutura semântica
    const card = document.createElement("article");
    card.className = "book-card";
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", `Abrir livro ${book.title}`);
    card.innerHTML = `
      <div class="book-cover-container">
        <div class="book-cover-3d" style="background-image: linear-gradient(135deg, rgba(0,0,0,0.05), rgba(0,0,0,0.25)), url('${coverUrl}');">
          <!-- Fallback decorativo majestoso no estilo do lombo do livro se a capa não carregar -->
          <div style="position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: space-between; padding: 1.5rem 1rem; border: 1.5px solid var(--border-gold); background-color: var(--bg-surface); border-radius: 6px;">
            <div style="font-family: var(--font-sans); font-size: 0.75rem; color: var(--gold-primary); letter-spacing: 3px; font-weight: 800; text-transform: uppercase; text-align: center;">VERBUM DEI</div>
            <div style="font-family: var(--font-serif); font-size: 1.25rem; font-weight: 900; color: var(--txt-primary); text-align: center; line-height: 1.35;">${book.title}</div>
            <div style="font-family: var(--font-cursive); font-size: 1.25rem; color: var(--gold-primary); text-align: center;">${book.author}</div>
          </div>
        </div>
      </div>
      <div class="book-details">
        <span class="book-category">${book.category}</span>
        <h3 class="book-card-title">${book.title}</h3>
        <p class="book-card-desc">${book.description}</p>
        <div class="book-progress-wrapper">
          <div class="book-progress-info">
            <span>${progressText}</span>
            <span>${book.readingTime}</span>
          </div>
          <div class="book-progress-bar">
            <div id="progress-fill-${book.id}" class="book-progress-fill" style="width: ${percent}%"></div>
          </div>
        </div>
        <button class="btn-read-card" data-book-id="${book.id}">${buttonText}</button>
      </div>
    `;
    
    // Abrir leitor ao clicar no cartão ou no botão
    card.addEventListener("click", (e) => {
      // Impede clique duplo se clicado no botão dentro do cartão
      if (e.target.tagName !== "BUTTON") {
        openBook(book.id);
      }
    });
    
    const readBtn = card.querySelector(".btn-read-card");
    readBtn.addEventListener("click", () => {
      openBook(book.id);
    });
    
    grid.appendChild(card);
  });
}

function updateLibraryCardProgress(bookId, percent) {
  const fill = document.getElementById(`progress-fill-${bookId}`);
  if (fill) {
    fill.style.width = `${percent}%`;
    const label = fill.parentElement.previousElementSibling.firstElementChild;
    if (label) {
      label.textContent = `${percent}% lido`;
    }
  }
}

// 6. Navegador SPA: Abrir Livro e Carregar E-Reader
function openBook(bookId) {
  const book = BOOKS_DATABASE.find(b => b.id === bookId);
  if (!book) return;
  
  state.currentBook = book;
  
  // Carregar progresso salvo ou inicializar no começo
  const saved = state.progressData[bookId];
  if (saved) {
    state.currentChapterIndex = saved.chapterIndex;
    state.currentPageIndex = saved.pageIndex;
  } else {
    state.currentChapterIndex = 0;
    state.currentPageIndex = 0;
  }
  
  // Atualizar metadados do E-Reader
  document.getElementById("reader-book-title").textContent = book.title;
  
  // Renderizar sumário e página
  renderSidebarChapters();
  renderCurrentPage();
  
  // Transição suave de telas (SPA)
  switchScreen("library-screen", "reader-screen");
}

function closeBook() {
  state.currentBook = null;
  switchScreen("reader-screen", "library-screen");
  
  // Recarrega biblioteca para refletir mudanças atualizadas de progresso
  renderLibrary();
}

function switchScreen(fromId, toId) {
  const fromScreen = document.getElementById(fromId);
  const toScreen = document.getElementById(toId);
  
  // Ocultar tela de saída com efeito físico
  fromScreen.classList.remove("active");
  
  // Exibir e deslizar tela de entrada
  setTimeout(() => {
    toScreen.classList.add("active");
    // Voltar rolagem para o topo
    toScreen.scrollTop = 0;
  }, 200); // Aguarda fade-out da tela anterior
}

// 7. Renderização do E-Reader (Conteúdo e Paginação)
function renderCurrentPage() {
  if (!state.currentBook) return;
  
  const book = state.currentBook;
  const chapter = book.chapters[state.currentChapterIndex];
  const pageContent = chapter.pages[state.currentPageIndex];
  
  // 1. Atualizar Título do Capítulo Barra Superior
  document.getElementById("reader-chapter-indicator").textContent = chapter.title;
  
  // 2. Renderizar conteúdo rico da página na caixa
  const contentBox = document.getElementById("reader-page-content");
  contentBox.innerHTML = pageContent;
  contentBox.scrollTop = 0; // Reseta rolagem do texto para o topo
  
  // 3. Atualizar Indicador de Páginas Inferior
  const totalPagesInChapter = chapter.pages.length;
  document.getElementById("reader-page-indicator").textContent = `Página ${state.currentPageIndex + 1} de ${totalPagesInChapter}`;
  
  // 4. Habilitar/Desabilitar botões de paginação inferior
  const isFirstChapter = state.currentChapterIndex === 0;
  const isFirstPage = state.currentPageIndex === 0;
  const isLastChapter = state.currentChapterIndex === book.chapters.length - 1;
  const isLastPage = state.currentPageIndex === chapter.pages.length - 1;
  
  document.getElementById("btn-page-prev").disabled = isFirstChapter && isFirstPage;
  document.getElementById("btn-page-prev-side").disabled = isFirstChapter && isFirstPage;
  
  document.getElementById("btn-page-next").disabled = isLastChapter && isLastPage;
  document.getElementById("btn-page-next-side").disabled = isLastChapter && isLastPage;
  
  // 5. Atualizar Barra de Progresso Superior
  const percent = calculateBookProgressPercentage(book.id, state.currentChapterIndex, state.currentPageIndex);
  document.getElementById("reader-progress-bar").style.width = `${percent}%`;
  
  // 6. Atualizar item ativo no sumário
  updateSidebarActiveItem();
  
  // 7. Salvar progresso no armazenamento
  saveProgressToStorage(book.id, state.currentChapterIndex, state.currentPageIndex);
}

// 8. Navegação de Páginas (Avançar e Retroceder)
function navigatePage(direction) {
  if (!state.currentBook) return;
  
  const book = state.currentBook;
  const chapter = book.chapters[state.currentChapterIndex];
  
  if (direction === "next") {
    // Avançar página dentro do capítulo
    if (state.currentPageIndex < chapter.pages.length - 1) {
      state.currentPageIndex++;
      renderCurrentPage();
    } 
    // Avançar para próximo capítulo
    else if (state.currentChapterIndex < book.chapters.length - 1) {
      state.currentChapterIndex++;
      state.currentPageIndex = 0;
      renderCurrentPage();
    }
  } else if (direction === "prev") {
    // Voltar página dentro do capítulo
    if (state.currentPageIndex > 0) {
      state.currentPageIndex--;
      renderCurrentPage();
    } 
    // Voltar para página final do capítulo anterior
    else if (state.currentChapterIndex > 0) {
      state.currentChapterIndex--;
      const prevChapter = book.chapters[state.currentChapterIndex];
      state.currentPageIndex = prevChapter.pages.length - 1;
      renderCurrentPage();
    }
  }
}

// 9. Lógica do Sumário Lateral (Sidebar)
function renderSidebarChapters() {
  if (!state.currentBook) return;
  
  const book = state.currentBook;
  const list = document.getElementById("sidebar-chapters-list");
  list.innerHTML = "";
  
  book.chapters.forEach((chap, idx) => {
    const item = document.createElement("li");
    item.className = "chapter-item";
    item.setAttribute("data-chapter-idx", idx);
    
    // Obter quantidade de páginas
    const pCount = chap.pages.length;
    
    item.innerHTML = `
      <div class="chapter-item-title">${chap.title}</div>
      <div class="chapter-item-progress">${pCount} ${pCount === 1 ? 'página' : 'páginas'}</div>
    `;
    
    item.addEventListener("click", () => {
      state.currentChapterIndex = idx;
      state.currentPageIndex = 0;
      renderCurrentPage();
      closeSidebar();
    });
    
    list.appendChild(item);
  });
}

function updateSidebarActiveItem() {
  const items = document.querySelectorAll(".chapter-item");
  items.forEach(item => {
    const idx = parseInt(item.getAttribute("data-chapter-idx"), 10);
    if (idx === state.currentChapterIndex) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });
}

function openSidebar() {
  document.getElementById("reader-sidebar").classList.add("open");
  document.getElementById("reader-sidebar-overlay").classList.add("active");
}

function closeSidebar() {
  document.getElementById("reader-sidebar").classList.remove("open");
  document.getElementById("reader-sidebar-overlay").classList.remove("active");
}

// 10. Controle Dinâmico do Tamanho de Fonte
function changeFontSize(action) {
  const sizes = ["font-size-sm", "font-size-md", "font-size-lg", "font-size-xl", "font-size-xxl"];
  let currentIdx = sizes.indexOf(state.fontSizeClass);
  
  if (action === "increase" && currentIdx < sizes.length - 1) {
    currentIdx++;
  } else if (action === "decrease" && currentIdx > 0) {
    currentIdx--;
  }
  
  state.fontSizeClass = sizes[currentIdx];
  applyFontSize();
  
  // Salva preferência do usuário de acessibilidade
  localStorage.setItem("verbum_dei_reader_font_size", state.fontSizeClass);
}
 
function applyFontSize() {
  const readerScreen = document.getElementById("reader-screen");
  
  // Limpar classes antigas de fonte
  readerScreen.classList.remove("font-size-sm", "font-size-md", "font-size-lg", "font-size-xl", "font-size-xxl");
  // Aplicar nova classe
  readerScreen.classList.add(state.fontSizeClass);
}

// 11. Registrar Event Listeners do E-Reader
function setupEventListeners() {
  // Voltar à Biblioteca
  document.getElementById("btn-back-to-library").addEventListener("click", closeBook);
  
  // Alternância de Tema Claro/Escuro
  const libThemeBtn = document.getElementById("theme-toggle-library");
  if (libThemeBtn) {
    libThemeBtn.addEventListener("click", toggleTheme);
  }
  
  const readerThemeBtn = document.getElementById("btn-theme-toggle");
  if (readerThemeBtn) {
    readerThemeBtn.addEventListener("click", toggleTheme);
  }
  
  // Paginação de Páginas
  document.getElementById("btn-page-prev").addEventListener("click", () => navigatePage("prev"));
  document.getElementById("btn-page-prev-side").addEventListener("click", () => navigatePage("prev"));
  document.getElementById("btn-page-next").addEventListener("click", () => navigatePage("next"));
  document.getElementById("btn-page-next-side").addEventListener("click", () => navigatePage("next"));
  
  // Controles de Fonte
  document.getElementById("btn-text-decrease").addEventListener("click", () => changeFontSize("decrease"));
  document.getElementById("btn-text-increase").addEventListener("click", () => changeFontSize("increase"));
  
  // Sidebar Sumário Toggle
  document.getElementById("btn-toggle-sidebar").addEventListener("click", openSidebar);
  document.getElementById("btn-close-sidebar").addEventListener("click", closeSidebar);
  document.getElementById("reader-sidebar-overlay").addEventListener("click", closeSidebar);
  
  // Navegação por teclado (Acessibilidade)
  document.addEventListener("keydown", (e) => {
    // Apenas responde se o leitor estiver ativo
    if (!state.currentBook) return;
    
    if (e.key === "ArrowLeft") {
      navigatePage("prev");
    } else if (e.key === "ArrowRight") {
      navigatePage("next");
    } else if (e.key === "Escape") {
      closeSidebar();
    }
  });

  // Suporte a gestos de deslizar para mobile (Swiping)
  let touchStartX = 0;
  let touchEndX = 0;
  const contentBox = document.getElementById("reader-page-content");

  contentBox.addEventListener("touchstart", (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  contentBox.addEventListener("touchend", (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipeGesture();
  }, { passive: true });

  function handleSwipeGesture() {
    const swipeThreshold = 55; // pixels mínimos de arraste
    if (touchStartX - touchEndX > swipeThreshold) {
      // Deslizou para a esquerda -> Avançar página
      navigatePage("next");
    } else if (touchEndX - touchStartX > swipeThreshold) {
      // Deslizou para a direita -> Voltar página
      navigatePage("prev");
    }
  }

  // Lógica de acordeão para os esboços de Josué (cards expansíveis)
  contentBox.addEventListener("click", (e) => {
    // Detecta clique no cabeçalho ou em elementos dentro do cabeçalho
    const header = e.target.closest(".outline-header");
    if (!header) return;
    
    const card = header.closest(".outline-card");
    if (!card) return;
    
    // Evita propagação ou comportamento indesejado se clicar em texto selecionável
    const selection = window.getSelection().toString();
    if (selection) return;

    const isExpanded = card.classList.contains("expanded");
    
    // Opcional: Se quiser fechar os outros cartões quando um for aberto, descomente abaixo:
    /*
    document.querySelectorAll(".outline-card.expanded").forEach(c => {
      if (c !== card) {
        c.classList.remove("expanded");
      }
    });
    */
    
    if (isExpanded) {
      card.classList.remove("expanded");
    } else {
      card.classList.add("expanded");
    }
  });
}
