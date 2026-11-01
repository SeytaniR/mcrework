import struct, zlib, os
from PIL import Image
import io

def extract_jpeg3_tags(swf_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(swf_path, "rb") as f:
        data = f.read()

    sig = data[:3]
    ver = data[3]
    length = struct.unpack("<I", data[4:8])[0]
    decomp = zlib.decompress(data[8:]) if sig == b"CWS" else data[8:]
    full = b"FWS\t" + data[4:8] + decomp

    pos = 8
    nbits = full[pos] >> 3
    pos += (5 + nbits * 4 + 7) // 8 + 4

    extracted = []
    shapes = {} # char_id -> matrix / bounds

    while pos < len(full):
        hdr = int.from_bytes(full[pos:pos+2], "little")
        t_type = hdr >> 6
        t_len = hdr & 0x3F
        pos += 2
        if t_len == 0x3F:
            t_len = int.from_bytes(full[pos:pos+4], "little")
            pos += 4

        tag_bytes = full[pos:pos+t_len]

        if t_type == 35: # DefineBitsJPEG3
            char_id = int.from_bytes(tag_bytes[:2], "little")
            alpha_offset = int.from_bytes(tag_bytes[2:6], "little")
            jpeg_data = tag_bytes[6:6+alpha_offset]
            alpha_comp = tag_bytes[6+alpha_offset:]
            try:
                # Decompress alpha mask
                alpha_data = zlib.decompress(alpha_comp)
                # Open JPEG image
                img = Image.open(io.BytesIO(jpeg_data)).convert("RGBA")
                # Apply alpha mask
                if len(alpha_data) == img.width * img.height:
                    img.putalpha(Image.frombytes("L", (img.width, img.height), alpha_data))
                out_path = os.path.join(out_dir, f"bitmap_{char_id}.png")
                img.save(out_path)
                extracted.append((char_id, img.width, img.height, out_path))
            except Exception as e:
                print(f"Error on char {char_id}: {e}")

        pos += t_len

    print(f"Extracted {len(extracted)} PNGs with alpha to {out_dir}")
    return extracted

out_char_dir = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\extracted_char"
swf_file = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\b68e68f7e6ed33ca378b507e60664d2b"
extract_jpeg3_tags(swf_file, out_char_dir)
