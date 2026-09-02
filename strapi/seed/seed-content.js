// Seeds the Strapi catalog (Products, Certifications, Standards) from
// catalog-seed.json using the Document Service API.
//
// Boots Strapi fully in-process — the exact same
// `compileStrapi()` + `createStrapi(appContext).load()` sequence Strapi's
// own CLI commands use internally (e.g. `strapi admin:create-user`) — so it
// gets full access to `strapi.documents(...)` without going over HTTP or
// needing an admin session/token.
//
// Idempotent via the Core Store (`strapi.store`), the direct analog of
// WordPress's `contentbridge_seeded` wp_options flag: both live inside the
// same DB/volume as the content itself, so a fresh volume always re-seeds
// and an existing one always no-ops.
//
// Run via seed.sh, which in turn runs via the `strapi-seed` one-shot
// compose service. Safe to re-run manually too.

'use strict';

const path = require('path');
const { createStrapi, compileStrapi } = require('@strapi/strapi');

const catalogSeed = require('./catalog-seed.json');

const SEEDED_FLAG_KEY = 'contentbridge_catalog_seeded';

// Product.description is a `blocks` (rich text) attribute; Certification and
// Standard descriptions are plain `text`. Keeping the seed file itself as
// plain strings (human-readable/diffable) and doing this trivial wrap here
// keeps catalog-seed.json readable without needing to hand-author Strapi's
// internal blocks JSON shape.
function toBlocks(text) {
  if (!text) return null;
  return [{ type: 'paragraph', children: [{ type: 'text', text }] }];
}

async function seedCertifications(app) {
  console.log('==> Seeding certifications');
  const documentIdByName = {};
  for (const cert of catalogSeed.certifications) {
    const doc = await app.documents('api::certification.certification').create({
      data: {
        name: cert.name,
        issuingBody: cert.issuingBody,
        description: cert.description,
      },
    });
    await app.documents('api::certification.certification').publish({ documentId: doc.documentId });
    documentIdByName[cert.name] = doc.documentId;
  }
  return documentIdByName;
}

async function seedStandards(app) {
  console.log('==> Seeding standards');
  const documentIdByName = {};
  for (const standard of catalogSeed.standards) {
    const doc = await app.documents('api::standard.standard').create({
      data: {
        name: standard.name,
        organization: standard.organization,
        description: standard.description,
      },
    });
    await app.documents('api::standard.standard').publish({ documentId: doc.documentId });
    documentIdByName[standard.name] = doc.documentId;
  }
  return documentIdByName;
}

async function seedProducts(app, certificationIdByName, standardIdByName) {
  console.log('==> Seeding products');
  for (const product of catalogSeed.products) {
    const doc = await app.documents('api::product.product').create({
      data: {
        name: product.name,
        sku: product.sku,
        legacyId: product.legacyId,
        price: product.price,
        description: toBlocks(product.description),
        certifications: (product.certifications || []).map((name) => certificationIdByName[name]),
        standards: (product.standards || []).map((name) => standardIdByName[name]),
      },
    });
    await app.documents('api::product.product').publish({ documentId: doc.documentId });
  }
}

async function main() {
  const appContext = await compileStrapi({ appDir: path.join(__dirname, '..') });
  const app = await createStrapi(appContext).load();

  try {
    // `type: 'core'` must be passed explicitly to both calls: `store.get`
    // defaults it to 'core' internally, but `store.set` does NOT — a bare
    // `store.set({ key, value })` silently writes under a different key
    // than `store.get({ key })` reads, so the flag would never be found on
    // a later run without this. Confirmed by reading Strapi's own
    // core-store.js source (an asymmetry in Strapi itself, not obvious from
    // the outside).
    const alreadySeeded = await app.store.get({ key: SEEDED_FLAG_KEY, type: 'core' });
    if (alreadySeeded) {
      console.log(`==> ${SEEDED_FLAG_KEY} flag already set. Nothing to do.`);
      return;
    }

    const certificationIdByName = await seedCertifications(app);
    const standardIdByName = await seedStandards(app);
    await seedProducts(app, certificationIdByName, standardIdByName);

    await app.store.set({ key: SEEDED_FLAG_KEY, value: true, type: 'core' });
    console.log('==> Done.');
  } finally {
    await app.destroy();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
