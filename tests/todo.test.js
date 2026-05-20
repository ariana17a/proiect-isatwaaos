'use strict';

// ── Shim pentru localStorage (nu există în Node.js) ───────────────────────
const store = {};
global.localStorage = {
  getItem:    key       => store[key] ?? null,
  setItem:    (key, v)  => { store[key] = v; },
  removeItem: key       => { delete store[key]; }
};

// Curăță state-ul între teste
global.localStorage.setItem('isa-todos', '[]');

const { TodoApp } = require('../app/app.js');

// ── Mini test runner ───────────────────────────────────────────────────────
let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    TodoApp.reset();
    fn();
    console.log(`  ✅  ${name}`);
    passed++;
  } catch (err) {
    console.error(`  ❌  ${name}`);
    console.error(`       ${err.message}`);
    failed++;
  }
}

function assert(condition, msg) {
  if (!condition) throw new Error(msg || 'Assertion failed');
}

function assertEqual(a, b, msg) {
  if (a !== b) throw new Error(msg || `Expected ${JSON.stringify(b)}, got ${JSON.stringify(a)}`);
}

// ── Teste ──────────────────────────────────────────────────────────────────
console.log('\nTODO Manager — Test Suite\n');

// 1. addTodo
console.log('addTodo()');

test('adaugă o sarcină cu text valid', () => {
  const todo = TodoApp.addTodo('Primul task');
  assert(todo !== null, 'Ar trebui să returneze un obiect');
  assertEqual(todo.text, 'Primul task');
  assertEqual(todo.completed, false);
  assertEqual(TodoApp.getFiltered().length, 1);
});

test('ignoră textul gol', () => {
  const result = TodoApp.addTodo('   ');
  assertEqual(result, null, 'Textul gol nu trebuie acceptat');
  assertEqual(TodoApp.getFiltered().length, 0);
});

test('trimează spațiile din text', () => {
  const todo = TodoApp.addTodo('  sarcină cu spații  ');
  assertEqual(todo.text, 'sarcină cu spații');
});

test('fiecare sarcină primește un id unic', () => {
  const a = TodoApp.addTodo('Task A');
  const b = TodoApp.addTodo('Task B');
  assert(a.id !== b.id, 'ID-urile trebuie să fie distincte');
});

// 2. toggleTodo
console.log('\ntoggleTodo()');

test('marchează o sarcină ca finalizată', () => {
  const todo = TodoApp.addTodo('Test toggle');
  TodoApp.toggleTodo(todo.id);
  const items = TodoApp.getFiltered();
  assertEqual(items[0].completed, true);
});

test('demarchează o sarcină finalizată', () => {
  const todo = TodoApp.addTodo('Test toggle dublu');
  TodoApp.toggleTodo(todo.id);
  TodoApp.toggleTodo(todo.id);
  const items = TodoApp.getFiltered();
  assertEqual(items[0].completed, false);
});

test('returnează false pentru id inexistent', () => {
  const result = TodoApp.toggleTodo(9999);
  assertEqual(result, false);
});

// 3. deleteTodo
console.log('\ndeleteTodo()');

test('șterge o sarcină existentă', () => {
  const todo = TodoApp.addTodo('De șters');
  const ok = TodoApp.deleteTodo(todo.id);
  assertEqual(ok, true);
  assertEqual(TodoApp.getFiltered().length, 0);
});

test('returnează false pentru id inexistent', () => {
  const ok = TodoApp.deleteTodo(9999);
  assertEqual(ok, false);
});

// 4. clearCompleted
console.log('\nclearCompleted()');

test('șterge doar sarcinile finalizate', () => {
  TodoApp.addTodo('Activă');
  const b = TodoApp.addTodo('Finalizată');
  TodoApp.toggleTodo(b.id);
  const removed = TodoApp.clearCompleted();
  assertEqual(removed, 1);
  assertEqual(TodoApp.getFiltered().length, 1);
  assertEqual(TodoApp.getFiltered()[0].text, 'Activă');
});

test('returnează 0 dacă nu există sarcini finalizate', () => {
  TodoApp.addTodo('Activă 1');
  TodoApp.addTodo('Activă 2');
  const removed = TodoApp.clearCompleted();
  assertEqual(removed, 0);
});

// 5. getFiltered
console.log('\ngetFiltered()');

test('filtrul "all" returnează toate sarcinile', () => {
  TodoApp.addTodo('A'); TodoApp.addTodo('B'); TodoApp.addTodo('C');
  assertEqual(TodoApp.getFiltered('all').length, 3);
});

test('filtrul "active" returnează doar sarcinile necompletate', () => {
  const a = TodoApp.addTodo('Activă');
  const b = TodoApp.addTodo('Finalizată');
  TodoApp.toggleTodo(b.id);
  const active = TodoApp.getFiltered('active');
  assertEqual(active.length, 1);
  assertEqual(active[0].id, a.id);
});

test('filtrul "completed" returnează doar sarcinile finalizate', () => {
  const a = TodoApp.addTodo('Activă');
  const b = TodoApp.addTodo('Finalizată');
  TodoApp.toggleTodo(b.id);
  const completed = TodoApp.getFiltered('completed');
  assertEqual(completed.length, 1);
  assertEqual(completed[0].id, b.id);
});

// 6. activeCount
console.log('\nactiveCount');

test('numără corect sarcinile active', () => {
  TodoApp.addTodo('A'); TodoApp.addTodo('B'); TodoApp.addTodo('C');
  const c = TodoApp.getFiltered()[2];
  TodoApp.toggleTodo(c.id);
  assertEqual(TodoApp.activeCount, 2);
});

// ── Raport final ───────────────────────────────────────────────────────────
console.log(`\n${'─'.repeat(40)}`);
console.log(`Total: ${passed + failed} teste | ✅ ${passed} trecute | ❌ ${failed} eșuate`);
console.log(`${'─'.repeat(40)}\n`);

if (failed > 0) process.exit(1);
