# Christopher Huang — personal website

Static site. No npm, no framework, no build dependencies beyond Python 3.

## Editing

All text lives in **`src/content.json`**. Edit that, then rebuild:

```bash
python3 build.py            # regenerate site/
python3 build.py --serve    # regenerate, then preview at http://localhost:8000
```

`build.py` rewrites every `.html` file in `site/`. Never edit the generated HTML
directly — changes there are lost on the next build. Styling is in
`src/style.css`, the gallery lightbox in `src/app.js`; both are copied into
`site/assets/` on build.

## Adding photos to a project

1. Drop images into `site/assets/img/<folder>/` (`.jpg`, `.png`, `.webp`).
2. Set that project's `"images"` field in `content.json` to `"img/<folder>"`.
3. Rebuild. Images are picked up automatically in filename order, so rename
   them in the order you want them shown (`01-cad.jpg`, `02-print.jpg`, …).

The first image in a folder becomes the project's card thumbnail.

## Adding a project or paper

Append an object to the `projects` or `research` array in `content.json`. The
`id` becomes the page URL (`site/projects/<id>.html`). A `note` field renders as
a visible TODO banner on the page — useful while a project is still missing
material, and a reminder to remove it before sharing the link.

Project fields follow the MIT MechE Communication Lab's recommended order:
outcome first (what you built and what it achieved), then motivation, your
specific role, and technical detail last.

## Deploying

The `site/` directory is the whole website. Push the repo and point GitHub Pages
at it, or drag `site/` into Netlify or Cloudflare Pages.

Use a real domain you own rather than a platform subdomain — a portfolio link on
a resume outlives the host it started on.

## Source materials

Everything that is **not** part of the website lives under `originals/`, which
is excluded from git. `site/assets/` holds only the unpacked, web-ready copies.

```
originals/
  photos/              untouched camera-roll originals, per project
                       (optimize_images.py backs up here automatically)
  source-files/        the .zip archives, .pptx decks, .docx papers,
                       the resume, and intro.txt
  slides-media/        images extracted from the two PowerPoint decks
  withheld-private/    photos deliberately kept off the website
  unrelated-work-docs/ Digital Realty / Particle Media files that were
                       sitting in this folder and have nothing to do with
                       the site — safe to move elsewhere entirely
```

- `site/assets/img/_needs-reupload/` — 10 Big Hands photos that arrived
  truncated mid-file (cut off at exactly 217,088 bytes). Re-export these from
  the original camera roll and move them into `site/assets/img/big-hands/`.
- The resume is published as a **redacted** PDF: home address and phone number
  are stripped, email kept. If you regenerate it from the `.docx`, redact again
  before committing.

## Staging pile

`originals/slides-media/` holds every image extracted from the two PowerPoint
decks (50 files). It is **not** published — it's raw material, mixed in with QR
codes, stock photos, and chart exports. Pick the good ones (CAD renders, circuit
diagrams, test-rig photos, result charts) and move them into the relevant
`site/assets/img/<project>/` folder.

There is also a headshot in `originals/slides-media/shoe-sole-slides/` worth
checking — the home page needs one at `site/assets/img/headshot.jpg`.

## Photos: resizing

Photos straight off a phone are ~1 MB each — far more than a page needs. After
dropping new images into `site/assets/img/<folder>/`, run:

```bash
python3 optimize_images.py            # process anything new
python3 optimize_images.py --force    # redo everything
```

It writes two sizes per photo and strips all metadata:

- `<name>.jpg` — long edge 1600px, used for the full view and lightbox
- `<name>.thumb.jpg` — long edge 640px, used in card and gallery grids

Untouched originals are copied to `originals/` first, so this is non-destructive
and safe to re-run. `build.py` picks up the thumbnails automatically; the
`.thumb.jpg` files are never listed as separate gallery items.

Current result: 43 photos, 43.7 MB → 16.3 MB including thumbnails. A project
page loads about 0.4 MB.

## Hero and card crops

Cards and the home hero display at a fixed shape, so letting the browser crop
them loses control of the framing. `make_heroes.py` cuts them deliberately:

```bash
python3 make_heroes.py
```

Edit the `HEROES` dict at the top of that file. Each entry is
`name -> (source photo, width:height, vertical anchor)`, where the anchor is
`0.0` to keep the top of the frame, `0.5` to centre, `1.0` to keep the bottom.
Portraits of people want a low anchor so heads are not cropped off.

Output goes to `site/assets/img/heroes/`. A project uses one via its `"hero"`
field in `content.json`; the home page picks up `assets/img/headshot.jpg`
automatically if present.

## Withheld photos

`originals/withheld-private/` holds images kept **out** of the website. Nothing in
it is deployed.

- `big-hands/IMG_7531`, `IMG_7581` — these show prosthesis recipients' names on
  printed labels. Recipients are identifiable private individuals, several of
  them minors, so their names should not go on a public page. If you want these
  shots on the site, blur the labels first and move the blurred copies back.

Apply the same check to any new Big Hands photo before publishing: look for
name labels, intake forms, addresses, and recognisable faces of recipients.

## A note on photo orientation

The source photos are all stored 2016x1512 landscape with an EXIF Orientation
tag doing the real rotation (14 need a quarter turn, 6 need a half turn, 23 are
upright). `optimize_images.py` bakes that rotation into the pixels via
`exif_transpose`, so the shipped files are correct. Beware that some tools —
`magick montage` among them — ignore the tag and will show portrait photos
sideways. Check orientation against the files in `site/assets/img/`, not against
a contact sheet.
