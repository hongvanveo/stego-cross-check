# stego-cross-check

Lab nay minh hoa co che xac thuc audio theo kieu cross-check giua hai lop:

- Lop 1: `LSB marker` de mang message va hash.
- Lop 2: `DWT-style watermark` de mang dau vet robust cua `hash(message)`.

Audio chi duoc xem la hop le neu ca hai lop cung khop.

Tap trung cua lab:

- Nhung dong thoi hai lop marker vao `cover.wav`.
- Dung `cross_verify.py` de kiem tra tung lop rieng va tong hop ket qua.
- Minh hoa 3 tinh huong: `VALID`, `POSSIBLY MODIFIED`, `INVALID OR DESTROYED`.

Luong thuc hanh:

```bash
cd ~/stego
python3 cross_embed.py cover.wav marked_cross.wav --message "cross check demo" --key 13579
python3 cross_verify.py marked_cross.wav --key 13579
python3 attack.py marked_cross.wav light_modified.wav --type crop --level light
python3 cross_verify.py light_modified.wav --key 13579
python3 attack.py marked_cross.wav destroyed.wav --type replace --level heavy
python3 cross_verify.py destroyed.wav --key 13579
```
