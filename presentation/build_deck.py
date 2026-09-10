"""Builds the ContentBridge review deck, one function per slide.

Run this whenever a slide is added/changed:
    python3 build_deck.py

Slides are added incrementally (per the review session) — only the ones
implemented below actually appear in the output. Each add_slide_N function
is self-contained and only depends on theme.py, so slides can be reordered
or regenerated independently.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

import theme

OUTPUT_PATH = "ContentBridge_Review.pptx"


def add_slide_1_title(prs):
    """Slide 1: Title + team."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout
    theme.set_background(slide)

    # Title — vertically centered on the slide; no subtitle (the "without
    # migration" framing and the WordPress/Strapi specifics are introduced
    # on later slides, not here).
    title_box = slide.shapes.add_textbox(Inches(1.0), Inches(3.3), Inches(11.33), Inches(1.1))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Bridging CMS Silos"
    run.font.size = Pt(44)
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.TEXT_DARK

    # Thin accent rule between title and team line, purely decorative,
    # keeps the minimalist look instead of a hard divider.
    line = slide.shapes.add_shape(1, Inches(5.67), Inches(4.55), Inches(2.0), Pt(2))
    line.fill.solid()
    line.fill.fore_color.rgb = theme.ACCENT
    line.line.fill.background()

    # Team / presenter line at the bottom.
    team_box = slide.shapes.add_textbox(Inches(1.0), Inches(4.8), Inches(11.33), Inches(0.6))
    tf = team_box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Ayoub  \u00b7  Mohammed  \u00b7  Vishnudev"
    run.font.size = Pt(16)
    run.font.name = theme.FONT
    run.font.color.rgb = theme.MUTED


def add_slide_2_intro(prs):
    """Slide 2: the multi-CMS reality stat, the pain, and the framing
    question — deliberately no WordPress/Strapi specifics yet (slide 3)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    theme.set_background(slide)

    theme.add_slide_title(slide, "The Multi-CMS Reality")

    # Big stat, left column — the single number the audience should
    # remember from this slide.
    stat_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.9), Inches(4.6), Inches(2.0))
    tf = stat_box.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "61%"
    run.font.size = Pt(96)
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT

    caption_box = slide.shapes.add_textbox(Inches(0.75), Inches(3.75), Inches(4.5), Inches(1.0))
    tf = caption_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "of organizations run content across multiple CMS platforms"
    run.font.size = Pt(16)
    run.font.name = theme.FONT
    run.font.color.rgb = theme.MUTED

    # Right column — the pain, in plain language.
    pain_box = slide.shapes.add_textbox(Inches(6.0), Inches(1.9), Inches(6.6), Inches(2.6))
    tf = pain_box.text_frame
    tf.word_wrap = True
    lines = [
        "Keeping them connected today means manual, repetitive work.",
        "It doesn't scale, and it doesn't get cheaper with more content.",
    ]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(14)
        run = p.add_run()
        run.text = line
        run.font.size = Pt(20)
        run.font.name = theme.FONT
        run.font.color.rgb = theme.TEXT_DARK

    # Framing question, set apart at the bottom as the slide's takeaway.
    question_box = slide.shapes.add_textbox(Inches(0.7), Inches(5.6), Inches(11.9), Inches(1.0))
    tf = question_box.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "If full migration isn't the answer \u2014 what is?"
    run.font.size = Pt(26)
    run.font.italic = True
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT


def add_slide_3_problem(prs):
    """Slide 3: crystallize the problem — one concrete case. WordPress
    (posts/pages) on one side, Strapi (tables + their own relations) on the
    other, with no shared schema connecting them."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    theme.set_background(slide)

    theme.add_slide_title(slide, "A Concrete Case")

    # --- Left panel: WordPress -------------------------------------
    label_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.75), Inches(4.6), Inches(0.5))
    p = label_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "WordPress"
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT

    # Real seed content, pulled live from each system so nothing here is
    # invented: two WordPress posts and two pages, each as its own card
    # rather than grouped into a "Posts"/"Pages" list.
    theme.add_content_card(
        slide, Inches(0.6), Inches(2.1), Inches(2.55), Inches(1.75),
        "Post", "Burn it with BX54",
        "The newly developed engraver BX54 uses the most powerful laser\u2026",
    )
    theme.add_content_card(
        slide, Inches(3.35), Inches(2.1), Inches(2.55), Inches(1.75),
        "Post", "Reordering the BX54 Focus Lens",
        "When reordering the replacement lens for your BX54 engraver\u2026",
    )
    theme.add_content_card(
        slide, Inches(0.6), Inches(4.0), Inches(2.55), Inches(1.75),
        "Page", "Veridian Safety Light Curtains",
        "Veridian Automation Type 4 safety light curtains for\u2026",
    )
    theme.add_content_card(
        slide, Inches(3.35), Inches(4.0), Inches(2.55), Inches(1.75),
        "Page", "Veridian Emergency Stop Devices",
        "Veridian Automation emergency stop pushbuttons and\u2026",
    )

    note_box = slide.shapes.add_textbox(Inches(0.6), Inches(5.9), Inches(5.3), Inches(0.6))
    tf = note_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Some posts carry extra custom fields \u2014 free-form, not part of the base schema."
    run.font.size = Pt(13)
    run.font.italic = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.MUTED

    # --- Middle: no shared schema divider ---------------------------
    theme.add_connector(slide, Inches(6.35), Inches(1.9), Inches(6.35), Inches(6.0), dashed=True)
    gap_box = slide.shapes.add_textbox(Inches(5.55), Inches(3.75), Inches(1.6), Inches(0.9))
    tf = gap_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "No shared\nschema"
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.MUTED

    # --- Right panel: Strapi (its own internal relations) -----------
    label_box = slide.shapes.add_textbox(Inches(7.4), Inches(1.75), Inches(5.3), Inches(0.5))
    p = label_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Strapi"
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT

    theme.add_mini_table(
        slide, Inches(7.4), Inches(2.15), Inches(5.3), Inches(1.0),
        headers=["Product", "SKU"],
        rows=[
            ["Aurora BX54 Fiber Laser Engraver", "SIS-BX54-ENGR"],
            ["BX54 Replacement Focus Lens", "SIS-BX54-LENS"],
        ],
        col_widths=[0.62, 0.38],
    )
    theme.add_mini_table(
        slide, Inches(7.4), Inches(3.35), Inches(5.3), Inches(0.75),
        headers=["Standard", "Organization"],
        rows=[["IEC 61496-2", "IEC"]],
        col_widths=[0.62, 0.38],
    )
    theme.add_mini_table(
        slide, Inches(7.4), Inches(4.3), Inches(5.3), Inches(0.75),
        headers=["Certification", "Issuing Body"],
        rows=[["UL Listed", "Underwriters Laboratories"]],
        col_widths=[0.45, 0.55],
    )

    rel_box = slide.shapes.add_textbox(Inches(7.4), Inches(5.3), Inches(5.3), Inches(0.9))
    tf = rel_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Many-to-many relations \u2014 already structured, on its own side."
    run.font.size = Pt(13)
    run.font.italic = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.MUTED


