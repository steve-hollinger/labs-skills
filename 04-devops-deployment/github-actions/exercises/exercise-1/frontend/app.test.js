/**
 * Tests for sample frontend.
 */

const { test } = require('node:test');
const assert = require('node:assert');
const { add, multiply } = require('./app');

test('add function', () => {
    assert.strictEqual(add(2, 3), 5);
});

test('multiply function', () => {
    assert.strictEqual(multiply(2, 3), 6);
});
