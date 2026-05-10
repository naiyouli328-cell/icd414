#!/usr/bin/env python3
"""Build the quiz web app - reads questions.json and generates index.html with embedded data."""

import json

DATA_FILE = 'D:/414Web/questions.json'
OUTPUT_FILE = 'D:/414Web/index.html'

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Generate type summary
from collections import Counter
type_counts = Counter(q['type'] for q in questions)
type_summary = dict(type_counts.most_common())

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ICD 刷题系统</title>
<style>
  :root {
    --primary: #4f6ef7;
    --primary-light: #6b84f5;
    --primary-dark: #3a56d4;
    --success: #22c55e;
    --error: #ef4444;
    --warning: #f59e0b;
    --bg: #f0f2f5;
    --card-bg: #ffffff;
    --text: #1e293b;
    --text-secondary: #64748b;
    --border: #e2e8f0;
    --radius: 12px;
    --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
    --shadow-lg: 0 10px 30px rgba(0,0,0,0.1);
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }

  /* Header */
  .app-header {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: white;
    padding: 24px 32px;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 12px rgba(79, 110, 247, 0.3);
  }
  .app-header h1 {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 1px;
  }
  .app-header .subtitle {
    font-size: 13px;
    opacity: 0.85;
    margin-top: 4px;
  }

  /* Filter bar */
  .filter-bar {
    display: flex;
    gap: 8px;
    padding: 16px 32px;
    background: var(--card-bg);
    border-bottom: 1px solid var(--border);
    overflow-x: auto;
    position: sticky;
    top: 80px;
    z-index: 99;
  }
  .filter-btn {
    flex-shrink: 0;
    padding: 8px 18px;
    border: 1px solid var(--border);
    border-radius: 20px;
    background: var(--card-bg);
    color: var(--text-secondary);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
    font-family: inherit;
  }
  .filter-btn:hover { border-color: var(--primary); color: var(--primary); }
  .filter-btn.active {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
  }
  .filter-btn .count {
    display: inline-block;
    background: rgba(0,0,0,0.08);
    border-radius: 10px;
    padding: 0 8px;
    margin-left: 4px;
    font-size: 11px;
    line-height: 18px;
  }
  .filter-btn.active .count {
    background: rgba(255,255,255,0.25);
  }

  /* Question list */
  .question-list {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px 16px 60px;
  }
  .question-list .empty {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-secondary);
    font-size: 15px;
  }

  /* Question card */
  .q-card {
    background: var(--card-bg);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 16px;
    padding: 24px;
    transition: box-shadow 0.2s;
    border: 1px solid var(--border);
  }
  .q-card:hover { box-shadow: var(--shadow-lg); }

  .q-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
  }
  .q-id {
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 600;
  }
  .q-type-badge {
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 10px;
    background: #eef2ff;
    color: var(--primary);
    font-weight: 600;
  }

  .q-text {
    font-size: 15px;
    line-height: 1.8;
    margin-bottom: 18px;
    color: var(--text);
  }
  .q-text .blank-input {
    display: inline-block;
    width: 120px;
    margin: 0 4px;
    padding: 2px 8px;
    border: none;
    border-bottom: 2px solid var(--primary);
    background: #f8f9ff;
    font-size: 14px;
    color: var(--text);
    outline: none;
    font-family: inherit;
    transition: border-color 0.2s;
  }
  .q-text .blank-input:focus { border-bottom-color: var(--primary-dark); }
  .q-text .blank-input.correct { border-bottom-color: var(--success); }
  .q-text .blank-input.wrong { border-bottom-color: var(--error); }

  /* Options (选择题) */
  .options {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 14px;
  }
  .option-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border: 1px solid var(--border);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 14px;
  }
  .option-item:hover { border-color: var(--primary-light); background: #f8f9ff; }
  .option-item.selected {
    border-color: var(--primary);
    background: #eef2ff;
  }
  .option-item .letter {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: var(--bg);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
    flex-shrink: 0;
  }
  .option-item.selected .letter { background: var(--primary); color: white; }

  /* 判断题 buttons */
  .judge-group {
    display: flex;
    gap: 12px;
    margin-bottom: 14px;
  }
  .judge-btn {
    padding: 10px 32px;
    border: 1px solid var(--border);
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.2s;
    background: var(--card-bg);
    font-family: inherit;
  }
  .judge-btn:hover { border-color: var(--primary); }
  .judge-btn.selected-true { border-color: var(--success); color: var(--success); background: #f0fdf4; }
  .judge-btn.selected-false { border-color: var(--error); color: var(--error); background: #fef2f2; }

  /* Text input / Textarea */
  .text-input {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid var(--border);
    border-radius: 8px;
    font-size: 14px;
    font-family: inherit;
    outline: none;
    transition: border-color 0.2s;
    resize: vertical;
    min-height: 38px;
  }
  .text-input:focus { border-color: var(--primary); }

  /* Action buttons */
  .q-actions {
    display: flex;
    gap: 8px;
    margin-top: 14px;
    flex-wrap: wrap;
  }
  .btn {
    padding: 8px 20px;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
  }
  .btn-primary { background: var(--primary); color: white; }
  .btn-primary:hover { background: var(--primary-dark); }
  .btn-outline {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-secondary);
  }
  .btn-outline:hover { border-color: var(--primary); color: var(--primary); }
  .btn-success { background: var(--success); color: white; }
  .btn-success:hover { opacity: 0.9; }

  /* Feedback */
  .feedback {
    margin-top: 12px;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    display: none;
  }
  .feedback.show { display: block; }
  .feedback.correct { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }
  .feedback.wrong { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
  .feedback.info { background: #f8f9ff; color: var(--primary); border: 1px solid #c7d2fe; }

  /* Answer reveal */
  .answer-reveal {
    margin-top: 12px;
    padding: 14px;
    background: #f8fafc;
    border: 1px dashed var(--border);
    border-radius: 8px;
    display: none;
  }
  .answer-reveal.show { display: block; }
  .answer-reveal .label { font-size: 12px; color: var(--text-secondary); font-weight: 600; margin-bottom: 6px; }
  .answer-reveal .content { font-size: 14px; line-height: 1.7; color: var(--text); }
  .answer-reveal .content code {
    display: inline-block;
    background: #eef2ff;
    color: var(--primary);
    padding: 1px 8px;
    border-radius: 4px;
    font-size: 14px;
  }
  .answer-reveal .detail-box {
    margin-top: 10px;
    padding: 10px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 13px;
    line-height: 1.6;
    white-space: pre-wrap;
    color: var(--text-secondary);
  }

  /* Stats footer */
  .stats-bar {
    text-align: center;
    padding: 16px;
    color: var(--text-secondary);
    font-size: 13px;
  }

  /* Responsive */
  @media (max-width: 600px) {
    .app-header { padding: 16px 16px; }
    .app-header h1 { font-size: 18px; }
    .filter-bar { padding: 12px 16px; top: 64px; }
    .question-list { padding: 12px 8px 40px; }
    .q-card { padding: 16px; }
    .q-text { font-size: 14px; }
  }
</style>
</head>
<body>

<header class="app-header">
  <h1>ICD 刷题系统</h1>
  <div class="subtitle">疾病分类与代码  ·  共 <strong id="total-count"></strong> 题</div>
</header>

<nav class="filter-bar" id="filter-bar"></nav>

<main class="question-list" id="question-list"></main>

<div class="stats-bar" id="stats-bar"></div>

<script>
const QUESTIONS = __DATA__;

const TYPE_LABELS = {
  '填空题': '填空题',
  '选择题': '选择题',
  '判断题': '判断题',
  '简答题': '简答题',
  '查码题': '查码题',
  '主要诊断选择题': '主要诊断',
};

const LETTERS = 'ABCDEFGH'.split('');

// ---- State ----
let currentType = '全部';
let userAnswers = {};       // { id: value }
let checkedState = {};      // { id: 'correct'|'wrong'|null }
let revealedAnswers = new Set();

// ---- Init ----
document.getElementById('total-count').textContent = QUESTIONS.length;

// ---- Filter ----
function buildFilter() {
  const counts = { '全部': QUESTIONS.length };
  QUESTIONS.forEach(q => {
    counts[q.type] = (counts[q.type] || 0) + 1;
  });
  const frag = document.createDocumentFragment();
  for (const [type, count] of Object.entries(counts)) {
    const btn = document.createElement('button');
    btn.className = 'filter-btn' + (type === currentType ? ' active' : '');
    const label = TYPE_LABELS[type] || type;
    btn.innerHTML = `${label} <span class="count">${count}</span>`;
    btn.dataset.type = type;
    btn.addEventListener('click', () => {
      currentType = type;
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.toggle('active', b.dataset.type === currentType));
      renderQuestions();
    });
    frag.appendChild(btn);
  }
  document.getElementById('filter-bar').appendChild(frag);
}

// ---- Render ----
function getFiltered() {
  return currentType === '全部'
    ? QUESTIONS
    : QUESTIONS.filter(q => q.type === currentType);
}

function renderQuestions() {
  const list = document.getElementById('question-list');
  const filtered = getFiltered();

  if (filtered.length === 0) {
    list.innerHTML = '<div class="empty">没有找到题目</div>';
    document.getElementById('stats-bar').textContent = '';
    return;
  }

  const frag = document.createDocumentFragment();
  filtered.forEach((q, idx) => {
    const card = createCard(q, idx + 1, filtered.length);
    frag.appendChild(card);
  });
  list.innerHTML = '';
  list.appendChild(frag);

  const total = filtered.length;
  const answered = filtered.filter(q => checkedState[q.id] === 'correct').length;
  document.getElementById('stats-bar').textContent = `显示 ${total} 题 · 答对 ${answered} 题`;
}

function createCard(q, index, total) {
  const div = document.createElement('div');
  div.className = 'q-card';
  div.dataset.id = q.id;

  // Header
  const header = document.createElement('div');
  header.className = 'q-header';
  header.innerHTML = `<span class="q-id">#${q.id}</span><span class="q-type-badge">${TYPE_LABELS[q.type] || q.type}</span>`;
  div.appendChild(header);

  // Question text
  const qText = document.createElement('div');
  qText.className = 'q-text';
  div.appendChild(qText);

  // Interaction area
  const interaction = document.createElement('div');
  div.appendChild(interaction);

  // Feedback
  const feedback = document.createElement('div');
  feedback.className = 'feedback';
  div.appendChild(feedback);

  // Answer reveal
  const reveal = document.createElement('div');
  reveal.className = 'answer-reveal';
  div.appendChild(reveal);

  // Render based on type
  switch (q.type) {
    case '填空题':
      renderFillBlank(q, qText, interaction, feedback, reveal);
      break;
    case '选择题':
      renderChoice(q, qText, interaction, feedback, reveal);
      break;
    case '判断题':
      renderJudge(q, qText, interaction, feedback, reveal);
      break;
    case '简答题':
      renderTextQ(q, qText, interaction, feedback, reveal);
      break;
    case '查码题':
      renderCodeQ(q, qText, interaction, feedback, reveal);
      break;
    case '主要诊断选择题':
      renderMainDiagQ(q, qText, interaction, feedback, reveal);
      break;
    default:
      qText.textContent = q.question;
      renderTextQ(q, qText, interaction, feedback, reveal);
  }

  return div;
}

// ---- 填空题 ----
function renderFillBlank(q, qText, interaction, feedback, reveal) {
  const parts = q.question.split('（____）');
  if (parts.length > 1) {
    const frag = document.createDocumentFragment();
    parts.forEach((part, i) => {
      frag.appendChild(document.createTextNode(part));
      if (i < parts.length - 1) {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'blank-input';
        input.placeholder = '答案';
        input.dataset.id = q.id;
        const saved = userAnswers[q.id];
        if (saved) input.value = saved;
        input.addEventListener('input', () => {
          userAnswers[q.id] = input.value;
          checkedState[q.id] = null;
          input.classList.remove('correct', 'wrong');
          feedback.classList.remove('show', 'correct', 'wrong');
        });
        frag.appendChild(input);
      }
    });
    qText.appendChild(frag);
  } else {
    qText.textContent = q.question;
  }

  const actions = document.createElement('div');
  actions.className = 'q-actions';
  const checkBtn = document.createElement('button');
  checkBtn.className = 'btn btn-primary';
  checkBtn.textContent = '检查答案';
  checkBtn.addEventListener('click', () => {
    const input = qText.querySelector('.blank-input');
    if (!input || !input.value.trim()) { showFeedback(feedback, '请先输入答案', 'info'); return; }
    const val = input.value.trim();
    const isCorrect = q.answers.some(a => a === val);
    checkedState[q.id] = isCorrect ? 'correct' : 'wrong';
    input.classList.add(isCorrect ? 'correct' : 'wrong');
    showFeedback(feedback, isCorrect ? '正确！' : '不正确，再看看正确答案', isCorrect ? 'correct' : 'wrong');
  });
  actions.appendChild(checkBtn);

  const revealBtn = createRevealBtn(q, reveal);
  actions.appendChild(revealBtn);
  interaction.appendChild(actions);

  buildRevealContent(q, reveal);

  // Check if already checked
  if (checkedState[q.id]) {
    const input = qText.querySelector('.blank-input');
    if (input) {
      input.classList.add(checkedState[q.id]);
      showFeedback(feedback, checkedState[q.id] === 'correct' ? '正确！' : '不正确', checkedState[q.id]);
    }
  }
}

// ---- 选择题 ----
function renderChoice(q, qText, interaction, feedback, reveal) {
  qText.textContent = q.question;

  const optDiv = document.createElement('div');
  optDiv.className = 'options';

  q.options.forEach((optText, idx) => {
    const label = LETTERS[idx];
    const item = document.createElement('div');
    item.className = 'option-item';
    if (userAnswers[q.id] === label) item.classList.add('selected');
    item.innerHTML = `<span class="letter">${label}</span><span>${optText}</span>`;
    item.addEventListener('click', () => {
      optDiv.querySelectorAll('.option-item').forEach(el => el.classList.remove('selected'));
      item.classList.add('selected');
      userAnswers[q.id] = label;
      checkedState[q.id] = null;
      feedback.classList.remove('show', 'correct', 'wrong');

      // Auto-check
      checkChoice(q, label, feedback);
    });
    optDiv.appendChild(item);
  });
  interaction.appendChild(optDiv);

  const actions = document.createElement('div');
  actions.className = 'q-actions';
  const revealBtn = createRevealBtn(q, reveal);
  actions.appendChild(revealBtn);
  interaction.appendChild(actions);

  buildRevealContent(q, reveal);
}

function checkChoice(q, selected, feedback) {
  const correct = q.answer;
  const isCorrect = selected === correct;
  checkedState[q.id] = isCorrect ? 'correct' : 'wrong';
  showFeedback(feedback, isCorrect ? '正确！' : `回答错误，正确答案是 ${correct}`, isCorrect ? 'correct' : 'wrong');
  // Highlight the correct option
  const card = feedback.closest('.q-card');
  if (card) {
    const items = card.querySelectorAll('.option-item');
    items.forEach((item, idx) => {
      const letter = LETTERS[idx];
      if (letter === correct) item.style.borderColor = 'var(--success)';
      if (letter === selected && !isCorrect) item.style.borderColor = 'var(--error)';
    });
  }
}

// ---- 判断题 ----
function renderJudge(q, qText, interaction, feedback, reveal) {
  qText.textContent = q.question;

  const group = document.createElement('div');
  group.className = 'judge-group';

  const trueBtn = document.createElement('button');
  trueBtn.className = 'judge-btn';
  trueBtn.textContent = '正确';
  trueBtn.addEventListener('click', () => {
    group.querySelectorAll('.judge-btn').forEach(b => b.className = 'judge-btn');
    trueBtn.classList.add('selected-true');
    checkJudge(q, '正确', feedback);
  });

  const falseBtn = document.createElement('button');
  falseBtn.className = 'judge-btn';
  falseBtn.textContent = '错误';
  falseBtn.addEventListener('click', () => {
    group.querySelectorAll('.judge-btn').forEach(b => b.className = 'judge-btn');
    falseBtn.classList.add('selected-false');
    checkJudge(q, '错误', feedback);
  });

  group.appendChild(trueBtn);
  group.appendChild(falseBtn);
  interaction.appendChild(group);

  const actions = document.createElement('div');
  actions.className = 'q-actions';
  const revealBtn = createRevealBtn(q, reveal);
  actions.appendChild(revealBtn);
  interaction.appendChild(actions);

  buildRevealContent(q, reveal);
}

function checkJudge(q, selected, feedback) {
  const isCorrect = selected === q.answer;
  checkedState[q.id] = isCorrect ? 'correct' : 'wrong';
  showFeedback(feedback, isCorrect ? '正确！' : '回答错误', isCorrect ? 'correct' : 'wrong');
}

// ---- 简答题 ----
function renderTextQ(q, qText, interaction, feedback, reveal) {
  qText.textContent = q.question;

  const textarea = document.createElement('textarea');
  textarea.className = 'text-input';
  textarea.rows = 3;
  textarea.placeholder = '输入你的答案...';
  const saved = userAnswers[q.id];
  if (saved) textarea.value = saved;
  textarea.addEventListener('input', () => { userAnswers[q.id] = textarea.value; });
  interaction.appendChild(textarea);

  const actions = document.createElement('div');
  actions.className = 'q-actions';
  const revealBtn = createRevealBtn(q, reveal);
  actions.appendChild(revealBtn);
  interaction.appendChild(actions);

  buildRevealContent(q, reveal);
}

// ---- 查码题 ----
function renderCodeQ(q, qText, interaction, feedback, reveal) {
  qText.textContent = q.question;

  const input = document.createElement('input');
  input.type = 'text';
  input.className = 'text-input';
  input.style.maxWidth = '200px';
  input.placeholder = '输入 ICD 编码...';
  const saved = userAnswers[q.id];
  if (saved) input.value = saved;
  input.addEventListener('input', () => { userAnswers[q.id] = input.value; });
  interaction.appendChild(input);

  const actions = document.createElement('div');
  actions.className = 'q-actions';
  const checkBtn = document.createElement('button');
  checkBtn.className = 'btn btn-primary';
  checkBtn.textContent = '检查答案';
  checkBtn.addEventListener('click', () => {
    if (!input.value.trim()) { showFeedback(feedback, '请输入编码', 'info'); return; }
    const isCorrect = input.value.trim().toUpperCase() === q.answer.toUpperCase();
    checkedState[q.id] = isCorrect ? 'correct' : 'wrong';
    showFeedback(feedback, isCorrect ? '编码正确！' : `不正确，正确答案是 ${q.answer}`, isCorrect ? 'correct' : 'wrong');
  });
  actions.appendChild(checkBtn);

  const revealBtn = createRevealBtn(q, reveal);
  actions.appendChild(revealBtn);
  interaction.appendChild(actions);

  buildRevealContent(q, reveal);
}

// ---- 主要诊断选择题 ----
function renderMainDiagQ(q, qText, interaction, feedback, reveal) {
  qText.textContent = q.question;

  const textarea = document.createElement('textarea');
  textarea.className = 'text-input';
  textarea.rows = 3;
  textarea.placeholder = '输入主要诊断及编码...';
  const saved = userAnswers[q.id];
  if (saved) textarea.value = saved;
  textarea.addEventListener('input', () => { userAnswers[q.id] = textarea.value; });
  interaction.appendChild(textarea);

  const actions = document.createElement('div');
  actions.className = 'q-actions';
  const revealBtn = createRevealBtn(q, reveal);
  actions.appendChild(revealBtn);
  interaction.appendChild(actions);

  buildRevealContent(q, reveal);
}

// ---- Shared helpers ----
function createRevealBtn(q, reveal) {
  const btn = document.createElement('button');
  btn.className = 'btn btn-outline';
  btn.textContent = '显示答案';
  btn.addEventListener('click', () => {
    const isShowing = reveal.classList.toggle('show');
    btn.textContent = isShowing ? '隐藏答案' : '显示答案';
    if (isShowing) revealedAnswers.add(q.id);
    else revealedAnswers.delete(q.id);
  });
  // Auto-show if previously revealed
  if (revealedAnswers.has(q.id)) {
    reveal.classList.add('show');
    btn.textContent = '隐藏答案';
  }
  return btn;
}

function buildRevealContent(q, reveal) {
  let html = '<div class="label">正确答案</div><div class="content">';
  html += `<code>${escapeHtml(q.answer)}</code>`;
  html += '</div>';
  if (q.detail) {
    html += `<div class="detail-box">${escapeHtml(q.detail)}</div>`;
  }
  reveal.innerHTML = html;
}

function showFeedback(el, msg, type) {
  el.className = 'feedback show ' + type;
  el.textContent = msg;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ---- Start ----
buildFilter();
renderQuestions();
</script>
</body>
</html>
'''

# Replace placeholder with actual data
data_json = json.dumps(questions, ensure_ascii=False)
html = HTML_TEMPLATE.replace('__DATA__', data_json)

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

type_labels = {
    '填空题': '填空题', '选择题': '选择题', '判断题': '判断题',
    '简答题': '简答题', '查码题': '查码题', '主要诊断选择题': '主要诊断',
}
print(f'✅ 生成完成: {OUTPUT_FILE}')
print(f'📊 共 {len(questions)} 题')
for t, c in type_summary.items():
    print(f'   {type_labels.get(t, t)}: {c}题')
