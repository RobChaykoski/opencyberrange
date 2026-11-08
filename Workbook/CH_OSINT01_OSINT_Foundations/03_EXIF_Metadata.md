# Exercise 1.3: EXIF Metadata Investigation

## Before You Begin

- [ ] Launched the exercise and opened the lab browser or a terminal
- [ ] You can reach `http://archive.lab/`
- [ ] You have a shell with `curl` and either `exiftool`, `exiv2`, or `grep -a`

!!! note "Bonus exercise"
    This is an optional Level 1 bonus exercise. It teaches the metadata workflow
    without changing the Level 1 certificate requirement, so students who
    already earned the certificate keep it.

## Scenario

FinanceCorp published an incident update with a photo from the loading bay.
The image looks harmless, but it was exported from the physical security
archive without stripping metadata. The company wants to know what the file
reveals before the update stays online.

Your task is to recover the capture details, the GPS coordinates, and the
internal note that was never meant to leave the archive.

!!! note "Safe target"
    The image is simulated. It contains no real person, location, or
    credential. The GPS coordinates point at a fictional loading bay.

## Your Objectives

- Download the published image without re-encoding it
- Read EXIF, GPS, and device metadata from the original file
- Explain how metadata can expose location and internal context
- Capture the flag

## Background: What EXIF Carries

EXIF (Exchangeable Image File Format) is a metadata standard written by cameras
and phones. It travels with the pixels unless the publisher removes it. Common
fields include:

| Group | Examples | Why it matters |
|---|---|---|
| Camera | `Make`, `Model`, `LensModel`, `SerialNumber` | Identifies the device and sometimes the owner |
| Time | `DateTimeOriginal`, `CreateDate` | Places the image at a specific moment |
| Location | `GPSLatitude`, `GPSLongitude`, `GPSAltitude` | Can pinpoint a home, office, or job site |
| Author | `Artist`, `Copyright`, `OwnerName` | Exposes people and organisations |
| Free text | `ImageDescription`, `UserComment` | Often carries internal notes or workflow metadata |
| Software | `Software`, `ProcessingSoftware` | Reveals the editing and export pipeline |

Metadata is not visible in the rendered image. A viewer that only draws pixels
will not show it. That is why an image can look safe and still leak the camera
location and an internal comment.

## Walkthrough

### Step 1: Download the original image

Open the archive in the lab browser, or download the file directly:

!!! kali "Kali - Download the evidence image"
    ```bash
    curl -s http://archive.lab/evidence.jpg -o evidence.jpg
    file evidence.jpg
    ```

Expected output:

```
evidence.jpg: JPEG image data, Exif standard: [TIFF image data, ...]
```

Do not open and re-save the image in a photo editor before analysis. Some
editors rewrite or drop the metadata.

### Step 2: Read the metadata

!!! kali "Kali - Show every metadata group"
    ```bash
    exiftool evidence.jpg
    ```

`exiftool` prints a readable summary. Use the grouped form when you need the
raw tag names or want to see every duplicate field:

```bash
exiftool -a -G1 -s evidence.jpg
```

Look for these fields:

```
Make                : Canon
Model               : EOS R6
DateTimeOriginal    : 2026:10:24 14:32:11
ImageDescription    : Loading bay camera 3, frame 0042...
UserComment         : OCR{ex1f_m3tadata_l34ks}
GPSLatitude         : 42 deg 18' 53.00" N
GPSLongitude        : 83 deg 2' 11.00" W
```

If `exiftool` is not installed, use `exiv2` or search the raw file:

```bash
exiv2 -pa evidence.jpg
grep -a -E 'OCR|Canon|GPS|2026:10:24' evidence.jpg
```

### Step 3: Convert the GPS coordinates

!!! kali "Kali - Print decimal coordinates"
    ```bash
    exiftool -c "%.6f" -GPSLatitude -GPSLongitude evidence.jpg
    ```

The values resolve to the loading bay area in Windsor, Ontario. Publishing the
original file leaks the camera location even though the visible image is
innocuous.

!!! tip "Why the format matters"
    Camera GPS is stored as degrees, minutes, and seconds. Decimal degrees are
    easier to paste into a map. `exiftool -c "%.6f"` does the conversion for
    you.

### Step 4: Recover and submit the flag

The flag is the value in `UserComment`:

```
OCR{ex1f_m3tadata_l34ks}
```

Paste it into the **Submit Flag** form on the platform and submit.

## What Just Happened?

The visible pixels and the metadata are separate layers in the same file.
FinanceCorp removed neither before publishing. The metadata revealed:

- the camera make and model;
- the exact capture time;
- the camera's GPS position;
- an internal description that named the camera and frame.

An attacker can combine these fields with other public sources to identify a
building, a shift pattern, or a device. The same data can also break an
anonymised photo by linking it back to a person or location.

## Analysis Questions

1. Which metadata field is the most sensitive in this image, and why?
2. How would the risk change if the image had been captured on a personal phone
   instead of a fixed dock camera?
3. Why is `DateTimeOriginal` useful when correlating an image with other
   evidence?
4. What is the difference between deleting metadata and re-encoding the image?
5. Which publishing workflow would have prevented this leak?

## Defensive Takeaways

- Strip metadata before publishing images outside a controlled archive:

  ```bash
  exiftool -all= -overwrite_original evidence.jpg
  ```

- Re-check the file after stripping:

  ```bash
  exiftool evidence.jpg
  ```

- Keep the original evidence copy in a controlled archive and publish a
  sanitised derivative.
- Treat GPS, device serial numbers, author names, and free-text comments as
  sensitive.
- Add a metadata-stripping step to the publishing workflow and verify it in a
  pre-publication checklist or CI job.
- Train staff that "the image looks fine" is not a metadata review.

## If You Get Stuck

1. Confirm you downloaded the file with `curl`, not a browser or chat client
   that may re-encode it.
2. Run `exiftool -a -G1 -s evidence.jpg` to show every group and raw tag name.
3. Search the raw file if `exiftool` is unavailable:

   ```bash
   grep -a -o 'OCR{[^}]*}' evidence.jpg
   grep -a -E 'Canon|GPS|2026:10:24' evidence.jpg
   ```

4. The flag is in `UserComment`, not in the visible pixels.
5. If the file has no metadata, you probably downloaded a re-saved copy. Delete
   it and download the original again with `curl`.

## Further Reading

- [ExifTool tag names](https://exiftool.org/TagNames/)
- [CIPA DC-008 EXIF standard](https://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf)
- [OWASP Mobile Top 10: Insecure data storage](https://owasp.org/www-project-mobile-top-10/)
- [NIST SP 800-86: Guide to Integrating Forensic Techniques into Incident Response](https://csrc.nist.gov/pubs/sp/800/86/final)
