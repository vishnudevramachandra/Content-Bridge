import { factories } from '@strapi/strapi';

// createCoreController wires up the standard find/findOne/create/update/delete
// REST handlers from the schema.json above — no CRUD to hand-write unless we
// later need custom behavior (e.g. an endpoint the Sync agent calls directly).
export default factories.createCoreController('api::product.product');
