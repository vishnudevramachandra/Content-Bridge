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
} );
