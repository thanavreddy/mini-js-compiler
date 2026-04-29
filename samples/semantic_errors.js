// Samples that trigger semantic errors for testing
// 1) Use-before-declare
console.log(u);
let u = 5;

// 2) Redeclaration in same scope (will be reported)
let v = 1;
let v = 2;

// 3) Invalid operator on strings
let s = "foo" - "bar";
console.log(s);
