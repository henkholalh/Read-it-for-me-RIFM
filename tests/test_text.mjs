// Text-processing tests for index.html. Run:  node tests/test_text.mjs
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const grab = name => html.match(new RegExp(`function ${name}\\([\\s\\S]*?\\n}\\n`))[0];
const isYearLine = html.match(/const isYear = .*\n/)[0];
const { splitSentences, speakable, joinLines, stripMarkdown, paginate, mapIndex } =
  new Function("window", `${grab('splitSentences')}${grab('cleanText')}${isYearLine}${grab('sayWord')}${grab('sayTokens')}
    ${grab('speakable')}${grab('joinLines')}${grab('stripMarkdown')}${grab('paginate')}${grab('mapIndex')}
    return { splitSentences, speakable, joinLines, stripMarkdown, paginate, mapIndex };`)(globalThis);

let n = 0;
const test = (name, fn) => { fn(); n++; console.log('✓', name); };

test('headings and bullets get a full stop so the voice pauses', () => {
  assert.equal(speakable('Introduction'), 'Introduction.');
  assert.equal(speakable('• First point'), 'First point.');
  assert.equal(speakable('Already done.'), 'Already done.');
  assert.equal(speakable('Is it?'), 'Is it?');
  assert.equal(speakable('   \n '), '');
});

test('PDF wrapped lines are joined, headings kept separate', () => {
  const out = joinLines([
    { t: 'Introduction', gap: 24 },
    { t: 'The quick brown fox jumps over the lazy dog and keeps', gap: 12 },
    { t: 'running across the field until the sun goes down. Then', gap: 12 },
    { t: 'it rests.', gap: 24 },
    { t: 'A well-', gap: 12 },
    { t: 'known fact is stated here in this long final line of text.', gap: 0 },
  ]);
  assert.match(out, /^Introduction\nThe quick brown fox .* keeps running across .* Then it rests\./);
  assert.match(out, /well-?known/);
});

test('long sentences are split into short chunks', () => {
  const parts = splitSentences('word, '.repeat(200));
  assert.ok(parts.length > 1);
  assert.ok(parts.every(p => p.length <= 141));
  assert.equal(parts.join(''), 'word, '.repeat(200));   // nothing lost
});

test('long sentences split at the comma, not mid-phrase', () => {
  const parts = splitSentences('This is a sample document that is being read out loud by the app, and it wraps across several lines just like a real PDF would do when it is printed.');
  assert.equal(parts.length, 2);
  assert.match(parts[0], /by the app,$/);
});

test('sentences split on punctuation and line breaks', () => {
  const parts = splitSentences('Hello there. How are you?\nNew line').map(speakable).filter(Boolean);
  assert.deepEqual(parts, ['Hello there.', 'How are you?', 'New line.']);
});

test('markdown is cleaned up', () => {
  assert.equal(stripMarkdown('# Title\nSee [docs](http://x) **now**').trim(), 'Title\nSee docs now');
});

test('PDF pages stay as real pages', () => {
  const { sentences, pageStart } = paginate('Page one text.\n\n\fPage two text. More.\n\n\f\n\n\fLast page.');
  assert.equal(pageStart.length, 4);                      // an empty (image-only) page still counts
  assert.equal(sentences.slice(pageStart[1], pageStart[2]).join('').trim(), 'Page two text. More.');
  assert.ok(sentences.every(s => !s.includes('\f')));
});

test('other text is cut into pages at paragraph breaks', () => {
  const para = 'A sentence that is about fifty characters long. '.repeat(10) + '\n\n';   // ~490 chars
  const text = para.repeat(30);
  const { sentences, pageStart } = paginate(text);
  assert.ok(pageStart.length >= 5 && pageStart.length <= 7, String(pageStart.length));
  for (const start of pageStart.slice(1)) assert.match(sentences[start - 1], /\n\s*$/);   // pages end with a paragraph
  for (const start of pageStart) assert.ok(sentences[start].trim(), 'page starts with a blank line');
  assert.equal(sentences.join(''), text);                 // nothing lost
});

