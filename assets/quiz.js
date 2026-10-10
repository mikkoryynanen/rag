// Quiz component. Markup:
//   <fieldset class="quiz" data-correct="b">
//     <legend>Question?</legend>
//     <div class="options"><button type="button" data-key="a">…</button>…</div>
//     <p class="explain" hidden>Why.</p>
//   </fieldset>
// Optional: <p class="quiz-score" data-quiz-score></p> shows the tally once every question is answered.
(function () {
  const quizzes = [...document.querySelectorAll('.quiz')];
  let right = 0, done = 0;
  quizzes.forEach((q) => {
    const buttons = q.querySelectorAll('button[data-key]');
    buttons.forEach((b) => b.addEventListener('click', () => {
      const ok = b.dataset.key === q.dataset.correct;
      buttons.forEach((x) => {
        x.disabled = true;
        if (x.dataset.key === q.dataset.correct) x.classList.add('is-correct');
      });
      if (!ok) b.classList.add('is-wrong');
      const explain = q.querySelector('.explain');
      explain.prepend(document.createTextNode(ok ? 'Correct. ' : 'Not quite. '));
      explain.hidden = false;
      done += 1; right += ok ? 1 : 0;
      const score = document.querySelector('[data-quiz-score]');
      if (score && done === quizzes.length) score.textContent = right + ' of ' + quizzes.length + ' correct on the first try.';
    }));
  });
})();
