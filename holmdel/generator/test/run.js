const ts = require('typescript'); const fs = require('fs');
const [,, tsPath, dataPath, settings] = process.argv;
const js = ts.transpileModule(fs.readFileSync(tsPath, 'utf8'), { compilerOptions: { target: ts.ScriptTarget.ES2019, module: ts.ModuleKind.None } }).outputText;
const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
const wb = { getName: () => data.name, getWorksheets: () => data.sheets.map(s => ({ getName: () => s.name, getRange: (a) => { if (a !== 'A1:R57') throw new Error('range ' + a); return { getValues: () => s.v }; } })) };
const main = new Function(js + '\nreturn main;')();
const out = main(wb, settings || '');
JSON.parse(out); // must be valid JSON
console.log(out);