def add_slide_4_slug_example(prs):
    """Slide 4: the concrete field-to-column example. `related_product_ids`
    is shown under the pseudonym "slug" (per the anonymity request) next
    to the real Strapi Product table it should resolve against. Arrow is
    static \u2014 the presenter adds a PowerPoint entrance animation on it."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    theme.set_background(slide)

    theme.add_slide_title(slide, "Mapping a Field to Its Match")

    # --- Left: the WordPress post and its custom field --------------
    label_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.75), Inches(4.3), Inches(0.5))
    p = label_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "WordPress"
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT

    theme.add_content_card(
        slide, Inches(0.7), Inches(2.3), Inches(4.3), Inches(1.3),
        "Post", "Burn it with BX54",
        "The newly developed engraver BX54 uses the most powerful laser\u2026",
    )
    theme.add_field_tag(slide, Inches(0.7), Inches(3.75), Inches(4.3), Inches(1.15),
                         "custom field \u2014 slug", "104, 891, 233")

    # --- Middle: arrow toward the matching Strapi column ------------
    arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(5.25), Inches(4.0),
                                    Inches(2.35), Inches(0.7))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = theme.ACCENT
    arrow.line.fill.background()
    arrow.shadow.inherit = False

    # --- Right: the real Strapi Product table, match highlighted ----
    label_box = slide.shapes.add_textbox(Inches(7.95), Inches(1.75), Inches(4.7), Inches(0.5))
    p = label_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Strapi \u2014 Product"
    run.font.size = Pt(16)
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT

    theme.add_mini_table(
        slide, Inches(7.95), Inches(2.3), Inches(4.7), Inches(2.6),
        headers=["Product", "legacyId"],
        rows=[
            ["Aurora BX54 Fiber Laser Engraver", "104"],
            ["BX54 Fume Extraction Filter Cartridge", "233"],
            ["Veridian GL100 Safety Interlock Switch", "512"],
            ["Veridian ES200 Emergency Stop Pushbutton", "618"],
            ["Veridian LC900 Type 4 Safety Light Curtain", "734"],
            ["BX54 Replacement Focus Lens", "891"],
        ],
        col_widths=[0.75, 0.25],
        highlight_rows={0, 1, 5},
    )

    # --- Bottom: the framing goal, matching slide 2's question style -
    goal_box = slide.shapes.add_textbox(Inches(0.7), Inches(6.2), Inches(11.9), Inches(0.9))
    tf = goal_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Goal: an LLM identifies which system, table, and column this value belongs to."
    run.font.size = Pt(20)
    run.font.italic = True
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT


def add_slide_5_end_product(prs):
    """Slide 5: the end product. A small pictorial diagram (post \u2192 Strapi
    entity, solid for resolved / dashed for escalated) sits above the
    mapping table itself, so the audience sees both the concrete
    connection and the persisted record of it. The `slug` pseudonym from
    slide 4 is kept for continuity, and the table intentionally avoids
    the real, differently-named `slug` custom field so the two don't
    collide on the same slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    theme.set_background(slide)

    theme.add_slide_title(slide, "The End Product: A Mapping Table")

    # --- Pictorial diagram: how a post actually relates to Strapi ---
    label_l = slide.shapes.add_textbox(Inches(0.9), Inches(1.48), Inches(3.0), Inches(0.4))
    p = label_l.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "WordPress"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT

    label_r = slide.shapes.add_textbox(Inches(8.9), Inches(1.48), Inches(3.5), Inches(0.4))
    p = label_r.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Strapi"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT

    theme.add_box(slide, Inches(0.9), Inches(2.1), Inches(3.0), Inches(0.85),
                  "Post: Burn it with BX54", font_size=12.5, bold=True)
    theme.add_box(slide, Inches(8.9), Inches(1.85), Inches(3.5), Inches(0.75),
                  "Product", font_size=13, bold=True)
    theme.add_box(slide, Inches(8.9), Inches(2.85), Inches(3.5), Inches(0.75),
                  "Standard / Certification", font_size=13, bold=True)

    # Solid = resolved (the slide 4 example), dashed = escalated (no
    # confident target yet) \u2014 same two outcomes the table rows below show.
    theme.add_connector(slide, Inches(3.9), Inches(2.53), Inches(8.9), Inches(2.23))
    theme.add_connector(slide, Inches(3.9), Inches(2.53), Inches(8.9), Inches(3.23), dashed=True)

    link_label = slide.shapes.add_textbox(Inches(4.5), Inches(1.95), Inches(3.9), Inches(0.35))
    p = link_label.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "1.0 \u2014 resolved"
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT

    link_label2 = slide.shapes.add_textbox(Inches(4.5), Inches(3.35), Inches(3.9), Inches(0.35))
    p = link_label2.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "0.3 \u2014 escalated"
    run.font.size = Pt(11)
    run.font.name = theme.FONT
    run.font.color.rgb = theme.MUTED

    # --- The persisted record of exactly those connections ----------
    theme.add_mini_table(
        slide, Inches(0.6), Inches(4.15), Inches(12.1), Inches(1.9),
        headers=["Source", "Evidence", "Target", "Confidence", "Method"],
        rows=[
            ["post.slug", "values match product.legacyId", "product.legacyId", "1.0", "Value Match"],
            ["post body mentions \u201cbx54\u201d", "2+ candidate products", "\u2014 (escalated)", "0.3", "Human Review"],
            ["post body mentions \u201csafety\u201d", "no strong candidate found", "\u2014 (no match)", "0.05", "LLM Judgment"],
        ],
        col_widths=[0.19, 0.29, 0.20, 0.12, 0.20],
        highlight_rows={0},
    )

    caption_box = slide.shapes.add_textbox(Inches(0.6), Inches(6.15), Inches(12.1), Inches(0.55))
    tf = caption_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Every row is a documented semantic connection \u2014 including honest \u201cno match\u201d decisions."
    run.font.size = Pt(16)
    run.font.italic = True
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT

    subcaption_box = slide.shapes.add_textbox(Inches(0.6), Inches(6.7), Inches(12.1), Inches(0.5))
    tf = subcaption_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "This table \u2014 not the two content systems \u2014 is the durable, reusable record of how they relate."
    run.font.size = Pt(12.5)
    run.font.name = theme.FONT
    run.font.color.rgb = theme.MUTED


