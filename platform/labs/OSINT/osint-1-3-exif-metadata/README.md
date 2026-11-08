# Lab 1.3: EXIF Metadata Investigation

## Learning Objectives

- Download a published image without re-encoding it
- Read EXIF, GPS, and device metadata from the original file
- Explain how metadata can expose location and internal context
- Capture the flag

## Scenario

FinanceCorp published an incident update with a photo from the loading bay.
The image looks harmless, but it was exported from the physical security archive
without stripping metadata.

## Solution Walkthrough

### Step 1: Download the original image

```bash
curl -s http://archive.lab/evidence.jpg -o evidence.jpg
file evidence.jpg
```

Do not open and re-save the file in an image editor first. Some editors rewrite
the metadata and destroy the evidence.

### Step 2: Read the metadata

```bash
exiftool evidence.jpg
```

Or, to see every group and the raw tag names:

```bash
exiftool -a -G1 -s evidence.jpg
```

The important fields are:

| Field | Value |
|---|---|
| `Make` / `Model` | Canon / EOS R6 |
| `DateTimeOriginal` | 2026:10:24 14:32:11 |
| `GPSLatitude` | 42Â° 18' 53" N |
| `GPSLongitude` | 83Â° 2' 11" W |
| `ImageDescription` | Loading bay camera 3, frame 0042 |
| `UserComment` | `OCR{ex1f_m3tadata_l34ks}` |

If you prefer a different tool:

```bash
exiv2 -pa evidence.jpg
identify -verbose evidence.jpg | grep -i -A2 'exif'
```

### Step 3: Convert the GPS coordinates (optional)

`exiftool` can print decimal coordinates directly:

```bash
exiftool -c "%.6f" -GPSLatitude -GPSLongitude evidence.jpg
```

The coordinates resolve to the loading bay area in Windsor, Ontario. Publishing
the original file leaks the camera location even when the visible content is
innocuous.

### Step 4: Submit the flag

The flag is the value in `UserComment`:

```
OCR{ex1f_m3tadata_l34ks}
```

Paste it into the **Submit Flag** form and submit.

## What Just Happened?

EXIF is a metadata standard that cameras and phones write into image files. It
can include the device make and model, capture time, GPS position, software,
and free-text comments. The visible image and the metadata travel together
unless the publisher explicitly strips the metadata.

## Defensive Takeaways

- Strip metadata before publishing images outside a controlled archive:

  ```bash
  exiftool -all= -overwrite_original evidence.jpg
  ```

- Re-check the file after stripping:

  ```bash
  exiftool evidence.jpg
  ```

- Keep the original evidence copy in a controlled archive; publish a sanitised
  derivative.
- Treat GPS, device serial numbers, author names, and comments as sensitive.
- Add a metadata-stripping step to the publishing workflow and verify it in CI
  or a pre-publication checklist.

## If You Get Stuck

1. Confirm you downloaded the file with `curl`, not a browser that may rename
   or re-encode it.
2. Run `exiftool -a -G1 -s evidence.jpg` to show all groups and raw tag names.
3. Search the raw file if `exiftool` is unavailable:

   ```bash
   grep -a -o 'OCR{[^}]*}' evidence.jpg
   grep -a -E 'Canon|GPS|2026:10:24' evidence.jpg
   ```

4. The flag is in `UserComment`, not in the visible pixels.

## Further Reading

- [ExifTool tag names](https://exiftool.org/TagNames/)
- [CIPA DC-008 EXIF standard](https://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf)
- OWASP Mobile Top 10: Insecure data storage and privacy leaks
