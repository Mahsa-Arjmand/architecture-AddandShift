def add_and_shift_unsigned(A, B, bits):
    steps = []
    A_bin = complement(A, bits)
    B_bin = complement(B, bits)
    M = int(A_bin, 2)
    Q = int(B_bin, 2)

    product = 0
    for i in range(bits):
        if Q & 1:
            product += M
            steps.append(f"[Step {i + 1}, +]  M={product:0{bits * 2}b}  Q={Q:0{bits}b}")
        Q >>= 1
        steps.append(f"[Step {i + 1}, >]  M={product:0{bits * 2}b}  Q={Q:0{bits}b}")
        M <<= 1

    return steps, product
def add_and_shift_signed(A, B, bits):
    steps = []
    sign = 1
    if (A < 0) != (B < 0):
        sign = -1

    M = abs(A)
    Q = abs(B)
    product = 0

    for i in range(bits):
        if Q & 1:
            product += M << i
            steps.append(f"[Step {i + 1}, +]  M={product:0{bits * 2}b}  Q={Q:0{bits}b}")
        Q >>= 1
        steps.append(f"[Step {i + 1}, >]  M={product:0{bits * 2}b}  Q={Q:0{bits}b}")

    product *= sign
    return steps, product

def complement(num, bits):
    if num < 0:
        num = (1 << bits) + num
    return f"{num:0{bits}b}"
def booth_multiply_unsigned(A, B, bit_length):
    Q = B
    M = A
    result = 0
    steps = []

    for i in range(bit_length):
        if Q & 1:
            result += M << i
            steps.append(f"[Step {i + 1}, +]  M={result:0{bit_length * 2}b}  Q={Q:0{bit_length}b}")
        Q >>= 1
        steps.append(f"[Step {i + 1}, >]  M={result:0{bit_length * 2}b}  Q={Q:0{bit_length}b}")

    steps.append(f"[Final]  M=AxB={result:0{bit_length * 2}b}")
    return steps, result


def booth_multiply_signed(A, B, bit_length):
    def to_binary(n, bits):
        """Return the 2's complement binary representation of integer n with given bits."""
        if n < 0:
            n = (1 << bits) + n
        return n

    def to_signed(n, bits):
        """Convert an unsigned integer n to a signed integer with given bits."""
        if n >= (1 << (bits - 1)):
            n -= (1 << bits)
        return n

    A = to_binary(A, bit_length)
    B = to_binary(B, bit_length)

    Q = B
    M = A
    Q_minus_1 = 0
    ACC = 0
    steps = []

    full_length = bit_length + 1  # Includes Q-1

    for i in range(bit_length):
        last_bit_Q = Q & 1
        if last_bit_Q == 1 and Q_minus_1 == 0:
            ACC = (ACC - M) & ((1 << bit_length) - 1)  # Subtract M and keep within bit length
            steps.append(f"[Step {i + 1}, -]  M={((ACC << bit_length) | Q):0{full_length * 2}b}")
        elif last_bit_Q == 0 and Q_minus_1 == 1:
            ACC = (ACC + M) & ((1 << bit_length) - 1)  # Add M and keep within bit length
            steps.append(f"[Step {i + 1}, +]  M={((ACC << bit_length) | Q):0{full_length * 2}b}")
        Q_minus_1 = last_bit_Q

        # Arithmetic right shift
        combined = (ACC << (bit_length + 1)) | (Q << 1) | Q_minus_1
        sign_bit = combined & (1 << (bit_length * 2))
        combined = (combined >> 1) | sign_bit
        Q_minus_1 = combined & 1
        Q = (combined >> 1) & ((1 << bit_length) - 1)
        ACC = (combined >> (bit_length + 1)) & ((1 << bit_length) - 1)
        steps.append(f"[Step {i + 1}, >]  M={((ACC << bit_length) | Q):0{full_length * 2}b}")

    final_result = (ACC << bit_length) | Q
    final_result = to_signed(final_result, bit_length * 2)
    steps.append(f"[Final]  M=AxB={final_result:0{bit_length * 2}b}")
    return steps, final_result

def main():
    with open("in.txt", "r") as f:
        n = int(f.readline().strip())
        with open("booth.txt", "w") as out_booth, open("out.txt", "w") as out_add_shift:
            for i in range(n):
                algo_type = int(f.readline().strip())
                bits = int(f.readline().strip())
                is_signed = int(f.readline().strip())
                A = int(f.readline().strip())
                B = int(f.readline().strip())

                if algo_type == 0:
                    if is_signed:
                        steps, product = add_and_shift_signed(A, B, bits)
                    else:
                        steps, product = add_and_shift_unsigned(A, B, bits)
                else:
                    if is_signed:
                        steps, product = booth_multiply_signed(A, B, bits)
                    else:
                        steps, product = booth_multiply_unsigned(A, B, bits)

                out_booth.write(f"------------------------------------------\nout-{i}\n")
                out_add_shift.write(f"------------------------------------------\nout-{i}\n")

                if is_signed:
                    out_booth.write("signed ")
                    out_add_shift.write("signed ")
                else:
                    out_booth.write("unsigned ")
                    out_add_shift.write("unsigned ")

                if algo_type == 0:
                    out_add_shift.write("add & shift multiplication\n")
                    out_booth.write("booth multiplication\n")
                else:
                    out_add_shift.write("booth multiplication\n")
                    out_booth.write("booth multiplication\n")

                out_booth.write(f"A={A}={complement(A, bits)}, B={B}={complement(B, bits)}\n")
                out_add_shift.write(f"A={A}={complement(A, bits)}, B={B}={complement(B, bits)}\n")

                for step in steps:
                    out_booth.write(f"{step}\n")
                    out_add_shift.write(f"{step}\n")

                out_booth.write(f"~~~~~~~~~~~~~~~~~~~~\nM=AxB={product}\n")
                out_add_shift.write(f"~~~~~~~~~~~~~~~~~~~~\nM=AxB={product}\n")

                if is_signed:
                    out_booth.write("Signed Booth Result: {}\n".format(product))
                    out_add_shift.write("Signed Booth Result: {}\n".format(product))
                else:
                    out_booth.write("Unsigned Booth Result: {}\n".format(product))
                    out_add_shift.write("Unsigned Booth Result: {}\n".format(product))

if __name__ == "__main__":
    main()