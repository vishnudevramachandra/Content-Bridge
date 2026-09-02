// Snapshots the current *published* catalog content (Products,
// Certifications, Standards) back into catalog-seed.json, so whatever you
// just built/edited in the Strapi admin becomes reproducible on a fresh
// volume via seed.sh — the direct analog of wordpress/seed/dump.sh.
//
// Run after making content changes, then commit the updated JSON file:
//   docker compose exec strapi bash seed/dump.sh
//   git add strapi/seed/catalog-seed.json && git commit -m "..."
//
// Only published entries are captured — draft-only content is skipped,
// since seed.sh republishes everything it creates anyway (there's no
// "draft" concept in the seed file).
//
// Boots Strapi in-process the same way seed-content.js does, so it can use
// the Document Service API directly instead of going over HTTP with an
// admin token.

'use strict';

const fs = require('fs');
const path = require('path');
const { createStrapi, compileStrapi } = require('@strapi/strapi');

const SEED_FILE = path.join(__dirname, 'catalog-seed.json');

// Inverse of seed-content.js's toBlocks(). Only round-trips the simple
// "single paragraph of plain text" shape toBlocks() produces — richer
// blocks content (multiple paragraphs, bold/italic, lists, ...) authored
// later directly in the Strapi admin will be flattened into plain text
// here, losing that structure. A deliberate trade-off for keeping
// catalog-seed.json a plain, human-readable/diffable JSON file rather than
// mirroring Strapi's internal blocks format.
function fromBlocks(blocks) {
  if (!blocks || blocks.length === 0) return null;
  return blocks
    .map((block) => (block.children || []).map((child) => child.text || '').join(''))
    .join('\n\n');
}

async function dumpCertifications(app) {
  const entries = await app.documents('api::certification.certification').findMany({
    status: 'published',
  });
  return entries.map((c) => ({
    name: c.name,
    issuingBody: c.issuingBody,
    description: c.description,
  }));
}

async function dumpStandards(app) {
  const entries = await app.documents('api::standard.standard').findMany({
    status: 'published',
  });
  return entries.map((s) => ({
    name: s.name,
    organization: s.organization,
    description: s.description,
  }));
}

async function dumpProducts(app) {
  const entries = await app.documents('api::product.product').findMany({
    status: 'published',
    populate: ['certifications', 'standards'],
  });
  return entries
    .slice()
    .sort((a, b) => (a.legacyId ?? 0) - (b.legacyId ?? 0))
    .map((p) => ({
      legacyId: p.legacyId,
      name: p.name,
      sku: p.sku,
      price: p.price,
      description: fromBlocks(p.description),
      certifications: (p.certifications || []).map((c) => c.name),
      standards: (p.standards || []).map((s) => s.name),
    }));
}

async function main() {
  const appContext = await compileStrapi({ appDir: path.join(__dirname, '..') });
  const app = await createStrapi(appContext).load();

  try {
    console.log('==> Reading published certifications');
    const certifications = await dumpCertifications(app);

    console.log('==> Reading published standards');
    const standards = await dumpStandards(app);

    console.log('==> Reading published products');
    const products = await dumpProducts(app);

    const seed = { certifications, standards, products };
    fs.writeFileSync(SEED_FILE, `${JSON.stringify(seed, null, 2)}\n`);

    console.log(`==> Wrote ${SEED_FILE}`);
    console.log(
      `    ${certifications.length} certification(s), ${standards.length} standard(s), ${products.length} product(s)`
    );
  } finally {
    await app.destroy();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
