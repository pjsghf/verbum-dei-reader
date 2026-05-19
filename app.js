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
  progressData: {}, // Estrutura: { "livro-id": { chapterIndex: X, pageIndex: Y, percent: Z } }
  bookmarksData: {}, // Estrutura: { "bookId-chapIndex-pageIndex": { bookId, chapterIndex, pageIndex, bookTitle, chapTitle } }
  notesData: {} // Estrutura: { "bookId-chapIndex-pageIndex": { text, bookId, chapterIndex, pageIndex, bookTitle, chapTitle, updatedAt } }
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
  
  const savedBookmarks = localStorage.getItem("verbum_dei_reader_bookmarks");
  if (savedBookmarks) {
    try {
      state.bookmarksData = JSON.parse(savedBookmarks);
    } catch (e) {
      console.error("Erro ao analisar favoritos salvos:", e);
      state.bookmarksData = {};
    }
  }
  
  const savedNotes = localStorage.getItem("verbum_dei_reader_notes");
  if (savedNotes) {
    try {
      state.notesData = JSON.parse(savedNotes);
    } catch (e) {
      console.error("Erro ao analisar anotações salvas:", e);
      state.notesData = {};
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
  const libThemeBtn = document.getElementById("btn-theme-toggle-library");
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
  // Atualiza as estatísticas no painel antes de renderizar
  updateLibraryStats();
  
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
  
  // 6.1. Atualizar favoritos e notas no leitor
  updateBookmarkUI();
  updateNoteUI();
  
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
  const libThemeBtn = document.getElementById("btn-theme-toggle-library");
  if (libThemeBtn) {
    libThemeBtn.addEventListener("click", toggleTheme);
  }
  
  const readerThemeBtn = document.getElementById("btn-theme-toggle");
  if (readerThemeBtn) {
    readerThemeBtn.addEventListener("click", toggleTheme);
  }
  
  // Favoritos
  const toggleBookmarkBtn = document.getElementById("btn-toggle-bookmark");
  if (toggleBookmarkBtn) {
    toggleBookmarkBtn.addEventListener("click", toggleBookmark);
  }
  
  // Anotações
  const addNoteBtn = document.getElementById("btn-add-note");
  if (addNoteBtn) {
    addNoteBtn.addEventListener("click", openNoteModal);
  }
  
  const closeNoteModalBtn = document.getElementById("btn-close-note-modal");
  if (closeNoteModalBtn) {
    closeNoteModalBtn.addEventListener("click", closeNoteModal);
  }
  
  const noteModalOverlay = document.getElementById("note-modal-overlay");
  if (noteModalOverlay) {
    noteModalOverlay.addEventListener("click", closeNoteModal);
  }
  
  const deleteNoteBtn = document.getElementById("btn-delete-note");
  if (deleteNoteBtn) {
    deleteNoteBtn.addEventListener("click", deleteNote);
  }
  
  const saveNoteBtn = document.getElementById("btn-save-note");
  if (saveNoteBtn) {
    saveNoteBtn.addEventListener("click", saveNote);
  }
  
  // Abas do Sumário
  const tabChapters = document.getElementById("tab-chapters");
  if (tabChapters) {
    tabChapters.addEventListener("click", () => switchSidebarTab("chapters"));
  }
  
  const tabSaved = document.getElementById("tab-saved");
  if (tabSaved) {
    tabSaved.addEventListener("click", () => switchSidebarTab("saved"));
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

// ==========================================================================
// 12. Lógica das Estatísticas da Biblioteca
// ==========================================================================
function updateLibraryStats() {
  const totalBooks = BOOKS_DATABASE.length;
  let totalProgress = 0;
  let completedCount = 0;
  
  BOOKS_DATABASE.forEach(book => {
    const saved = state.progressData[book.id];
    if (saved) {
      totalProgress += saved.percent || 0;
      if (saved.percent === 100) {
        completedCount++;
      }
    }
  });
  
  const avgProgress = totalBooks > 0 ? Math.round(totalProgress / totalBooks) : 0;
  const bookmarksCount = Object.keys(state.bookmarksData).length;
  const notesCount = Object.keys(state.notesData).length;
  
  const progressEl = document.getElementById("stat-total-progress");
  if (progressEl) progressEl.textContent = `${avgProgress}%`;
  
  const completedEl = document.getElementById("stat-books-completed");
  if (completedEl) completedEl.textContent = `${completedCount}/${totalBooks}`;
  
  const bookmarksEl = document.getElementById("stat-bookmarks-count");
  if (bookmarksEl) bookmarksEl.textContent = bookmarksCount;
  
  const notesEl = document.getElementById("stat-notes-count");
  if (notesEl) notesEl.textContent = notesCount;
}

// ==========================================================================
// 13. Helpers e Lógica de Favoritos (Bookmarks)
// ==========================================================================
function getPageKey(bookId, chapIndex, pageIndex) {
  return `${bookId}-${chapIndex}-${pageIndex}`;
}

function toggleBookmark() {
  if (!state.currentBook) return;
  
  const bookId = state.currentBook.id;
  const chapIndex = state.currentChapterIndex;
  const pageIndex = state.currentPageIndex;
  const key = getPageKey(bookId, chapIndex, pageIndex);
  
  if (state.bookmarksData[key]) {
    delete state.bookmarksData[key];
  } else {
    const bookTitle = state.currentBook.title;
    const chapTitle = state.currentBook.chapters[chapIndex].title;
    state.bookmarksData[key] = {
      bookId,
      chapterIndex: chapIndex,
      pageIndex,
      bookTitle,
      chapTitle
    };
  }
  
  localStorage.setItem("verbum_dei_reader_bookmarks", JSON.stringify(state.bookmarksData));
  
  updateBookmarkUI();
  renderBookmarksList();
  updateLibraryStats();
}

function updateBookmarkUI() {
  if (!state.currentBook) return;
  
  const key = getPageKey(state.currentBook.id, state.currentChapterIndex, state.currentPageIndex);
  const isBookmarked = !!state.bookmarksData[key];
  
  const icon = document.getElementById("bookmark-status-icon");
  const text = document.getElementById("bookmark-status-text");
  const btn = document.getElementById("btn-toggle-bookmark");
  
  if (icon) {
    icon.textContent = isBookmarked ? "★" : "☆";
  }
  if (text) {
    text.textContent = isBookmarked ? "Favoritada" : "Favoritar Página";
  }
  if (btn) {
    if (isBookmarked) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  }
}

function renderBookmarksList() {
  const list = document.getElementById("bookmarks-list");
  if (!list) return;
  
  list.innerHTML = "";
  
  if (!state.currentBook) return;
  const bookId = state.currentBook.id;
  
  const bookmarkedKeys = Object.keys(state.bookmarksData).filter(key => key.startsWith(`${bookId}-`));
  
  if (bookmarkedKeys.length === 0) {
    list.innerHTML = `<li class="saved-empty-msg">Nenhum favorito salvo nesta leitura.</li>`;
    return;
  }
  
  bookmarkedKeys.sort((a, b) => {
    const partA = a.split("-");
    const partB = b.split("-");
    const chapA = parseInt(partA[1], 10);
    const chapB = parseInt(partB[1], 10);
    if (chapA !== chapB) return chapA - chapB;
    const pageA = parseInt(partA[2], 10);
    const pageB = parseInt(partB[2], 10);
    return pageA - pageB;
  });
  
  bookmarkedKeys.forEach(key => {
    const fav = state.bookmarksData[key];
    const item = document.createElement("li");
    item.className = "saved-item";
    
    item.innerHTML = `
      <div class="saved-item-info">
        <div class="saved-item-title">${fav.chapTitle}</div>
        <div class="saved-item-meta">Pág. ${fav.pageIndex + 1}</div>
      </div>
      <button class="saved-item-delete-btn" aria-label="Remover favorito" data-key="${key}">×</button>
    `;
    
    item.querySelector(".saved-item-info").addEventListener("click", () => {
      state.currentChapterIndex = fav.chapterIndex;
      state.currentPageIndex = fav.pageIndex;
      renderCurrentPage();
      closeSidebar();
    });
    
    item.querySelector(".saved-item-delete-btn").addEventListener("click", (e) => {
      e.stopPropagation();
      delete state.bookmarksData[key];
      localStorage.setItem("verbum_dei_reader_bookmarks", JSON.stringify(state.bookmarksData));
      updateBookmarkUI();
      renderBookmarksList();
      updateLibraryStats();
    });
    
    list.appendChild(item);
  });
}

// ==========================================================================
// 14. Lógica de Anotações com Auto-Salvamento (Opção A)
// ==========================================================================
function openNoteModal() {
  if (!state.currentBook) return;
  
  const bookId = state.currentBook.id;
  const chapIndex = state.currentChapterIndex;
  const pageIndex = state.currentPageIndex;
  const key = getPageKey(bookId, chapIndex, pageIndex);
  
  const modal = document.getElementById("note-modal");
  const textarea = document.getElementById("note-textarea");
  const deleteBtn = document.getElementById("btn-delete-note");
  
  if (modal) {
    modal.classList.add("open");
  }
  
  if (state.notesData[key]) {
    if (textarea) textarea.value = state.notesData[key].text;
    if (deleteBtn) deleteBtn.style.display = "block";
  } else {
    if (textarea) textarea.value = "";
    if (deleteBtn) deleteBtn.style.display = "none";
  }
  
  if (textarea) {
    textarea.focus();
  }
}

function closeNoteModal() {
  const modal = document.getElementById("note-modal");
  if (!modal || !modal.classList.contains("open")) return;
  
  // Opção A: Auto-salvar alterações ao fechar pelo overlay ou botão X
  if (state.currentBook) {
    const bookId = state.currentBook.id;
    const chapIndex = state.currentChapterIndex;
    const pageIndex = state.currentPageIndex;
    const key = getPageKey(bookId, chapIndex, pageIndex);
    
    const textarea = document.getElementById("note-textarea");
    const currentText = textarea ? textarea.value.trim() : "";
    const savedNote = state.notesData[key];
    const savedText = savedNote ? savedNote.text.trim() : "";
    
    if (currentText !== savedText) {
      if (currentText === "") {
        if (savedNote) {
          delete state.notesData[key];
          localStorage.setItem("verbum_dei_reader_notes", JSON.stringify(state.notesData));
        }
      } else {
        const bookTitle = state.currentBook.title;
        const chapTitle = state.currentBook.chapters[chapIndex].title;
        state.notesData[key] = {
          text: currentText,
          bookId,
          chapterIndex: chapIndex,
          pageIndex,
          bookTitle,
          chapTitle,
          updatedAt: new Date().toISOString()
        };
        localStorage.setItem("verbum_dei_reader_notes", JSON.stringify(state.notesData));
      }
      
      updateNoteUI();
      renderNotesList();
      updateLibraryStats();
    }
  }
  
  modal.classList.remove("open");
  const textarea = document.getElementById("note-textarea");
  if (textarea) {
    textarea.value = "";
  }
}

function saveNote() {
  if (!state.currentBook) return;
  
  const bookId = state.currentBook.id;
  const chapIndex = state.currentChapterIndex;
  const pageIndex = state.currentPageIndex;
  const key = getPageKey(bookId, chapIndex, pageIndex);
  
  const textarea = document.getElementById("note-textarea");
  const text = textarea ? textarea.value.trim() : "";
  
  if (!text) {
    deleteNote();
    return;
  }
  
  const bookTitle = state.currentBook.title;
  const chapTitle = state.currentBook.chapters[chapIndex].title;
  
  state.notesData[key] = {
    text,
    bookId,
    chapterIndex: chapIndex,
    pageIndex,
    bookTitle,
    chapTitle,
    updatedAt: new Date().toISOString()
  };
  
  localStorage.setItem("verbum_dei_reader_notes", JSON.stringify(state.notesData));
  
  // Limpar campo temporariamente para evitar duplo salvamento no encerramento do modal
  if (textarea) textarea.value = text;
  
  closeNoteModal();
  updateNoteUI();
  renderNotesList();
  updateLibraryStats();
}

function deleteNote() {
  if (!state.currentBook) return;
  
  const bookId = state.currentBook.id;
  const chapIndex = state.currentChapterIndex;
  const pageIndex = state.currentPageIndex;
  const key = getPageKey(bookId, chapIndex, pageIndex);
  
  if (state.notesData[key]) {
    delete state.notesData[key];
    localStorage.setItem("verbum_dei_reader_notes", JSON.stringify(state.notesData));
  }
  
  // Limpar campo para evitar re-salvar no fechamento automático
  const textarea = document.getElementById("note-textarea");
  if (textarea) textarea.value = "";
  
  closeNoteModal();
  updateNoteUI();
  renderNotesList();
  updateLibraryStats();
}

function updateNoteUI() {
  if (!state.currentBook) return;
  
  const key = getPageKey(state.currentBook.id, state.currentChapterIndex, state.currentPageIndex);
  const hasNote = !!state.notesData[key];
  
  const btn = document.getElementById("btn-add-note");
  const textSpan = btn ? btn.querySelector(".note-text") : null;
  
  if (btn) {
    if (hasNote) {
      btn.classList.add("active");
      if (textSpan) textSpan.textContent = "Editar Nota";
    } else {
      btn.classList.remove("active");
      if (textSpan) textSpan.textContent = "Anotação";
    }
  }
}

function renderNotesList() {
  const list = document.getElementById("notes-list");
  if (!list) return;
  
  list.innerHTML = "";
  
  if (!state.currentBook) return;
  const bookId = state.currentBook.id;
  
  const noteKeys = Object.keys(state.notesData).filter(key => key.startsWith(`${bookId}-`));
  
  if (noteKeys.length === 0) {
    list.innerHTML = `<li class="saved-empty-msg">Nenhuma anotação feita nesta leitura.</li>`;
    return;
  }
  
  noteKeys.sort((a, b) => {
    const partA = a.split("-");
    const partB = b.split("-");
    const chapA = parseInt(partA[1], 10);
    const chapB = parseInt(partB[1], 10);
    if (chapA !== chapB) return chapA - chapB;
    const pageA = parseInt(partA[2], 10);
    const pageB = parseInt(partB[2], 10);
    return pageA - pageB;
  });
  
  noteKeys.forEach(key => {
    const note = state.notesData[key];
    const item = document.createElement("li");
    item.className = "saved-item note-item";
    
    item.innerHTML = `
      <div class="saved-item-info">
        <div class="saved-item-title">${note.chapTitle}</div>
        <div class="saved-item-meta">Pág. ${note.pageIndex + 1}</div>
        <div class="saved-item-snippet">${note.text}</div>
      </div>
      <button class="saved-item-delete-btn" aria-label="Remover anotação" data-key="${key}">×</button>
    `;
    
    item.querySelector(".saved-item-info").addEventListener("click", () => {
      state.currentChapterIndex = note.chapterIndex;
      state.currentPageIndex = note.pageIndex;
      renderCurrentPage();
      closeSidebar();
      setTimeout(() => {
        openNoteModal();
      }, 100);
    });
    
    item.querySelector(".saved-item-delete-btn").addEventListener("click", (e) => {
      e.stopPropagation();
      delete state.notesData[key];
      localStorage.setItem("verbum_dei_reader_notes", JSON.stringify(state.notesData));
      updateNoteUI();
      renderNotesList();
      updateLibraryStats();
    });
    
    list.appendChild(item);
  });
}

// ==========================================================================
// 15. Alternância de Abas na Sidebar (Índice vs. Favoritos e Notas)
// ==========================================================================
function switchSidebarTab(tabId) {
  const tabChapters = document.getElementById("tab-chapters");
  const tabSaved = document.getElementById("tab-saved");
  const panelChapters = document.getElementById("sidebar-chapters-panel");
  const panelSaved = document.getElementById("sidebar-saved-panel");
  
  if (tabId === "chapters") {
    if (tabChapters) tabChapters.classList.add("active");
    if (tabSaved) tabSaved.classList.remove("active");
    if (panelChapters) panelChapters.classList.add("active");
    if (panelSaved) panelSaved.classList.remove("active");
  } else if (tabId === "saved") {
    if (tabChapters) tabChapters.classList.remove("active");
    if (tabSaved) tabSaved.classList.add("active");
    if (panelChapters) panelChapters.classList.remove("active");
    if (panelSaved) panelSaved.classList.add("active");
    
    renderBookmarksList();
    renderNotesList();
  }
}
