#!/usr/bin/env python3
"""Generate the deterministic V13 Linux/AArch64 syscall-only probe."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


MESSAGE = b"ORION V13 container pass\n"
BASE = 0x400000
ELF_HEADER_SIZE = 64
PROGRAM_HEADER_SIZE = 56
CODE_OFFSET = ELF_HEADER_SIZE + PROGRAM_HEADER_SIZE


def movz_x(register: int, immediate: int) -> int:
    if not (0 <= register <= 31 and 0 <= immediate <= 0xFFFF):
        raise ValueError("MOVZ operand out of range")
    return 0xD2800000 | (immediate << 5) | register


def adr(register: int, delta: int) -> int:
    if not (-(1 << 20) <= delta < (1 << 20)):
        raise ValueError("ADR delta out of range")
    encoded = delta & ((1 << 21) - 1)
    immlo = encoded & 0x3
    immhi = encoded >> 2
    return 0x10000000 | (immlo << 29) | (immhi << 5) | register


def build() -> bytes:
    instruction_count = 8
    message_offset = CODE_OFFSET + 4 * instruction_count
    instructions = [
        movz_x(0, 1),  # stdout
        adr(1, message_offset - (CODE_OFFSET + 4)),
        movz_x(2, len(MESSAGE)),
        movz_x(8, 64),  # Linux/AArch64 write
        0xD4000001,  # svc #0
        movz_x(0, 0),
        movz_x(8, 93),  # Linux/AArch64 exit
        0xD4000001,
    ]
    code = b"".join(struct.pack("<I", word) for word in instructions) + MESSAGE
    file_size = CODE_OFFSET + len(code)

    ident = b"\x7fELF" + bytes([2, 1, 1, 0, 0]) + bytes(7)
    elf_header = struct.pack(
        "<16sHHIQQQIHHHHHH",
        ident,
        2,  # ET_EXEC
        183,  # EM_AARCH64
        1,
        BASE + CODE_OFFSET,
        ELF_HEADER_SIZE,
        0,
        0,
        ELF_HEADER_SIZE,
        PROGRAM_HEADER_SIZE,
        1,
        0,
        0,
        0,
    )
    program_header = struct.pack(
        "<IIQQQQQQ",
        1,  # PT_LOAD
        5,  # PF_R | PF_X
        0,
        BASE,
        BASE,
        file_size,
        file_size,
        0x1000,
    )
    binary = elf_header + program_header + code
    if len(binary) != file_size:
        raise AssertionError("ELF size construction mismatch")
    return binary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(build())
    args.output.chmod(0o755)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
