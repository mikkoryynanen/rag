// Two-vector playground. Markup: <div class="vsim wide" data-vector-sim></div>
// Shows cosine similarity, dot product and Euclidean distance for two 2D vectors,
// both as given and after scaling each to length 1.
(function () {
  const NS = 'http://www.w3.org/2000/svg';
  const svgEl = (tag, attrs, parent) => {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    parent.appendChild(n);
    return n;
  };
  const f = (x) => x.toFixed(3);

  document.querySelectorAll('[data-vector-sim]').forEach((root, i) => {
    const id = (s) => 'vsim' + i + '-' + s;
    const slider = (key, cls, label, min, max, step, value) =>
      '<label class="' + cls + '" for="' + id(key) + '">' + label +
      '<input type="range" id="' + id(key) + '" min="' + min + '" max="' + max + '" step="' + step + '" value="' + value + '">' +
      '<output id="' + id(key + '-out') + '"></output></label>';

    root.innerHTML =
      '<svg viewBox="-2.7 -2.7 5.4 5.4" role="img" aria-label="Two vectors drawn from the origin, with the unit circle"></svg>' +
      '<div class="vsim-panel">' +
      slider('aa', 'is-a', 'A direction', 0, 360, 1, 30) +
      slider('al', 'is-a', 'A length', 0.2, 2.5, 0.1, 1) +
      slider('ba', 'is-b', 'B direction', 0, 360, 1, 75) +
      slider('bl', 'is-b', 'B length', 0.2, 2.5, 0.1, 2) +
      '<div class="table-scroll"><table><thead><tr><th></th><th class="num">As given</th><th class="num">Scaled to length 1</th></tr></thead><tbody>' +
      '<tr><td>Cosine similarity</td><td class="num" id="' + id('cos') + '"></td><td class="num" id="' + id('ucos') + '"></td></tr>' +
      '<tr><td>Dot product</td><td class="num" id="' + id('dot') + '"></td><td class="num" id="' + id('udot') + '"></td></tr>' +
      '<tr><td>Euclidean distance</td><td class="num" id="' + id('dist') + '"></td><td class="num" id="' + id('udist') + '"></td></tr>' +
      '</tbody></table></div>' +
      '<p class="note" id="' + id('angle') + '"></p></div>';

    const svg = root.querySelector('svg');
    svgEl('line', { class: 'axis', x1: -2.7, y1: 0, x2: 2.7, y2: 0 }, svg);
    svgEl('line', { class: 'axis', x1: 0, y1: -2.7, x2: 0, y2: 2.7 }, svg);
    svgEl('circle', { class: 'unit', cx: 0, cy: 0, r: 1 }, svg);
    const parts = ['a', 'b'].map((k) => ({
      line: svgEl('line', { class: 'vec-' + k, x1: 0, y1: 0 }, svg),
      tip: svgEl('circle', { class: 'vec-' + k, r: 0.07 }, svg),
      ghost: svgEl('circle', { class: 'ghost vec-' + k, r: 0.055 }, svg), // where the vector lands once scaled to length 1
    }));
    const $ = (s) => document.getElementById(id(s));

    function draw() {
      const vecs = [['aa', 'al'], ['ba', 'bl']].map(([ang, len], k) => {
        const t = (+$(ang).value * Math.PI) / 180, r = +$(len).value;
        $(ang + '-out').textContent = $(ang).value + '°';
        $(len + '-out').textContent = r.toFixed(1);
        const v = { x: r * Math.cos(t), y: r * Math.sin(t), ux: Math.cos(t), uy: Math.sin(t) };
        const p = parts[k];
        p.line.setAttribute('x2', v.x); p.line.setAttribute('y2', -v.y); // SVG y points down
        p.tip.setAttribute('cx', v.x); p.tip.setAttribute('cy', -v.y);
        p.ghost.setAttribute('cx', v.ux); p.ghost.setAttribute('cy', -v.uy);
        return v;
      });
      const [a, b] = vecs;
      const dot = a.x * b.x + a.y * b.y;
      const cos = Math.max(-1, Math.min(1, a.ux * b.ux + a.uy * b.uy));
      $('cos').textContent = f(cos);
      $('ucos').textContent = f(cos);
      $('dot').textContent = f(dot);
      $('udot').textContent = f(cos);
      $('dist').textContent = f(Math.hypot(a.x - b.x, a.y - b.y));
      $('udist').textContent = f(Math.hypot(a.ux - b.ux, a.uy - b.uy));
      $('angle').textContent = 'Angle between A and B: ' + ((Math.acos(cos) * 180) / Math.PI).toFixed(0) + '°. Hollow dots mark each vector scaled to length 1 (on the dashed unit circle).';
    }
    root.querySelectorAll('input').forEach((inp) => inp.addEventListener('input', draw));
    draw();
  });
})();
