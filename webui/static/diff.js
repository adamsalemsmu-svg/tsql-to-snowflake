// webui/static/diff.js

function esc(s) {
  return s.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}
function lines(s) { return s.replace(/\r\n/g, '\n').split('\n'); }

function diffLines(aLines, bLines) {
  const n = aLines.length, m = bLines.length;
  const dp = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i][j] = aLines[i] === bLines[j]
        ? dp[i + 1][j + 1] + 1
        : Math.max(dp[i + 1][j], dp[i][j + 1]);
    }
  }
  const ops = [];
  let i = 0, j = 0;
  while (i < n && j < m) {
    if (aLines[i] === bLines[j]) { ops.push({ type: 'keep', a: aLines[i++], b: bLines[j++] }); }
    else if (dp[i + 1][j] >= dp[i][j + 1]) { ops.push({ type: 'del', a: aLines[i++] }); }
    else { ops.push({ type: 'add', b: bLines[j++] }); }
  }
  while (i < n) ops.push({ type: 'del', a: aLines[i++] });
  while (j < m) ops.push({ type: 'add', b: bLines[j++] });
  return ops;
}

function intraline(a, b) {
  if (a === b) return { aHtml: esc(a), bHtml: esc(b) };
  const lenA = a.length, lenB = b.length, min = Math.min(lenA, lenB);
  let i = 0; while (i < min && a[i] === b[i]) i++;
  let j = 0; while (j < (min - i) && a[lenA - 1 - j] === b[lenB - 1 - j]) j++;
  const aMid = a.slice(i, lenA - j);
  const bMid = b.slice(i, lenB - j);
  return {
    aHtml: esc(a.slice(0, i)) + (aMid ? `<span class="hl-del">${esc(aMid)}</span>` : '') + esc(a.slice(lenA - j)),
    bHtml: esc(b.slice(0, i)) + (bMid ? `<span class="hl-ins">${esc(bMid)}</span>` : '') + esc(b.slice(lenB - j))
  };
}

export function renderDiff(sourceText, targetText, host) {
  const A = lines(sourceText), B = lines(targetText);
  const ops = diffLines(A, B);
  host.innerHTML = '';

  const wrap = document.createElement('div'); wrap.className = 'diff-grid';
  const left = document.createElement('div'); left.className = 'diff-col';
  const right = document.createElement('div'); right.className = 'diff-col';

  const lh = document.createElement('div'); lh.className = 'diff-col-head'; lh.textContent = 'Original T-SQL';
  const rh = document.createElement('div'); rh.className = 'diff-col-head'; rh.textContent = 'Snowflake SQL';
  left.appendChild(lh); right.appendChild(rh);

  let lnA = 1, lnB = 1;

  function addRow(type, aStr = '', bStr = '') {
    const L = document.createElement('div'); L.className = `diff-line ${type}`;
    const R = document.createElement('div'); R.className = `diff-line ${type}`;

    const lnoA = document.createElement('span'); lnoA.className = 'ln'; lnoA.textContent = aStr !== '' ? String(lnA++) : '';
    const symA = document.createElement('span'); symA.className = 'sym'; symA.textContent = type === 'del' ? '−' : type === 'add' ? '' : ' ';
    const codeA = document.createElement('code'); codeA.innerHTML = aStr;

    const lnoB = document.createElement('span'); lnoB.className = 'ln'; lnoB.textContent = bStr !== '' ? String(lnB++) : '';
    const symB = document.createElement('span'); symB.className = 'sym'; symB.textContent = type === 'add' ? '+' : type === 'del' ? '' : ' ';
    const codeB = document.createElement('code'); codeB.innerHTML = bStr;

    L.appendChild(lnoA); L.appendChild(symA); L.appendChild(codeA);
    R.appendChild(lnoB); R.appendChild(symB); R.appendChild(codeB);
    left.appendChild(L); right.appendChild(R);
  }

  for (let k = 0; k < ops.length; k++) {
    const op = ops[k];
    if (op.type === 'keep') { addRow('keep', esc(op.a), esc(op.b)); continue; }
    if (op.type === 'del' && k + 1 < ops.length && ops[k + 1].type === 'add') {
      const { aHtml, bHtml } = intraline(op.a, ops[k + 1].b);
      addRow('change', aHtml, bHtml); k++; continue;
    }
    if (op.type === 'del') { addRow('del', `<span class="hl-del">${esc(op.a)}</span>`, ''); continue; }
    if (op.type === 'add') { addRow('add', '', `<span class="hl-ins">${esc(op.b)}</span>`); continue; }
  }

  wrap.appendChild(left); wrap.appendChild(right); host.appendChild(wrap);
}

export function updateDiffFromEditors() {
  const src = document.getElementById('sql_in')?.value ?? '';
  const out = document.getElementById('sql_out')?.textContent ?? '';
  const host = document.getElementById('diff_host');
  if (host) renderDiff(src, out, host);
}
