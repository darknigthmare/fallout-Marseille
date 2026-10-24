#!/usr/bin/env node
'use strict';

/* Offline validation/installation of attributed architecture annotations.
 * The game adapters validate the same metric/document contracts as runtime.
 * Validation completes before the destination directory or file is touched.
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const Architecture = require('../src/v050/06_architecture_sources.js');
const Facades = require('../src/v050/07_facades.js');
const Interiors = require('../src/v050/08_city_interiors.js');

const DEFAULT_OUTPUT = path.resolve(__dirname, '../data/map_pack/architecture/index.json');
const ADAPTERS = { facades: Facades, interiors: Interiors };
const HELP = `Usage:
  node tools/architecture_documents.cjs validate --input PATH
  node tools/architecture_documents.cjs install --input PATH [--output PATH]
  node tools/architecture_documents.cjs --help

Validate attributed site labels, facade openings and interior plans offline.
Plans must bind the exact source geometry and metric building component.
Unknown details are never promoted to documented architecture.

Commands:
  validate  Check the JSON atlas with the actual game validators; write nothing.
  install   Validate first, then atomically replace the local atlas JSON.

Options:
  --input PATH   Existing UTF-8 JSON file, at most ${Architecture.MAX_BYTES} bytes.
  --output PATH Destination for install only.
                Default: data/map_pack/architecture/index.json in this repository.
  --help, -h     Show this help.

No requests, downloads, fixture generation or game build are performed.
Successful commands print a JSON summary. Errors print JSON on stderr.
`;

class UsageError extends Error {}

function parseArgs(argv) {
  if (argv.length === 1 && ['--help', '-h'].includes(argv[0])) return { help: true };
  const command = argv[0];
  if (!['validate', 'install'].includes(command)) {
    throw new UsageError('Expected validate or install; use --help for usage.');
  }
  if (argv.length === 2 && ['--help', '-h'].includes(argv[1])) return { help: true };
  const options = { command };
  for (let i = 1; i < argv.length; i++) {
    const flag = argv[i];
    if (!['--input', '--output'].includes(flag)) throw new UsageError('Unknown argument: ' + flag);
    const key = flag.slice(2);
    if (options[key] !== undefined) throw new UsageError('Duplicate argument: ' + flag);
    if (!argv[i + 1] || argv[i + 1].startsWith('--')) throw new UsageError('Missing path after ' + flag);
    options[key] = argv[++i];
  }
  if (!options.input) throw new UsageError('--input PATH is required.');
  if (command === 'validate' && options.output !== undefined) {
    throw new UsageError('--output is available only for install.');
  }
  options.input = path.resolve(options.input);
  if (command === 'install') options.output = path.resolve(options.output || DEFAULT_OUTPUT);
  return options;
}

function readAtlas(input) {
  const fd = fs.openSync(input, 'r');
  let bytes;
  try {
    const stat = fs.fstatSync(fd);
    if (!stat.isFile() || stat.size < 1 || stat.size > Architecture.MAX_BYTES) {
      throw new Error('Input must be a nonempty regular JSON file within the byte budget.');
    }
    // A growing file must not turn readFile into an unbounded allocation.
    bytes = Buffer.alloc(stat.size + 1);
    let length = 0;
    while (length < bytes.length) {
      const count = fs.readSync(fd, bytes, length, bytes.length - length, null);
      if (!count) break;
      length += count;
    }
    if (length !== stat.size || fs.fstatSync(fd).size !== stat.size) {
      throw new Error('Input changed during its bounded read.');
    }
    bytes = bytes.subarray(0, length);
  } finally {
    fs.closeSync(fd);
  }
  let text;
  try {
    text = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  } catch {
    throw new Error('Input is not valid UTF-8.');
  }
  let raw;
  try { raw = JSON.parse(text); } catch { throw new Error('Input is not valid JSON.'); }
  Architecture.validate(raw, ADAPTERS);
  // Preserve the submitted JSON and its association evidence/metadata. The
  // validator's returned records contain derived registry bookkeeping and
  // must never replace the raw world-metric targets or original documents.
  const atlas = raw;
  const outputBytes = Buffer.from(JSON.stringify(atlas) + '\n', 'utf8');
  if (outputBytes.length > Architecture.MAX_BYTES) throw new Error('Normalized atlas exceeds the byte budget.');
  return { atlas, inputBytes: bytes, outputBytes };
}

function install(output, bytes) {
  const directory = path.dirname(output);
  fs.mkdirSync(directory, { recursive: true });
  const temporary = path.join(directory, '.' + path.basename(output) + '.' + process.pid + '.' + crypto.randomBytes(8).toString('hex') + '.tmp');
  let fd = null;
  try {
    fd = fs.openSync(temporary, 'wx', 0o644);
    fs.writeFileSync(fd, bytes);
    fs.fsyncSync(fd);
    fs.closeSync(fd);
    fd = null;
    fs.renameSync(temporary, output);
  } finally {
    if (fd !== null) fs.closeSync(fd);
    // A successful rename removes the temporary path. Any failed write or
    // rename removes its temporary file while preserving the previous atlas.
    try { fs.unlinkSync(temporary); } catch (error) { if (error.code !== 'ENOENT') throw error; }
  }
}

function summary(options, result) {
  return {
    ok: true,
    command: options.command,
    input: options.input,
    ...(options.command === 'install' ? { output: options.output } : {}),
    inputBytes: result.inputBytes.length,
    inputSha256: crypto.createHash('sha256').update(result.inputBytes).digest('hex'),
    installedBytes: options.command === 'install' ? result.outputBytes.length : 0,
    atlasSha256: crypto.createHash('sha256').update(result.outputBytes).digest('hex'),
    records: result.atlas.records.length,
    siteLabels: result.atlas.records.filter(record => record.label).length,
    facadeDocuments: result.atlas.records.filter(record => record.facadeDocument).length,
    interiorDocuments: result.atlas.records.filter(record => record.interiorDocument).length,
    network: false,
    wroteFiles: options.command === 'install'
  };
}

function main(argv = process.argv.slice(2)) {
  try {
    const options = parseArgs(argv);
    if (options.help) { process.stdout.write(HELP); return 0; }
    const result = readAtlas(options.input);
    if (options.command === 'install') install(options.output, result.outputBytes);
    process.stdout.write(JSON.stringify(summary(options, result)) + '\n');
    return 0;
  } catch (error) {
    process.stderr.write(JSON.stringify({ ok: false, error: error.message || String(error) }) + '\n');
    return error instanceof UsageError ? 2 : 1;
  }
}

module.exports = { DEFAULT_OUTPUT, HELP, UsageError, parseArgs, readAtlas, install, summary, main };
if (require.main === module) process.exitCode = main();
