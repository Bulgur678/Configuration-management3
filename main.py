import yaml
import argparse
import sys


def mask(n):
    return (1 << n) - 1


def asm_load(B):
    A = 1
    cmd = A | ((B & mask(30)) << 3)
    return cmd.to_bytes(5, "little")


def asm_read(B):
    A = 2
    cmd = A | ((B & mask(20)) << 3)
    return cmd.to_bytes(3, "little")


def asm_write(B):
    A = 7
    cmd = A | ((B & mask(20)) << 3)
    return cmd.to_bytes(3, "little")


def asm_shift_right(B):
    A = 5
    cmd = A | ((B & mask(20)) << 3)
    return cmd.to_bytes(3, "little")


def assemble(program):
    result = bytearray()
    for instruction in program:
        op = instruction["op"]
        arg = instruction["arg"]

        if op == "load":
            result.extend(asm_load(arg))
        elif op == "read":
            result.extend(asm_read(arg))
        elif op == "write":
            result.extend(asm_write(arg))
        elif op == "shift_right":
            result.extend(asm_shift_right(arg))
        else:
            print(f"Error: Unknown operation: {op}")
            sys.exit(1)
    return bytes(result)



def main():
    parser = argparse.ArgumentParser(description="Assembler for UVM (variant 13)")
    parser.add_argument("-i", "--input", required=True, help="Input YAML file")
    parser.add_argument("-o", "--output", required=True, help="Output binary file")
    parser.add_argument("-t", "--test", action="store_true", help="Enable test mode")

    args = parser.parse_args()


    with open(args.input, 'r') as f:
        data = yaml.safe_load(f)

    program = data.get("program", [])
    binary = assemble(program)


    if args.test:


        print("\nTest:")
        for instruction in program:
            op = instruction["op"]
            arg = instruction["arg"]
            if op == "load":
                cmd_bytes = asm_load(arg)
                expected = [0xB1, 0x02, 0x00, 0x00, 0x00]
                assert bytes(expected) == cmd_bytes, f"load failed: {expected} != {list(cmd_bytes)}"

            elif op == "read":
                cmd_bytes = asm_read(arg)
                expected = [0x32, 0x19, 0x00]
                assert bytes(expected) == cmd_bytes, f"read failed: {expected} != {list(cmd_bytes)}"

            elif op == "write":
                cmd_bytes = asm_write(arg)
                expected = [0xA7, 0x07, 0x00]
                assert bytes(expected) == cmd_bytes, f"write failed: {expected} != {list(cmd_bytes)}"

            elif op == "shift_right":
                cmd_bytes = asm_shift_right(arg)
                expected = [0x7D, 0x14, 0x00]
                assert bytes(expected) == cmd_bytes, f"shift_right failed: {expected} != {list(cmd_bytes)}"

            hex_bytes = ", ".join([f"0x{b:02X}" for b in cmd_bytes])
            print(f"{op} {arg}: [{hex_bytes}]")

    with open(args.output, 'wb') as f:
        f.write(binary)

    print(f"\nBinary written to {args.output} ({len(binary)} bytes)")


if __name__ == "__main__":
    main()