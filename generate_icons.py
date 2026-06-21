"""Generate placeholder icons for the browser extension."""
import os
import struct
import zlib

def create_png(width, height, color_rgb=(245, 166, 35)):
    """Create a simple PNG icon with the given color."""
    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    # Create raw pixel data
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # filter byte
        for x in range(width):
            # Simple circle with YT colors
            cx, cy = width // 2, height // 2
            r = min(width, height) // 2 - 1
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy <= r * r:
                # Inside circle - use red for YT
                raw_data += bytes([239, 68, 68, 255])
            else:
                raw_data += bytes([0, 0, 0, 0])

    # PNG signature
    signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr = chunk(b'IHDR', ihdr_data)

    # IDAT chunk
    compressed = zlib.compress(raw_data)
    idat = chunk(b'IDAT', compressed)

    # IEND chunk
    iend = chunk(b'IEND', b'')

    return signature + ihdr + idat + iend


def main():
    icons_dir = os.path.join(os.path.dirname(__file__), 'browser_extension', 'icons')
    os.makedirs(icons_dir, exist_ok=True)

    for size in [16, 48, 128]:
        png_data = create_png(size, size)
        filepath = os.path.join(icons_dir, f'icon{size}.png')
        with open(filepath, 'wb') as f:
            f.write(png_data)
        print(f"Created {filepath}")


if __name__ == '__main__':
    main()