def add_slide_6_compliance(prs):
    """Slide 6: the compliance use case. Unlike slides 3-5, the real seed
    data has no expiry/version field to show genuine cert staleness, so
    this one is an explicitly-labeled illustrative scenario (per the
    reviewer's own call) rather than a real-data walkthrough \u2014 it still
    reuses the same visual grammar (card, field tag, connector) so it
    reads as one more instance of the same mechanism, not a new idea."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    theme.set_background(slide)

    theme.add_slide_title(slide, "Beyond Cleanup: Catching Compliance Drift")

    note_box = slide.shapes.add_textbox(Inches(9.2), Inches(0.55), Inches(3.4), Inches(0.4))
    p = note_box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = "Illustrative scenario"
    run.font.size = Pt(11)
    run.font.italic = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.MUTED

    # --- Left: the public-facing content, as written ------------------
    theme.add_content_card(
        slide, Inches(0.7), Inches(1.7), Inches(4.6), Inches(2.3),
        kind="Blog Post",
        title="5 Reasons to Upgrade Your Machine Guarding",
        excerpt="\u201c...our light curtains are CE Marked, tested under "
                "our original 2016 certification, and UL Listed...\u201d",
    )
    theme.add_field_tag(
        slide, Inches(0.7), Inches(4.15), Inches(2.3), Inches(0.8),
        "cited certification year", "2016",
    )

    # --- Right: the current system of record --------------------------
    theme.add_card(
        slide, Inches(8.0), Inches(1.7), Inches(4.6), Inches(2.3),
        title="Strapi: CE Marked (current record)",
        lines=["Issuing body: EU (CE Marking Directive)",
               "Status: recertified 2024"],
    )
    theme.add_field_tag(
        slide, Inches(10.4), Inches(4.15), Inches(2.3), Inches(0.8),
        "system-of-record status", "2024",
    )

    # --- The mismatch itself, flagged rather than silently fixed -------
    theme.add_connector(slide, Inches(5.3), Inches(2.85), Inches(8.0), Inches(2.85),
                         dashed=True, color=theme.WARN)
    warn_label = slide.shapes.add_textbox(Inches(5.3), Inches(2.3), Inches(2.7), Inches(0.5))
    p = warn_label.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "\u26a0 2016 vs. 2024 \u2014 mismatch"
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.WARN

    caption_box = slide.shapes.add_textbox(Inches(0.6), Inches(5.55), Inches(12.1), Inches(0.55))
    tf = caption_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Flagged the moment public content and the system of record disagree."
    run.font.size = Pt(16)
    run.font.italic = True
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT

    subcaption_box = slide.shapes.add_textbox(Inches(0.6), Inches(6.1), Inches(12.1), Inches(0.5))
    tf = subcaption_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Escalated for compliance review \u2014 not auto-corrected."
    run.font.size = Pt(12.5)
    run.font.name = theme.FONT
    run.font.color.rgb = theme.MUTED


def add_slide_7_wrapup(prs):
    """Slide 7: wrap-up. Deliberately echoes slide 1's centered, minimal
    layout (same accent rule + team line) so the deck reads as a closed
    loop, with three summary lines that each tie back to one earlier
    slide (2, 4/5, 6) rather than introducing anything new."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout
    theme.set_background(slide)

    theme.add_slide_title(slide, "Summary")

    points = [
        "One mapping layer, not one migration \u2014 bridging WordPress and "
        "Strapi as they are.",
        "Deterministic where the data allows it, LLM judgment where it "
        "doesn't, a human in the loop when even that isn't enough.",
        "The same table that cleans up product references also catches "
        "compliance drift.",
    ]
    y = Inches(2.1)
    for point in points:
        box = slide.shapes.add_textbox(theme.MARGIN_X, y, Inches(11.9), Inches(0.9))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = "\u25b8 "
        run.font.size = Pt(19)
        run.font.bold = True
        run.font.name = theme.FONT
        run.font.color.rgb = theme.ACCENT
        run = p.add_run()
        run.text = point
        run.font.size = Pt(19)
        run.font.name = theme.FONT
        run.font.color.rgb = theme.TEXT_DARK
        y += Inches(0.95)

    # Bookend rule + team line, matching slide 1's closing look.
    line = slide.shapes.add_shape(1, Inches(5.67), Inches(5.65), Inches(2.0), Pt(2))
    line.fill.solid()
    line.fill.fore_color.rgb = theme.ACCENT
    line.line.fill.background()

    thanks_box = slide.shapes.add_textbox(Inches(1.0), Inches(5.85), Inches(11.33), Inches(0.5))
    tf = thanks_box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Thank you"
    run.font.size = Pt(22)
    run.font.italic = True
    run.font.bold = True
    run.font.name = theme.FONT
    run.font.color.rgb = theme.ACCENT

    team_box = slide.shapes.add_textbox(Inches(1.0), Inches(6.4), Inches(11.33), Inches(0.6))
    tf = team_box.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Ayoub  \u00b7  Mohammed  \u00b7  Vishnudev"
    run.font.size = Pt(16)
    run.font.name = theme.FONT
    run.font.color.rgb = theme.MUTED


def build():
    prs = Presentation()
    prs.slide_width = theme.SLIDE_W
    prs.slide_height = theme.SLIDE_H

    add_slide_1_title(prs)
    add_slide_2_intro(prs)
    add_slide_3_problem(prs)
    add_slide_4_slug_example(prs)
    add_slide_5_end_product(prs)
    add_slide_6_compliance(prs)
    add_slide_7_wrapup(prs)

    prs.save(OUTPUT_PATH)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
