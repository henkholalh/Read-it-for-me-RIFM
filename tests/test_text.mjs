// Text-processing tests for index.html. Run:  node tests/test_text.mjs
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const grab = name => html.match(new RegExp(`function ${name}\\([\\s\\S]*?\\n}\\n`))[0];
const { splitSentences, speakable, joinLines, stripMarkdown } =
  new Function("window", `${grab('splitSentences')}${grab('speakable')}${grab('joinLines')}${grab('stripMarkdown')}
    return { splitSentences, speakable, joinLines, stripMarkdown };`)(globalThis);

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

console.log(`\n${n} tests passed`);
