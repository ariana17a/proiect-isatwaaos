'use strict';

// ── State ──────────────────────────────────────────────────────────────────
let todos = JSON.parse(localStorage.getItem('isa-todos') || '[]');
let filter = 'all';
let nextId = todos.length ? Math.max(...todos.map(t => t.id)) + 1 : 1;

// ── Persistence ────────────────────────────────────────────────────────────
function save() {
  localStorage.setItem('isa-todos', JSON.stringify(todos));
}

// ── Core API (exportat pentru teste) ───────────────────────────────────────
const TodoApp = {
  /**
   * Adaugă o sarcină nouă.
   * @param {string} text
   * @returns {object|null} sarcina creată, sau null dacă textul e invalid
   */
  addTodo(text) {
    const trimmed = text.trim();
    if (!trimmed) return null;
    const todo = { id: nextId++, text: trimmed, completed: false };
    todos.push(todo);
    save();
    return todo;
  },

  /**
   * Comută starea completat/necompletat.
   * @param {number} id
   * @returns {boolean} true dacă s-a găsit elementul
   */
  toggleTodo(id) {
    const todo = todos.find(t => t.id === id);
    if (!todo) return false;
    todo.completed = !todo.completed;
    save();
    return true;
  },

  /**
   * Șterge o sarcină după id.
   * @param {number} id
   * @returns {boolean} true dacă s-a găsit și șters
   */
  deleteTodo(id) {
    const before = todos.length;
    todos = todos.filter(t => t.id !== id);
    if (todos.length < before) { save(); return true; }
    return false;
  },

  /**
   * Șterge toate sarcinile finalizate.
   * @returns {number} numărul de elemente șterse
   */
  clearCompleted() {
    const before = todos.length;
    todos = todos.filter(t => !t.completed);
    save();
    return before - todos.length;
  },

  /**
   * Returnează lista filtrată.
   * @param {'all'|'active'|'completed'} f
   * @returns {object[]}
   */
  getFiltered(f = 'all') {
    if (f === 'active')    return todos.filter(t => !t.completed);
    if (f === 'completed') return todos.filter(t =>  t.completed);
    return [...todos];
  },

  /** Numărul de sarcini active (necompletate). */
  get activeCount() {
    return todos.filter(t => !t.completed).length;
  },

  /** Resetează complet lista (util pentru teste). */
  reset() {
    todos = [];
    nextId = 1;
    save();
  }
};

// ── Export pentru teste (Node.js) ─────────────────────────────────────────
if (typeof module !== 'undefined') {
  module.exports = { TodoApp };
}

// ── Render (doar în browser) ───────────────────────────────────────────────
if (typeof document !== 'undefined') {

function render() {
  const list = document.getElementById('todo-list');
  const items = TodoApp.getFiltered(filter);

  if (!items.length) {
    list.innerHTML = '<li class="empty-msg">Nicio sarcină de afișat.</li>';
  } else {
    list.innerHTML = items.map(t => `
      <li class="${t.completed ? 'completed' : ''}" data-id="${t.id}">
        <input type="checkbox" ${t.completed ? 'checked' : ''} />
        <span class="todo-text">${escapeHtml(t.text)}</span>
        <button class="delete-btn" title="Șterge">✕</button>
      </li>`).join('');
  }

  const active = TodoApp.activeCount;
  document.getElementById('count-label').textContent =
    `${active} ${active === 1 ? 'sarcină rămasă' : 'sarcini rămase'}`;
}

function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;')
            .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Event handlers ─────────────────────────────────────────────────────────
function addItem() {
  const input = document.getElementById('todo-input');
  if (TodoApp.addTodo(input.value)) {
    input.value = '';
    render();
  }
}

document.getElementById('add-btn').addEventListener('click', addItem);
document.getElementById('todo-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') addItem();
});

const todoList = document.getElementById('todo-list');
todoList.addEventListener('change', e => {
  if (e.target.type === 'checkbox') {
    TodoApp.toggleTodo(+e.target.closest('li').dataset.id);
    render();
  }
});
todoList.addEventListener('click', e => {
  if (e.target.classList.contains('delete-btn')) {
    TodoApp.deleteTodo(+e.target.closest('li').dataset.id);
    render();
  }
});

document.getElementById('clear-btn').addEventListener('click', () => {
  TodoApp.clearCompleted(); render();
});

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    filter = btn.dataset.filter;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    render();
  });
});

// ── Init ───────────────────────────────────────────────────────────────────
render();

} // end if (typeof document !== 'undefined')

