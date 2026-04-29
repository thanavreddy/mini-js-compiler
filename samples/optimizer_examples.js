// Examples to exercise optimizer passes (constant folding, copy propagation)
let a = 5 + 3;        // should fold to 8
let b = a * 2;        // copy propagation may replace a with 8
let c = b + 0;        // adding 0 — trivially preserved but shows propagation
console.log(c);
