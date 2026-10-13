/* Dependency-free regression harness for the static browser explorer. */
"use strict";
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");

class FakeNode {
  constructor(tag = "div") {
    this.tag = tag;
    this.children = [];
    this.value = "";
    this.textContent = "";
    this.listeners = {};
    this.selectedIndex = 0;
  }
  appendChild(child) {
    this.children.push(child);
    if (this.tag === "select" && !this.value) this.value = child.value;
    return child;
  }
  append(...children) { children.forEach(node => this.appendChild(node)); }
  replaceChildren(...children) {
    this.children = [];
    this.value = "";
    children.forEach(node => this.appendChild(node));
  }
  addEventListener(name, callback) { this.listeners[name] = callback; }
}

const ids = ["gene", "allele1", "allele2", "result", "panel-form"];
const nodes = Object.fromEntries(ids.map(id => [id, new FakeNode(id.startsWith("allele") ? "select" : "div")]));
nodes.gene.value = "CYP2D6";
const document = {
  getElementById(id) { assert.ok(nodes[id], id); return nodes[id]; },
  createElement(tag) { return new FakeNode(tag); },
};
const html = fs.readFileSync("web/index.html", "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match, "Expected inline script");
const context = vm.createContext({document, Object});
vm.runInContext(match[1], context);
const cases = [
  ["CYP2D6","*1","*10","Normal metabolizer (NM)","1.25"],
  ["CYP2D6","*4","*4","Poor metabolizer (PM)","0"],
  ["CYP2D6","*10","*10","Intermediate metabolizer (IM)","0.5"],
  ["CYP2C19","*1","*17","Rapid metabolizer (RM)","Not applicable (function-based translation)"],
  ["CYP2C19","*17","*17","Ultrarapid metabolizer (UM)","Not applicable (function-based translation)"],
  ["CYP2C19","*2","*17","Intermediate metabolizer (IM)","Not applicable (function-based translation)"],
];
for (const [gene,a1,a2,phenotype,score] of cases) {
  const actual = vm.runInContext("interpret("+JSON.stringify(gene)+","+JSON.stringify(a1)+","+JSON.stringify(a2)+")",context);
  assert.equal(actual.phenotype, phenotype);
  assert.equal(actual.score, score);
}
nodes.gene.value = "CYP2C19";
nodes.gene.listeners.change();
assert.ok(nodes.allele1.children.some(x => x.value === "*17"));
nodes.allele1.value = "*1";
nodes.allele2.value = "*17";
nodes["panel-form"].listeners.submit({preventDefault() {}});
assert.ok(nodes.result.children.length > 0);
assert.ok(!html.includes("fetch('/api/audit'"), "Static page must not rely on API calls");
assert.ok(!html.includes("HMAC_SHA256_e83f"), "Do not display invented audit signatures");
console.log("Static browser phenotype mappings and DOM events: passed");
