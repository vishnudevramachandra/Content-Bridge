<?php
/**
 * Plugin Name: ContentBridge Fields
 * Description: Registers custom fields used by the ContentBridge Discovery/Mapping agents.
 * Version: 0.1.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_action( 'init', function () {
	register_post_meta( 'post', 'related_product_ids', [
		'type'         => 'string',
		'single'       => true,
		'show_in_rest' => true,
		// Deliberately no 'description': a bare comma-separated list of integers
		// (e.g. "104,891,233") is genuinely ambiguous from schema alone — it could
		// be WordPress post IDs, Strapi entry IDs, or arbitrary internal reference
		// numbers. Resolving it requires the Mapping Agent to cross-check the
		// actual values against both systems, not a fixed rule.
	] );

	register_post_meta( 'post', 'slug', [
		'type'         => 'string',
		'single'       => true,
		'show_in_rest' => true,
		// Deliberately no 'description', and deliberately named to collide with
		// WordPress's own core notion of "slug" (the URL-friendly post_name,
		// already exposed as a top-level `slug` field on every REST post). A
		// custom meta field *also* called "slug" holding an alphanumeric code
		// like "BX54-FL-02" is genuinely multiply-defensible from schema alone:
		// read literally it looks like a URL-style identifier; read loosely
		// ("slug" as industry shorthand for a short product code) it looks like
		// a part number. It doesn't exact-match or numerically range-match any
		// known Strapi sku/legacyId either, so it can't be resolved by a
		// deterministic rule — only a plausible fuzzy resemblance to one
		// product. A genuine judgment call, not a lookup.
	] );
} );
