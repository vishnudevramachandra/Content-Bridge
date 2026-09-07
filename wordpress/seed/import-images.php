<?php
/**
 * Imports the bundled seed images (wp-content/seed/images/) and sets each
 * as its post/page's featured image, driven by images-manifest.json.
 *
 * This is what actually populates `_links.wp:featuredmedia` on the REST
 * API — WordPress only emits that relation when a real attachment exists,
 * it's never present just because a post *could* have one.
 *
 * Run via: wp eval-file wp-content/seed/import-images.php
 * Called automatically from seed.sh, after the content-dump.sql restore
 * (posts must already exist with their real IDs/slugs before this runs).
 *
 * Idempotent: skips any post that already has a featured image, so a
 * manual re-run (or re-running seed.sh against an already-seeded site)
 * is a safe no-op — same idempotency shape as the rest of seed.sh.
 */

$manifest_path = __DIR__ . '/images-manifest.json';
$images_dir    = __DIR__ . '/images';

$manifest = json_decode( file_get_contents( $manifest_path ), true );
if ( ! is_array( $manifest ) ) {
	WP_CLI::error( "Could not parse $manifest_path" );
}

$imported = 0;
$skipped  = 0;

foreach ( $manifest as $entry ) {
	// Matched by slug alone (not get_page_by_path), because several of
	// these pages are hierarchical children (e.g. the Veridian pages
	// live under Products) and get_page_by_path requires the full
	// parent/child path rather than just the slug.
	$matches = get_posts(
		array(
			'name'        => $entry['slug'],
			'post_type'   => array( 'post', 'page' ),
			'post_status' => 'any',
			'numberposts' => 1,
		)
	);
	$post = $matches ? $matches[0] : null;
	if ( ! $post ) {
		WP_CLI::warning( "No post/page found for slug '{$entry['slug']}' — skipping." );
		continue;
	}

	if ( get_post_thumbnail_id( $post->ID ) ) {
		$skipped++;
		continue;
	}

	$file_path = $images_dir . '/' . $entry['file'];
	if ( ! file_exists( $file_path ) ) {
		WP_CLI::warning( "Image file not found: $file_path — skipping." );
		continue;
	}

	WP_CLI::run_command(
		array( 'media', 'import', $file_path ),
		array(
			'post_id'        => $post->ID,
			'title'          => $entry['title'],
			'alt'            => $entry['alt'],
			'featured_image' => true,
		)
	);
	$imported++;
}

WP_CLI::log( "Imported $imported featured image(s), skipped $skipped (already set)." );