test('one huge paragraph still gets pages', () => {
  const { pageStart } = paginate('No paragraph breaks here at all. '.repeat(1000));
  assert.ok(pageStart.length > 5);
});

test('short text is a single page', () => {
  assert.deepEqual(paginate('Just a little text.').pageStart, [0]);
});

test('abbreviations are read the way a person says them', () => {
  assert.equal(speakable('Fruit, e.g. apples, is good'), 'Fruit, for example apples, is good.');
  assert.equal(speakable('Bring tools (eg, a hammer)'), 'Bring tools (for example, a hammer).');
  assert.equal(speakable('The main one, i.e. the first'), 'The main one, that is the first.');
  assert.equal(speakable('Pens, paper etc.'), 'Pens, paper et cetera.');
  assert.equal(speakable('Cats vs. dogs'), 'Cats versus dogs.');
  assert.equal(speakable('It costs approx. 5 dollars'), 'It costs approximately 5 dollars.');
  assert.equal(speakable('See No. 5 below'), 'See number 5 below.');
  assert.equal(speakable('I said no. Then left'), 'I said no. Then left.');   // "no." alone is left alone
  assert.equal(speakable('Tea w/ milk, coffee w/o sugar'), 'Tea with milk, coffee without sugar.');
});

test('Q1 becomes Question 1, or quarter 1 next to a year', () => {
  assert.equal(speakable('Q1. What is your name?'), 'Question 1. What is your name?');
  assert.equal(speakable('Answer Q12 and Q3'), 'Answer Question 12 and Question 3.');
  assert.equal(speakable('Sales in Q1 2025 rose'), 'Sales in quarter 1 2025 rose.');
  assert.equal(speakable('FY24 Q2 results'), 'FY24 quarter 2 results.');
});

test('a slash between words is read as "or", but not in links, dates or units', () => {
  assert.equal(speakable('Answer yes/no'), 'Answer yes or no.');
  assert.equal(speakable('Bring a pen and/or pencil'), 'Bring a pen and or pencil.');
  assert.equal(speakable('He/she can come'), 'He or she can come.');
  assert.equal(speakable('Tea / coffee'), 'Tea or coffee.');
  assert.equal(speakable('Due 12/05/2025, half is 1/2'), 'Due 12/05/2025, half is 1/2.');
  assert.equal(speakable('Drive at 50 km/h'), 'Drive at 50 km/h.');
  assert.equal(speakable('Visit https://example.com/a/b now'), 'Visit https://example.com/a/b now.');
});

test('dashes still become pauses and bullets are dropped', () => {
  assert.equal(speakable('This – that'), 'This, that.');
  assert.equal(speakable('• e.g. one'), 'for example one.');
});

test('word highlighting stays on the right word after an expansion', () => {
  const raw = 'Use e.g. a pen today';
  const spoken = speakable(raw);                          // "Use for example a pen today."
  const at = word => mapIndex(raw, spoken, spoken.indexOf(word));
  assert.equal(raw.slice(at('example')), 'e.g. a pen today');
  assert.equal(raw.slice(at('pen')), 'pen today');
  const raw2 = '• Q1 – yes/no answers';
  const sp2 = speakable(raw2);                           // "Question 1, yes or no answers."
  assert.equal(raw2.slice(mapIndex(raw2, sp2, sp2.indexOf('answers'))), 'answers');
});

test('no sentence break after e.g. / i.e. / No.', () => {
  assert.deepEqual(splitSentences('Fruit, e.g. Apples are good. Next one.'), ['Fruit, e.g. Apples are good. ', 'Next one.']);
  assert.equal(splitSentences('Q1. What is it?').length, 2);           // a question number still pauses
  assert.equal(splitSentences('I said no. Then I left.').length, 2);   // "no." at a sentence end is not "number"
});

console.log(`\n${n} tests passed`);
