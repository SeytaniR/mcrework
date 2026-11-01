"""
Extração de Malha de Colisão de Mapas (Hit.swf -> collision.bin & collision_overlay.png)
Magic Campus Modern Rework
"""

import os, sys, zlib, struct, argparse
from PIL import Image

def extract_hit_swf(swf_path, out_bin, out_overlay_png=None, width=2031, height=1531):
    print(f"Lendo {swf_path}...")
    with open(swf_path, "rb") as f:
        data = f.read()

    decomp = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]
    full = b"FWS\t" + data[4:8] + decomp

    pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)

    raw_collision = None
    while pos < len(full):
        hdr = int.from_bytes(full[pos:pos+2], "little")
        t_type = hdr >> 6
        t_len = hdr & 0x3F
        pos += 2
        if t_len == 0x3F:
            t_len = int.from_bytes(full[pos:pos+4], "little")
            pos += 4

        tag_data = full[pos:pos+t_len]
        if t_type == 87: # DefineBinaryData
            # Bytes 6 em diante contêm o payload zlib
            payload = tag_data[6:]
            try:
                raw_collision = zlib.decompress(payload)
                print(f"Encontrada e descompactada malha de colisão: {len(raw_collision)} bytes.")
            except:
                raw_collision = payload
        pos += t_len

    if not raw_collision:
        print("Erro: Nenhuma malha binária encontrada no SWF.")
        return

    os.makedirs(os.path.dirname(out_bin), exist_ok=True)
    with open(out_bin, "wb") as f:
        f.write(raw_collision)
    print(f"Salvo arquivo de colisão binário: {out_bin} ({len(raw_collision)} bytes)")

    if out_overlay_png:
        print(f"Gerando overlay visual PNG ({width}x{height})...")
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        pix = overlay.load()
        for y in range(height):
            y_off = y * width
            for x in range(width):
                idx = y_off + x
                byte_idx = idx // 8
                bit_idx = idx % 8
                # 0 = Bloqueado (Obstáculo vermelho translúcido)
                if not (raw_collision[byte_idx] & (1 << bit_idx)):
                    pix[x, y] = (255, 30, 30, 140)
        overlay.save(out_overlay_png)
        print(f"Overlay de colisão salvo em: {out_overlay_png}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrai malha de colisão do Hit.swf para binário e overlay")
    parser.add_argument("--swf", required=True, help="Caminho do arquivo Hit.swf")
    parser.add_argument("--bin", required=True, help="Caminho de saída do collision.bin")
    parser.add_argument("--overlay", help="Caminho opcional para salvar o collision_overlay.png")
    parser.add_argument("--w", type=int, default=2031, help="Largura da malha de colisão")
    parser.add_argument("--h", type=int, default=1531, help="Altura da malha de colisão")
    args = parser.parse_args()
    extract_hit_swf(args.swf, args.bin, args.overlay, args.w, args.h)
